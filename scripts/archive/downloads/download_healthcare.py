from pathlib import Path
import sys
import osmnx as ox
import pandas as pd

# -----------------------------
# Project Root
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

# -----------------------------
# OSMnx Settings
# -----------------------------

ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.timeout = 180

lat, lon = config.MAP_CENTER

tags = {
    "amenity": [
        "pharmacy",
        "hospital",
        "clinic",
        "doctors",
        "healthcare"
    ]
}

print("Downloading healthcare facilities...")

gdf = ox.features_from_point(
    (lat, lon),
    tags=tags,
    dist=18000
)

print(f"\nDownloaded {len(gdf)} features.")

# -----------------------------
# Keep useful columns
# -----------------------------

wanted = [
    "amenity",
    "name",
    "operator",
    "brand",
    "phone",
    "addr:street",
    "geometry"
]

cols = [c for c in wanted if c in gdf.columns]

gdf = gdf[cols]

# -----------------------------
# Save GeoJSON
# -----------------------------

geojson_file = config.DATA_RAW / "healthcare.geojson"

gdf.to_file(geojson_file, driver="GeoJSON")

# -----------------------------
# Save CSV
# -----------------------------

csv_file = config.DATA_RAW / "healthcare.csv"

pd.DataFrame(gdf.drop(columns="geometry")).to_csv(
    csv_file,
    index=False,
    encoding="utf-8-sig"
)

# -----------------------------
# Save Excel
# -----------------------------

excel_file = config.DATA_RAW / "healthcare.xlsx"

pd.DataFrame(gdf.drop(columns="geometry")).to_excel(
    excel_file,
    index=False
)

print("\nSaved files:")

print(geojson_file)
print(csv_file)
print(excel_file)

print("\nAmenity counts:\n")
print(gdf["amenity"].value_counts())