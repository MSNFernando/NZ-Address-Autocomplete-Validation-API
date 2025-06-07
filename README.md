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
├── .env                      # Environment variables
├── docker-compose.yml        # Dev orchestration
├── db/
│   └── init.sql              # LINZ schema + data import
├── importer/
│   ├── Dockerfile
│   └── import_addresses.sh
├── backend/                  # FastAPI
├── frontend/                 # Next.js UI
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

# Run with Docker
docker compose up -d --build

# Initialise the addresses table
cd db
chmod +x import_addresses.sh
./import_addresses.sh
```

## If the import_addresses doesnt work
```bash
# Download the LINZ Address CSV
wget https://s3.filebase.co.nz/public/download%2F/nz-addresses.csv -o nz-address.csv

# Import into the addresses table
docker exec -i linz_postgres psql -U addressapi -d nz_address \
  -c "copy addresses FROM '/data/nz-address.csv' with CSV HEADER"

# Populate PostGIS geometry
UPDATE addresses
SET location = ST_SetSRID(ST_MakePoint(gd2000_xcoord, gd2000_ycoord), 4167)
WHERE gd2000_xcoord IS NOT NULL AND gd2000_ycoord IS NOT NULL;
```

## Generate Admin Token
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
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