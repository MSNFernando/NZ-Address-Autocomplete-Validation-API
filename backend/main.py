from fastapi import FastAPI, Request, HTTPException, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import uvicorn
import os
import time
import stripe
import secrets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
redis = Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)

# PostgreSQL async connection setup
DATABASE_URL = os.getenv("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Plan-based rate limits
PLAN_LIMITS = {
    "free": 100,
    "pro_monthly": 1000000,
    "pro_annual": 1000000
}

# Rate limiting middleware with plan logic
async def rate_limit(request: Request):
    api_key = request.headers.get("Authorization")
    if not api_key or not api_key.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")

    key = api_key.split("Bearer ")[-1].strip()
    redis_key = f"ratelimit:{key}:{time.strftime('%Y%m%d')}"

    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT plan, is_active FROM api_keys WHERE key = :key"), {"key": key})
        row = result.first()
        if not row:
            raise HTTPException(status_code=403, detail="API key not found")
        plan, is_active = row
        if not is_active:
            raise HTTPException(status_code=403, detail="API key is inactive")

    limit = PLAN_LIMITS.get(plan, 100)
    count = redis.incr(redis_key)
    if count == 1:
        redis.expire(redis_key, 86400)  # 1 day TTL

    if count > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

# List all API keys for a user
@app.get("/api/keys")
async def list_api_keys(email: str = Body(..., embed=True)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("""
            SELECT k.key, k.plan, k.is_active, k.created_at
            FROM api_keys k
            JOIN users u ON k.user_id = u.id
            WHERE u.email = :email
        """), {"email": email})
        keys = result.fetchall()
    return [{"key": k[0], "plan": k[1], "active": k[2], "created": k[3].isoformat()} for k in keys]

# Revoke an API key
@app.delete("/api/key")
async def revoke_api_key(key: str = Body(..., embed=True)):
    async with AsyncSessionLocal() as session:
        await session.execute(text("UPDATE api_keys SET is_active = false WHERE key = :key"), {"key": key})
        await session.commit()
    return {"message": "API key revoked"}

# Admin: update plan manually
@app.put("/api/admin/plan")
async def update_plan(
    email: str = Body(..., embed=True), 
    plan: str = Body(..., embed=True),
    admin_token: str = Body(..., embed=True)
):
    if admin_token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid admin token")

    if plan not in PLAN_LIMITS:
        raise HTTPException(status_code=400, detail="Invalid plan")

    async with AsyncSessionLocal() as session:
        await session.execute(text("""
            UPDATE api_keys SET plan = :plan
            WHERE user_id = (SELECT id FROM users WHERE email = :email)
        """), {"plan": plan, "email": email})
        await session.commit()

    return {"message": f"Plan updated to {plan}"}

# Admin: usage stats for API keys
@app.get("/api/admin/usage")
async def get_usage_stats(admin_token: str):
    if admin_token != os.getenv("ADMIN_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid admin token")

    keys = redis.keys("ratelimit:*")
    stats = {}
    for key in keys:
        stats[key] = redis.get(key)

    return stats

# Create a new API key
@app.post("/api/key")
async def create_api_key(email: str = Body(..., embed=True), stripe_customer_id: str = Body(..., embed=True)):
    key = secrets.token_urlsafe(32)
    async with AsyncSessionLocal() as session:
        user_result = await session.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email})
        user = user_result.first()

        if user:
            user_id = user[0]
        else:
            result = await session.execute(text("""
                INSERT INTO users (email, stripe_customer_id) 
                VALUES (:email, :customer_id) 
                RETURNING id
            """), {"email": email, "customer_id": stripe_customer_id})
            user_id = result.scalar()

        await session.execute(text("""
            INSERT INTO api_keys (user_id, key, plan, is_active) 
            VALUES (:user_id, :key, 'free', true)
        """), {"user_id": user_id, "key": key})
        await session.commit()

    return {"api_key": key, "plan": "free"}

# Stripe webhook for subscription sync
@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        stripe_plan_id = subscription["items"]["data"][0]["price"]["id"]
        status = subscription["status"]

        # Map Stripe plan ID to internal plan names
        plan_map = {
            os.getenv("STRIPE_PRICE_ID_MONTHLY"): "pro_monthly",
            os.getenv("STRIPE_PRICE_ID_ANNUAL"): "pro_annual"
        }
        internal_plan = plan_map.get(stripe_plan_id, "free")

        async with AsyncSessionLocal() as session:
            await session.execute(text("""
                UPDATE api_keys SET plan = :plan, is_active = :active 
                WHERE user_id = (SELECT id FROM users WHERE stripe_customer_id = :cid)
            """), {
                "plan": internal_plan,
                "active": status == "active",
                "cid": customer_id
            })
            await session.commit()

    return {"status": "success"}

# Autocomplete endpoint
@app.get("/api/autocomplete")
async def autocomplete(q: str = "", request: Request = Depends(rate_limit)):
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query too short")

    async with AsyncSessionLocal() as session:
        sql = text("""
            SELECT full_address 
            FROM addresses 
            WHERE full_address ILIKE :query
            ORDER BY similarity(full_address, :query) DESC
            LIMIT 10
        """)
        result = await session.execute(sql, {"query": f"%{q}%"})
        matches = [row[0] for row in result.fetchall()]

    return {"query": q, "results": matches}

# Verify endpoint
@app.get("/api/verify")
async def verify(address: str, request: Request = Depends(rate_limit)):
    async with AsyncSessionLocal() as session:
        sql = text("SELECT 1 FROM addresses WHERE full_address ILIKE :address LIMIT 1")
        result = await session.execute(sql, {"address": address})
        match = result.first()

    return {"address": address, "valid": bool(match)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3001)