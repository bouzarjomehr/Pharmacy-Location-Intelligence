"""
Score healthcare facilities based on nearby healthcare providers.
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

print("=" * 60)
print("Scoring Healthcare Facilities")
print("=" * 60)

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "master_database.geojson"
OUTPUT_FILE = ROOT / "data" / "processed" / "facility_scores.geojson"

TARGET_CRS = 32640
OUTPUT_CRS = 4326

SEARCH_RADIUS = 250

FACILITY_WEIGHTS = {
    "Hospital": 8,
    "Clinic": 4,
    "Doctor": 2,
    "Pharmacy": -6,
}

gdf = gpd.read_file(INPUT_FILE).to_crs(TARGET_CRS)

coords = np.c_[gdf.geometry.x, gdf.geometry.y]
tree = cKDTree(coords)

scores = []

doctor_count = []
clinic_count = []
hospital_count = []
pharmacy_count = []
nearest_pharmacy = []

for idx, row in gdf.iterrows():

    point = np.array([row.geometry.x, row.geometry.y])

    nearby_ids = tree.query_ball_point(point, SEARCH_RADIUS)

    score = 0.0

    doctors = 0
    clinics = 0
    hospitals = 0
    pharmacies = 0

    nearest = np.inf

    for i in nearby_ids:

        if i == idx:
            continue

        other = gdf.iloc[i]

        distance = np.linalg.norm(
            point - np.array([other.geometry.x, other.geometry.y])
        )

        facility_type = other["type"]

        if facility_type == "Doctor":
            doctors += 1

        elif facility_type == "Clinic":
            clinics += 1

        elif facility_type == "Hospital":
            hospitals += 1

        elif facility_type == "Pharmacy":
            pharmacies += 1
            nearest = min(nearest, distance)

        influence = np.exp(
            -(distance ** 2) / (2 * SEARCH_RADIUS ** 2)
        )

        score += (
            FACILITY_WEIGHTS.get(facility_type, 0)
            * influence
        )

    scores.append(score)

    doctor_count.append(doctors)
    clinic_count.append(clinics)
    hospital_count.append(hospitals)
    pharmacy_count.append(pharmacies)

    if np.isinf(nearest):
        nearest_pharmacy.append(None)
    else:
        nearest_pharmacy.append(round(nearest, 1))

gdf["facility_score"] = scores
gdf["doctor_count"] = doctor_count
gdf["clinic_count"] = clinic_count
gdf["hospital_count"] = hospital_count
gdf["pharmacy_count"] = pharmacy_count
gdf["nearest_pharmacy_m"] = nearest_pharmacy

gdf = gdf.to_crs(OUTPUT_CRS)

gdf.to_file(
    OUTPUT_FILE,
    driver="GeoJSON",
)

print()
print("Saved:")
print(OUTPUT_FILE)

print()
print(
    gdf[
        [
            "name",
            "type",
            "facility_score",
            "doctor_count",
            "pharmacy_count",
            "nearest_pharmacy_m",
        ]
    ].head()
)