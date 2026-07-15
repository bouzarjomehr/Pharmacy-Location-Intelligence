from pathlib import Path
import sys

import geopandas as gpd
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

# --------------------------------------------------

print("Loading master dataset...")

gdf = gpd.read_file(
    config.DATA_RAW / "master_healthcare.geojson"
)

# --------------------------------------------------
# Standardize Type
# --------------------------------------------------

def get_type(row):

    amenity = str(row.get("amenity", "")).lower()
    healthcare = str(row.get("healthcare", "")).lower()
    office = str(row.get("office", "")).lower()

    if "pharmacy" in amenity or "pharmacy" in healthcare:
        return "Pharmacy"

    if (
        "doctor" in amenity
        or "doctor" in healthcare
        or office == "doctor"
    ):
        return "Doctor"

    if "clinic" in amenity or "clinic" in healthcare:
        return "Clinic"

    if "hospital" in amenity or "hospital" in healthcare:
        return "Hospital"

    return None

gdf["type"] = gdf.apply(get_type, axis=1)

# --------------------------------------------------

gdf = gdf[gdf["type"].notna()]

# --------------------------------------------------

gdf["lat"] = gdf.geometry.y
gdf["lon"] = gdf.geometry.x

# --------------------------------------------------

cols = [
    "type",
    "name",
    "lat",
    "lon",
    "geometry"
]

gdf = gdf[cols]

# --------------------------------------------------
# Remove duplicates
# --------------------------------------------------

gdf = gdf.drop_duplicates(
    subset=["type","name","lat","lon"]
)

# --------------------------------------------------
# Save
# --------------------------------------------------

outfile_geo = config.DATA_PROCESSED / "master_healthcare_clean.geojson"

outfile_xlsx = config.DATA_PROCESSED / "master_healthcare_clean.xlsx"

gdf.to_file(outfile_geo, driver="GeoJSON")

gdf.drop(columns="geometry").to_excel(
    outfile_xlsx,
    index=False
)

print()

print("Saved:")
print(outfile_geo)
print(outfile_xlsx)

print()

print(gdf["type"].value_counts())