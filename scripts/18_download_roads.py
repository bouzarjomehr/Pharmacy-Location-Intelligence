from pathlib import Path

import osmnx as ox
import geopandas as gpd

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))
import config


print("=" * 60)
print("Downloading Road Network")
print("=" * 60)

tags = {
    "highway": True
}

roads = ox.features_from_point(
    config.MAP_CENTER,
    tags=tags,
    dist=18000
)

roads = roads[
    roads.geometry.type.isin(
        ["LineString", "MultiLineString"]
    )
]

roads = roads.to_crs(32640)

ROOT = Path(__file__).resolve().parent.parent

outfile = ROOT / "data" / "processed" / "roads.geojson"

roads.to_file(outfile, driver="GeoJSON")

print()
print("Saved:")
print(outfile)

print()
print("Highway types:")
print(roads["highway"].explode().value_counts().head(30))