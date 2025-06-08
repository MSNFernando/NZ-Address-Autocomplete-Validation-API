# New Zealand Address Autocomplete &amp; Validation API

This is a full-stack, Dockerised platform for NZ address search, powered by **LINZ data** with built-in:
- Address Autocomplete &amp; Validation API
- API Key Management
- Stripe-powered subscription billing (Free, Monthly, Annual)
- Rate limiting per plan
- Demo Next.JS frontend for address search


## The Tech Stack

- **FastAPI** - API backend
- **PostgreSQL + PostGIS + pg_trgm** - LINZ address storage with fuzzy and spatial search
- **Redis** – Fast rate-limiting and caching
- **Stripe** – Subscription billing and trial periods
- **Next.js** – Frontend for demo, signup, and usage dashboard
- **Docker Compose** – Local dev environment


## Features

- Autocomplete address search using `ILIKE` + `pg_trgm`
- Exact address verification
- Stripe-powered billing flow (free trial included)
- Daily/monthly rate limiting per plan
- API key authentication
- Subscription syncing via Stripe webhooks
- Admin-ready database schema


## Project Structure
```bash
/NZ-Address-Autocomplete-Validation-API
├── Makefile
├── .env                        # Environment variables
├── docker-compose.yml          # Dev orchestration
├── db/
│   └── init.sql                # LINZ schema + data import
│   └── download_and_clean_csv.py # Downloads and cleans the Addresses CSV file
├── importer/
│   ├── Dockerfile
│   └── import_addresses.sh     # Copies and imports the cleaned Addresses CSV into the Database
├── backend/                    # FastAPI
├── frontend/                   # Next.js UI
```

## Getting Started
```bash
# Clone the Repo
git clone https://github.com/MSNFernando/NZ-Address-Autocomplete-Validation-API.get
cd NZ-Address-Autocomplete-Validation-API

# Modify the .env file
cp sample.env .env
nano .env

# update your variables!!!
```

## Pre-requisite step
```bash
# Download the LINZ Address CSV and Clean for required columns
cd db
python3 download_and_clean_csv.py

## Generate Admin Token
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Run the Docker
You can use the docker commands or use make which is included in the repo.
```bash
# Run with Docker
docker compose up -d --build

# Initialise the addresses table
docker compose run --rm address_importer
```

## Monitoring or Debugging Redis
```bash
docker exec -it api_redis redis-cli
> KEYS ratelimit:*
> GET ratelimit:yourkey:20250606
```

## Makefile
```bash
make up
make import-addresses
make reset-db
```

## Test API
```bash
curl -X 'GET' \
  'http://192.168.1.133:3001/api/autocomplete?q=149%20coronation' \ 
  -H 'accept: application/json' \
  -H 'Authorization: Bearer test_api_key_123'
```

## Add user for testing
```sql
-- Create user
INSERT INTO users (email, stripe_customer_id)
VALUES ('test@example.com', 'cus_test123')
RETURNING id;

-- Replace with the returned UUID
INSERT INTO api_keys (user_id, key, plan, is_active)
VALUES (
  'uuid-you-copied',
  'test_api_key_123',
  'free',
  true
);
```