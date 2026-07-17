"""
Multi-criteria scoring engine for pharmacy candidate locations.
"""

from pathlib import Path
import json
import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]

CONFIG_FILE = ROOT / "config" / "scoring.json"
INPUT_FACILITIES = ROOT / "data" / "processed" / "master_database.geojson"
INPUT_ROADS = ROOT / "data" / "processed" / "road_points.geojson"
OUTPUT_FILE = ROOT / "data" / "processed" / "road_scores_multicriteria.geojson"

TARGET_CRS = 32640
OUTPUT_CRS = 4326


def main():
    print("="*60)
    print("Multi-Criteria Scoring Engine")
    print("="*60)

    with open(CONFIG_FILE, encoding="utf8") as f:
        settings = json.load(f)

    facility_weights = settings["facility_weights"]
    road_bonus = settings["road_bonus"]
    radius = settings["search_radius"]
    sigma = settings["gaussian_sigma"]
    score_weights = settings["score_weights"]

    facilities = gpd.read_file(INPUT_FACILITIES).to_crs(TARGET_CRS)
    roads = gpd.read_file(INPUT_ROADS).to_crs(TARGET_CRS)

    coords = np.c_[facilities.geometry.x, facilities.geometry.y]
    tree = cKDTree(coords)

    hospital_scores=[]
    clinic_scores=[]
    doctor_scores=[]
    competition_scores=[]
    accessibility_scores=[]
    road_scores=[]
    final_scores=[]

    for road in roads.itertuples():
        point=np.array([road.geometry.x,road.geometry.y])
        nearby_ids=tree.query_ball_point(point,radius)

        hospital=clinic=doctor=0.0
        competition=0.0
        accessibility=0.0
        road_score=road_bonus.get(road.road_type,1)

        for idx in nearby_ids:
            facility=facilities.iloc[idx]
            dist=np.linalg.norm(point-np.array([facility.geometry.x,facility.geometry.y]))
            influence=np.exp(-(dist**2)/(2*sigma**2))
            t=facility["type"]

            if t=="Hospital":
                hospital += facility_weights["Hospital"]*influence
                accessibility += influence
            elif t=="Clinic":
                clinic += facility_weights["Clinic"]*influence
                accessibility += influence
            elif t=="Doctor":
                doctor += facility_weights["Doctor"]*influence
                accessibility += influence
            elif t == "Pharmacy":
                competition += (
                    -facility_weights["Pharmacy"]
                    * influence
                )

        prescription=hospital+clinic+doctor
        final=(prescription*score_weights["prescription"]
               -competition*score_weights["competition"]
               +accessibility*score_weights["accessibility"]
               +road_score*score_weights["road"])

        hospital_scores.append(hospital)
        clinic_scores.append(clinic)
        doctor_scores.append(doctor)
        competition_scores.append(competition)
        accessibility_scores.append(accessibility)
        road_scores.append(road_score)
        final_scores.append(final)

    roads["hospital_score"]=hospital_scores
    roads["clinic_score"]=clinic_scores
    roads["doctor_score"]=doctor_scores
    roads["competition_score"]=competition_scores
    roads["accessibility_score"]=accessibility_scores
    roads["road_score"]=road_scores
    roads["prescription_score"]=[h+c+d for h,c,d in zip(hospital_scores,clinic_scores,doctor_scores)]
    roads["final_score"]=final_scores

    roads=roads.to_crs(OUTPUT_CRS)
    roads.to_file(OUTPUT_FILE,driver="GeoJSON")

    print("\nSaved:")
    print(OUTPUT_FILE)
    print(roads[["hospital_score","clinic_score","doctor_score","competition_score","accessibility_score","road_score","final_score"]].describe())

if __name__=="__main__":
    main()
