"""
Score candidate road points using nearby healthcare facilities.
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

print("=" * 60)
print("Scoring Road Network")
print("=" * 60)

ROOT = Path(__file__).resolve().parents[1]

INPUT_ROADS = ROOT / "data" / "processed" / "road_points.geojson"
INPUT_FACILITIES = ROOT / "data" / "processed" / "master_database.geojson"
OUTPUT_FILE = ROOT / "data" / "processed" / "scored_roads.geojson"

SEARCH_RADIUS = 800  # meters

FACILITY_WEIGHTS = {
    "Hospital": 8,
    "Clinic": 4,
    "Doctor": 2,
    "Pharmacy": -6,
}

ROAD_BONUS = {
    "trunk": 4,
    "primary": 3.5,
    "secondary": 3,
    "tertiary": 2,
    "residential": 1,
    "service": 0.5,
    "living_street": 0.5,
    "unclassified": 1,
    "primary_link": 2,
    "secondary_link": 1.5,
    "tertiary_link": 1,
    "trunk_link": 2.5,
}

roads = gpd.read_file(INPUT_ROADS).to_crs(32640)
facilities = gpd.read_file(INPUT_FACILITIES).to_crs(32640)

coords = np.c_[facilities.geometry.x, facilities.geometry.y]
tree = cKDTree(coords)

scores = []

for _, road in roads.iterrows():

    point = np.array([road.geometry.x, road.geometry.y])

    nearby_ids = tree.query_ball_point(point, SEARCH_RADIUS)

    score = ROAD_BONUS.get(road["road_type"], 1)

    for idx in nearby_ids:

        facility = facilities.iloc[idx]

        facility_point = np.array(facility.geometry.coords[0])

        distance = np.linalg.norm(point - facility_point)

        if distance < 1:
            distance = 1

        weight = FACILITY_WEIGHTS.get(facility["type"], 0)

        score += weight / (distance / 100)

    scores.append(score)

roads["score"] = scores

roads = roads.to_crs(4326)

roads.to_file(
    OUTPUT_FILE,
    driver="GeoJSON",
)

print()
print("Saved:")
print(OUTPUT_FILE)

print()
print(roads["score"].describe())