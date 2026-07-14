from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parent.parent

print("=" * 60)
print("Creating Road Sample Points")
print("=" * 60)

roads = gpd.read_file(
    ROOT / "data" / "processed" / "roads_clean.geojson"
)

roads = roads.to_crs(32640)

DISTANCE = {

    "trunk":40,
    "trunk_link":40,

    "primary":40,
    "primary_link":40,

    "secondary":50,
    "secondary_link":50,

    "tertiary":60,
    "tertiary_link":60,

    "residential":80,

    "service":90,

    "living_street":100,

    "unclassified":80

}

points = []

for _, row in roads.iterrows():

    line = row.geometry

    if line is None:
        continue

    d = DISTANCE[row.road_type]

    length = line.length

    current = 0

    while current <= length:

        p = line.interpolate(current)

        points.append({

            "road_type":row.road_type,

            "road_weight":row.road_weight,

            "geometry":p

        })

        current += d

gdf = gpd.GeoDataFrame(
    points,
    crs=roads.crs
)

outfile = ROOT / "data" / "processed" / "road_points.geojson"

gdf.to_file(outfile, driver="GeoJSON")

print()
print("Saved:")
print(outfile)

print()
print("Total road points:", len(gdf))

print()

print(
    gdf["road_type"].value_counts()
)