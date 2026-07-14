from pathlib import Path
import json

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

print("="*60)
print("Multi-Criteria Scoring Engine")
print("="*60)

ROOT = Path(__file__).resolve().parents[1]

# ---------- Settings ----------

with open(ROOT/"config"/"scoring.json", encoding="utf8") as f:
    settings = json.load(f)

weights = settings["weights"]

road_bonus = settings["road_bonus"]

radius = settings["radius"]

sigma = settings["sigma"]

competition_radius = settings["competition_radius"]

score_weights = settings["score_weights"]

# ---------- Data ----------

fac = gpd.read_file(ROOT/"data/processed/master_database.geojson").to_crs(32640)

roads = gpd.read_file(ROOT/"data/processed/road_points.geojson").to_crs(32640)

coords = np.c_[fac.geometry.x, fac.geometry.y]

tree = cKDTree(coords)

road_scores=[]

prescription_scores=[]

competition_scores=[]

access_scores=[]

road_importance=[]

for _, road in roads.iterrows():

    point=np.array([road.geometry.x,road.geometry.y])

    ids=tree.query_ball_point(point,radius)

    prescription=0

    competition=0

    access=0

    road_score=road_bonus.get(road["road_type"],1)

    for i in ids:

        f=fac.iloc[i]

        dist=np.linalg.norm(
            point-
            np.array([f.geometry.x,f.geometry.y])
        )

        influence=np.exp(-(dist**2)/(2*sigma**2))

        t=f["type"]

        if t=="Pharmacy":

            competition+=influence

        else:

            prescription+=weights.get(t,0)*influence

            access+=influence

    final=(
        prescription*score_weights["prescription"]
        -
        competition*score_weights["competition"]
        +
        access*score_weights["accessibility"]
        +
        road_score*score_weights["road"]
    )

    prescription_scores.append(prescription)

    competition_scores.append(competition)

    access_scores.append(access)

    road_importance.append(road_score)

    road_scores.append(final)

roads["prescription_score"]=prescription_scores

roads["competition_score"]=competition_scores

roads["accessibility_score"]=access_scores

roads["road_score"]=road_importance

roads["final_score"]=road_scores

roads=roads.to_crs(4326)

outfile=ROOT/"data/processed/road_scores_multicriteria.geojson"

roads.to_file(outfile,driver="GeoJSON")

print()

print("Saved:")

print(outfile)

print()

print(roads[[
    "prescription_score",
    "competition_score",
    "accessibility_score",
    "road_score",
    "final_score"
]].describe())