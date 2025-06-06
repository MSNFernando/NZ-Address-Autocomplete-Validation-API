# Makefile for NZ Address Autocomplete & Validation API

# Default environment file
ENV_FILE=.env

# Docker services
up:
	docker compose up --build

down:
	docker compose down

# Import NZ addresses CSV using the one-time importer
import-addresses:
	docker compose run --rm address_importer

# Start only the backend and dependencies (no frontend)
backend-only:
	docker compose up backend postgres redis

# Reset DB volume (DANGER: deletes data)
reset-db:
	docker compose down -v
	@echo "Postgres volume removed. Restart to reinit."

# View running containers
ps:
	docker compose ps

# Tail backend logs
logs:
	docker compose logs -f backend
