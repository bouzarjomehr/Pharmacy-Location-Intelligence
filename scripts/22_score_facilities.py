from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

print("="*60)
print("Scoring Healthcare Facilities")
print("="*60)

ROOT = Path(__file__).resolve().parents[1]

gdf = gpd.read_file(ROOT/"data/processed/master_database.geojson")
gdf = gdf.to_crs(32640)

coords = np.c_[gdf.geometry.x, gdf.geometry.y]
tree = cKDTree(coords)

radius = 250

facility_weights = {
    "Hospital":8,
    "Clinic":4,
    "Doctor":2,
    "Pharmacy":-6
}

scores = []
nearest_pharmacy = []
doctor_count = []
clinic_count = []
hospital_count = []
pharmacy_count = []

for idx, row in gdf.iterrows():

    point = np.array([row.geometry.x, row.geometry.y])

    ids = tree.query_ball_point(point, radius)

    score = 0

    dcount = 0
    ccount = 0
    hcount = 0
    pcount = 0

    nearest = np.inf

    for i in ids:

        if i == idx:
            continue

        other = gdf.iloc[i]

        dist = np.linalg.norm(
            point -
            np.array([other.geometry.x, other.geometry.y])
        )

        t = other["type"]

        if t == "Doctor":
            dcount += 1

        elif t == "Clinic":
            ccount += 1

        elif t == "Hospital":
            hcount += 1

        elif t == "Pharmacy":
            pcount += 1
            nearest = min(nearest, dist)

        score += facility_weights.get(t,0) * np.exp(-(dist**2)/(2*250**2))

    scores.append(score)

    doctor_count.append(dcount)
    clinic_count.append(ccount)
    hospital_count.append(hcount)
    pharmacy_count.append(pcount)

    if np.isinf(nearest):
        nearest_pharmacy.append(None)
    else:
        nearest_pharmacy.append(round(nearest,1))

gdf["facility_score"] = scores
gdf["doctor_count"] = doctor_count
gdf["clinic_count"] = clinic_count
gdf["hospital_count"] = hospital_count
gdf["pharmacy_count"] = pharmacy_count
gdf["nearest_pharmacy_m"] = nearest_pharmacy

gdf = gdf.to_crs(4326)

outfile = ROOT/"data/processed/facility_scores.geojson"

gdf.to_file(outfile, driver="GeoJSON")

print()
print("Saved:")
print(outfile)
print()
print(gdf[[
    "name",
    "type",
    "facility_score",
    "doctor_count",
    "pharmacy_count",
    "nearest_pharmacy_m"
]].head())