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

    print("=" * 60)
    print("Multi-Criteria Scoring Engine")
    print("=" * 60)

    # -------------------------------------------------
    # Load settings
    # -------------------------------------------------

    with open(CONFIG_FILE, encoding="utf8") as f:
        settings = json.load(f)

    facility_weights = settings["weights"]
    road_bonus = settings["road_bonus"]

    radius = settings["radius"]
    sigma = settings["sigma"]

    score_weights = settings["score_weights"]

    # competition_radius فعلاً استفاده نمی‌شود
    # ولی برای نسخه‌های بعدی در فایل تنظیمات نگه می‌داریم.
    _competition_radius = settings["competition_radius"]

    # -------------------------------------------------
    # Load data
    # -------------------------------------------------

    facilities = (
        gpd.read_file(INPUT_FACILITIES)
        .to_crs(TARGET_CRS)
    )

    roads = (
        gpd.read_file(INPUT_ROADS)
        .to_crs(TARGET_CRS)
    )

    coords = np.c_[facilities.geometry.x, facilities.geometry.y]
    tree = cKDTree(coords)

    prescription_scores = []
    competition_scores = []
    accessibility_scores = []
    road_scores = []
    final_scores = []

    # -------------------------------------------------
    # Score every candidate
    # -------------------------------------------------

    for road in roads.itertuples():

        point = np.array([
            road.geometry.x,
            road.geometry.y
        ])

        nearby_ids = tree.query_ball_point(
            point,
            radius
        )

        prescription = 0.0
        competition = 0.0
        accessibility = 0.0

        road_score = road_bonus.get(
            road.road_type,
            1
        )

        for idx in nearby_ids:

            facility = facilities.iloc[idx]

            distance = np.linalg.norm(
                point -
                np.array([
                    facility.geometry.x,
                    facility.geometry.y
                ])
            )

            influence = np.exp(
                -(distance ** 2) /
                (2 * sigma ** 2)
            )

            facility_type = facility["type"]

            if facility_type == "Pharmacy":

                competition += influence

            else:

                prescription += (
                    facility_weights.get(
                        facility_type,
                        0
                    )
                    * influence
                )

                accessibility += influence

        final_score = (

            prescription
            * score_weights["prescription"]

            -

            competition
            * score_weights["competition"]

            +

            accessibility
            * score_weights["accessibility"]

            +

            road_score
            * score_weights["road"]

        )

        prescription_scores.append(prescription)
        competition_scores.append(competition)
        accessibility_scores.append(accessibility)
        road_scores.append(road_score)
        final_scores.append(final_score)

    # -------------------------------------------------
    # Save scores
    # -------------------------------------------------

    roads["prescription_score"] = prescription_scores
    roads["competition_score"] = competition_scores
    roads["accessibility_score"] = accessibility_scores
    roads["road_score"] = road_scores
    roads["final_score"] = final_scores

    roads = roads.to_crs(OUTPUT_CRS)

    roads.to_file(
        OUTPUT_FILE,
        driver="GeoJSON"
    )

    print()
    print("Saved:")
    print(OUTPUT_FILE)

    print()

    print(
        roads[
            [
                "prescription_score",
                "competition_score",
                "accessibility_score",
                "road_score",
                "final_score",
            ]
        ].describe()
    )


if __name__ == "__main__":
    main()