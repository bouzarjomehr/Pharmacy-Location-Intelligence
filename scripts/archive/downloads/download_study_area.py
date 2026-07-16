from pathlib import Path
import sys

# -----------------------------
# Add project root to PYTHONPATH
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

import osmnx as ox

print("Project Root :", config.ROOT)
print("Raw Data Dir :", config.DATA_RAW)

PLACE = "Yazd County, Yazd Province, Iran"

print("\nDownloading study area...")

boundary = ox.geocode_to_gdf(PLACE)

print(boundary[["display_name"]])

outfile = config.DATA_RAW / "study_area_boundary.geojson"

boundary.to_file(outfile, driver="GeoJSON")

print("\nSaved successfully:")
print(outfile)