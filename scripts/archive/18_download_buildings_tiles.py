import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import config
import osmnx as ox
import geopandas as gpd
from shapely.geometry import box
import pandas as pd

print("="*60)
print("Downloading Buildings (Tile Mode)")
print("="*60)

# ----------------------------------------
# تنظیمات
# ----------------------------------------

RADIUS = 18000          # متر
TILE_SIZE = 3000        # متر

# ----------------------------------------
# ساخت محدوده
# ----------------------------------------

boundary = ox.utils_geo.bbox_from_point(
    config.MAP_CENTER,
    dist=RADIUS
)

west, south, east, north = boundary

boundary_poly = box(west, south, east, north)

boundary_gdf = gpd.GeoDataFrame(
    geometry=[boundary_poly],
    crs="EPSG:4326"
).to_crs(32640)

xmin, ymin, xmax, ymax = boundary_gdf.total_bounds

tiles = []

x = xmin
while x < xmax:

    y = ymin

    while y < ymax:

        tiles.append(
            box(
                x,
                y,
                min(x+TILE_SIZE, xmax),
                min(y+TILE_SIZE, ymax)
            )
        )

        y += TILE_SIZE

    x += TILE_SIZE

tiles = gpd.GeoDataFrame(
    geometry=tiles,
    crs=32640
).to_crs(4326)

print(f"\nTiles : {len(tiles)}")

# ----------------------------------------
# دانلود
# ----------------------------------------

all_buildings = []

tags = {
    "building": True
}

for i, tile in enumerate(tiles.geometry, start=1):

    print(f"Tile {i}/{len(tiles)}")

    try:

        gdf = ox.features_from_polygon(
            tile,
            tags
        )

        if len(gdf):

            all_buildings.append(gdf)

            print(f"   {len(gdf)} buildings")

    except Exception as e:

        print(e)

# ----------------------------------------
# ادغام
# ----------------------------------------

gdf = pd.concat(all_buildings)

gdf = gpd.GeoDataFrame(gdf)

print("\nBefore dedup :", len(gdf))

gdf = gdf[~gdf.index.duplicated()]

print("After dedup :", len(gdf))

gdf = gdf[gdf.geometry.type.isin(
    ["Polygon","MultiPolygon"]
)]

outfile = config.DATA_PROCESSED / "buildings.geojson"

gdf.to_file(outfile, driver="GeoJSON")

print("\nSaved:")
print(outfile)