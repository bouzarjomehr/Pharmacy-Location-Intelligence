import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import config
import osmnx as ox
import geopandas as gpd

print("=" * 60)
print("Downloading Buildings")
print("=" * 60)

tags = {
    "building": True
}

gdf = ox.features_from_point(
    config.MAP_CENTER,
    tags=tags,
    dist=18000
)

print(f"\nDownloaded {len(gdf):,} buildings")

# فقط ساختمان‌هایی که واقعاً پلیگون هستند
gdf = gdf[gdf.geometry.type.isin(["Polygon", "MultiPolygon"])]

print(f"Polygons: {len(gdf):,}")

outfile = config.DATA_PROCESSED / "buildings.geojson"

gdf.to_file(outfile, driver="GeoJSON")

print("\nSaved:")
print(outfile)