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