from pathlib import Path
import sys
import osmnx as ox

# -----------------------------
# Add project root
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
    "amenity": ["pharmacy"]
}

print("Downloading pharmacies...")

gdf = ox.features_from_point(
    (lat, lon),
    tags=tags,
    dist=15000
)

print()
print("=" * 50)
print(f"Downloaded {len(gdf)} pharmacies")
print("=" * 50)

print()
print(gdf[["name"]].head())

outfile = config.DATA_RAW / "pharmacies_osmnx.geojson"

gdf.to_file(outfile, driver="GeoJSON")

print()
print("Saved:")
print(outfile)