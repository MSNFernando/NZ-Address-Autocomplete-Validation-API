import wget
import csv

print("Downloading NZ-Address file from Filebase S3...")
wget.download("https://s3.filebase.co.nz/public/download%2Fnz-addresses.csv", outfile="nz-addresses.csv")
print("Download complete")

print("Cleaning CSV file...")
COLUMNS = [
    "address_id", "source_dataset", "change_id",
    "full_address_number", "full_road_name", "full_address", "territorial_authority",
    "unit_type", "unit_value", "level_type", "level_value",
    "address_number_prefix", "address_number", "address_number_suffix", "address_number_high",
    "road_name_prefix", "road_name", "road_type_name", "road_suffix",
    "water_name", "water_body_name",
    "suburb_locality", "town_city", "postcode",
    "address_class", "address_lifecycle",
    "gd2000_xcoord", "gd2000_ycoord"
]

with open("./nz-addresses.csv", newline='', encoding='utf-8') as infile, \
     open("./nz-addresses-clean.csv", "w", newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=COLUMNS, quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in reader:
        writer.writerow({col: row.get(col, "") for col in COLUMNS})

print("All done")