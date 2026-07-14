from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parents[1]

print("=" * 60)
print("Creating Smart Candidate Points")
print("=" * 60)

roads = gpd.read_file(
    ROOT / "data" / "processed" / "roads_clean.geojson"
)

roads = roads.to_crs(32640)

points = []

for _, row in roads.iterrows():

    line = row.geometry

    if line is None:
        continue

    length = line.length

    # -------------------------
    # Determine spacing
    # -------------------------

    if length < 100:
        spacing = length + 1

    elif length < 250:
        spacing = length / 2

    elif length < 500:
        spacing = 125

    elif length < 1000:
        spacing = 100

    else:
        spacing = 120

    d = 0

    while d <= length:

        p = line.interpolate(d)

        points.append({

            "road_type": row.road_type,

            "road_weight": row.road_weight,

            "geometry": p

        })

        d += spacing

    # همیشه انتهای خیابان را هم اضافه کن
    p = line.interpolate(length)

    points.append({

        "road_type": row.road_type,

        "road_weight": row.road_weight,

        "geometry": p

    })

gdf = gpd.GeoDataFrame(
    points,
    crs=roads.crs
)

# حذف نقاط تکراری
gdf["x"] = gdf.geometry.x.round(1)
gdf["y"] = gdf.geometry.y.round(1)

gdf = gdf.drop_duplicates(
    subset=["x", "y"]
)

gdf = gdf.drop(
    columns=["x", "y"]
)

gdf = gdf.to_crs(4326)

outfile = ROOT / "data" / "processed" / "road_points.geojson"

gdf.to_file(
    outfile,
    driver="GeoJSON"
)

print()
print("Saved:")
print(outfile)

print()
print("Total Smart Candidates:", len(gdf))