from pathlib import Path
import sys

import osmnx as ox
import geopandas as gpd
import pandas as pd

# -------------------------------------------------
# Project Root
# -------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

# -------------------------------------------------
# OSMnx
# -------------------------------------------------

ox.settings.use_cache = True
ox.settings.log_console = True
ox.settings.timeout = 300

lat, lon = config.MAP_CENTER

tags = {

    "amenity":[
        "pharmacy",
        "hospital",
        "clinic",
        "doctors"
    ],

    "office":"doctor",

    "healthcare":True,

    "building":"hospital",

    "dispensing":"yes"

}

print("="*60)
print("Downloading Master Healthcare Database")
print("="*60)

gdf = ox.features_from_point(
    (lat,lon),
    tags=tags,
    dist=18000
)

print()
print("Downloaded:",len(gdf))

# -------------------------------------------------
# Convert polygons to centroid
# -------------------------------------------------

gdf["geometry"] = gdf.geometry.centroid

# -------------------------------------------------
# Remove duplicate geometries
# -------------------------------------------------

gdf["x"] = gdf.geometry.x
gdf["y"] = gdf.geometry.y

gdf = gdf.drop_duplicates(
    subset=["x","y","name"],
    keep="first"
)

print("After dedup:",len(gdf))

# -------------------------------------------------
# Save
# -------------------------------------------------

outfile_geojson = config.DATA_RAW/"master_healthcare.geojson"
outfile_excel = config.DATA_RAW/"master_healthcare.xlsx"

gdf.to_file(outfile_geojson,driver="GeoJSON")

gdf.drop(columns="geometry").to_excel(
    outfile_excel,
    index=False
)

print()
print("Saved:")
print(outfile_geojson)
print(outfile_excel)

print()
print("="*60)
print("Amenity")
print("="*60)

if "amenity" in gdf.columns:
    print(gdf["amenity"].value_counts())

print()

print("="*60)
print("Healthcare")
print("="*60)

if "healthcare" in gdf.columns:
    print(gdf["healthcare"].value_counts())

print()

print("="*60)
print("Office")
print("="*60)

if "office" in gdf.columns:
    print(gdf["office"].value_counts())