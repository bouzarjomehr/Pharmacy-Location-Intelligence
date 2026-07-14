import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import geopandas as gpd

import config

print("=" * 60)
print("Cleaning Google Healthcare Database")
print("=" * 60)

file = config.DATA_PROCESSED / "google_healthcare.geojson"

gdf = gpd.read_file(file)

print("\nLoaded:", len(gdf))

# حذف رکوردهای بدون نام
gdf["name"] = gdf["name"].fillna("").str.strip()
gdf = gdf[gdf["name"] != ""]

print("After removing empty names:", len(gdf))

# حذف تکراری‌ها بر اساس نام و مختصات
gdf = gdf.drop_duplicates(
    subset=["name", "lat", "lon"]
)

print("After duplicate removal:", len(gdf))

# مرتب‌سازی
gdf = gdf.sort_values(
    by=["type", "name"]
)

# ذخیره
out_geo = config.DATA_PROCESSED / "google_healthcare_clean.geojson"
out_xlsx = config.DATA_PROCESSED / "google_healthcare_clean.xlsx"

gdf.to_file(out_geo, driver="GeoJSON")
gdf.drop(columns="geometry").to_excel(out_xlsx, index=False)

print("\nSaved:")
print(out_geo)
print(out_xlsx)

print("\nCounts:")
print(gdf["type"].value_counts())