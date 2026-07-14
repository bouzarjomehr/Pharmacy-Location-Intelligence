from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

print("=" * 60)
print("Scoring Road Network")
print("=" * 60)

ROOT = Path(__file__).resolve().parents[1]

roads = gpd.read_file(ROOT/"data/processed/road_points.geojson")
fac = gpd.read_file(ROOT/"data/processed/master_database.geojson")

roads = roads.to_crs(32640)
fac = fac.to_crs(32640)

coords = np.c_[fac.geometry.x, fac.geometry.y]
tree = cKDTree(coords)

weights = {
    "Hospital":8,
    "Clinic":4,
    "Doctor":2,
    "Pharmacy":-6
}

road_bonus = {
    "trunk":4,
    "primary":3.5,
    "secondary":3,
    "tertiary":2,
    "residential":1,
    "service":0.5,
    "living_street":0.5,
    "unclassified":1,
    "primary_link":2,
    "secondary_link":1.5,
    "tertiary_link":1,
    "trunk_link":2.5
}

scores=[]

radius=800

for p,row in roads.iterrows():

    point=np.array([row.geometry.x,row.geometry.y])

    ids=tree.query_ball_point(point,radius)

    s=road_bonus.get(row["road_type"],1)

    for i in ids:

        r=fac.iloc[i]

        d=point-fac.geometry.iloc[i].coords[0]
        dist=np.sqrt(d[0]**2+d[1]**2)

        if dist<1:
            dist=1

        w=weights.get(r["type"],0)

        s+=w/(dist/100)

    scores.append(s)

roads["score"]=scores

roads=roads.to_crs(4326)

outfile=ROOT/"data/processed/scored_roads.geojson"

roads.to_file(outfile,driver="GeoJSON")

print()
print("Saved:")
print(outfile)
print()
print(roads["score"].describe())