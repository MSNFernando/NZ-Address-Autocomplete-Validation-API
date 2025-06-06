#!/bin/bash

# Load environment variables from .env
set -o allexport
source .env
set +o allexport

# Configuration
CSV_URL="https://s3.filebase.co.nz/public/download%2F/nz-addresses.csv"
CSV_FILE="nz-addresses.csv"
CSV_PATH="/data/${CSV_FILE}"
CONTAINER_NAME="api_postgres"
TABLE_NAME="addresses"

echo "Downloading latest NZ address dataset..."
curl -L "$CSV_URL" -o "./db/$CSV_FILE"

echo "Copying CSV to Postgres container..."
docker cp "./db/$CSV_FILE" "$CONTAINER_NAME:$CSV_PATH"

echo "Importing CSV into $TABLE_NAME..."
docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\
  \COPY $TABLE_NAME(
    address_id, source_dataset, change_id,
    full_address_number, full_road_name, full_address, territorial_authority,
    unit_type, unit_value, level_type, level_value,
    address_number_prefix, address_number, address_number_suffix, address_number_high,
    road_name_prefix, road_name, road_type_name, road_suffix,
    water_name, water_body_name,
    suburb_locality, town_city, postcode,
    address_class, address_lifecycle,
    gd2000_xcoord, gd2000_ycoord
  ) FROM '$CSV_PATH' WITH CSV HEADER;
"

echo "Updating spatial geometry from coordinates..."
docker exec -i "$CONTAINER_NAME" psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\
  UPDATE $TABLE_NAME SET location = ST_SetSRID(ST_MakePoint(gd2000_xcoord, gd2000_ycoord), 4167) \
  WHERE gd2000_xcoord IS NOT NULL AND gd2000_ycoord IS NOT NULL;
"

echo "Address seeding complete."
