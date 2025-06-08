#!/bin/sh

set -e
. /app/.env

CSV="/app/db/nz-addresses-clean.csv"
TABLE_NAME="addresses"

echo "Importing CSV into $TABLE_NAME..."
psql -h postgres -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -c "\\copy $TABLE_NAME(
    address_id, source_dataset, change_id,
    full_address_number, full_road_name, full_address, territorial_authority,
    unit_type, unit_value, level_type, level_value,
    address_number_prefix, address_number, address_number_suffix, address_number_high,
    road_name_prefix, road_name, road_type_name, road_suffix,
    water_name, water_body_name,
    suburb_locality, town_city, postcode,
    address_class, address_lifecycle,
    gd2000_xcoord, gd2000_ycoord
  ) FROM '$CSV' WITH CSV HEADER"

echo "Updating spatial geometry..."
psql -h postgres -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<EOF
UPDATE $TABLE_NAME
SET location = ST_SetSRID(ST_MakePoint(gd2000_xcoord, gd2000_ycoord), 4167)
WHERE gd2000_xcoord IS NOT NULL AND gd2000_ycoord IS NOT NULL;
EOF

echo "Done importing addresses."
