import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import geopandas as gpd
import pandas as pd

import config

print("=" * 60)
print("Preparing Master Database")
print("=" * 60)

INPUT = config.DATA_PROCESSED / "google_healthcare_clean.geojson"

gdf = gpd.read_file(INPUT)

# -------------------------------------------------
# استانداردسازی ستون‌ها
# -------------------------------------------------

columns = {

    "google_id":"id",
    "name":"name",
    "type":"type",
    "lat":"lat",
    "lon":"lon",
    "rating":"rating",
    "reviews":"reviews",
    "address":"address",
    "phone":"phone",
    "website":"website",

}

gdf = gdf[list(columns.keys()) + ["geometry"]]

gdf = gdf.rename(columns=columns)

# -------------------------------------------------
# ستون‌هایی که بعداً استفاده می‌کنیم
# -------------------------------------------------

gdf["score"] = 0.0

gdf["weight"] = 0.0

gdf["specialty"] = ""

gdf["population"] = None

gdf["nearest_pharmacy"] = None

gdf["nearest_hospital"] = None

gdf["nearest_doctor"] = None

# -------------------------------------------------

OUT_GEO = config.DATA_PROCESSED / "master_database.geojson"

OUT_XLSX = config.DATA_PROCESSED / "master_database.xlsx"

gdf.to_file(OUT_GEO, driver="GeoJSON")

gdf.drop(columns="geometry").to_excel(
    OUT_XLSX,
    index=False
)

print()

print("Saved:")

print(OUT_GEO)

print(OUT_XLSX)

print()

print(gdf.head())

print()

print("Total:", len(gdf))