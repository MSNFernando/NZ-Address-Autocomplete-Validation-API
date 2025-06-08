FROM alpine:3.18

RUN apk add --no-cache curl postgresql-client

WORKDIR /app

# Copy clean CSV from project root into container
COPY db/nz-addresses-clean.csv /app/db/nz-addresses-clean.csv

# Copy the clean import script
COPY importer/import_addresses.sh .
RUN chmod +x import_addresses.sh

CMD ["sh", "import_addresses.sh"]
