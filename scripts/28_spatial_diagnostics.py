"""
Evaluate spatial characteristics of candidate pharmacy locations.
Produces diagnostic statistics without modifying project datasets.
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]

CANDIDATES = ROOT / "data" / "processed" / "candidate_database.geojson"
FACILITIES = ROOT / "data" / "processed" / "master_database.geojson"

OUTPUT = ROOT / "docs" / "spatial_report.xlsx"


def nearest_distance(points, targets):
    tree = cKDTree(np.c_[targets.geometry.x, targets.geometry.y])

    distances = []

    for geom in points.geometry:
        d, _ = tree.query([geom.x, geom.y], k=1)
        distances.append(round(float(d), 1))

    return distances


def main():

    print("=" * 70)
    print("SPATIAL DIAGNOSTICS")
    print("=" * 70)

    candidates = gpd.read_file(CANDIDATES).to_crs(32640)
    facilities = gpd.read_file(FACILITIES).to_crs(32640)

    report = candidates[[
        "candidate_id",
        "final_score",
        "road_type",
        "road_weight",
    ]].copy()

    for facility_type in [
        "Hospital",
        "Clinic",
        "Doctor",
        "Pharmacy",
    ]:

        subset = facilities[facilities["type"] == facility_type]

        report[f"nearest_{facility_type.lower()}_m"] = nearest_distance(
            candidates,
            subset,
        )

    summary = report.describe()

    with pd.ExcelWriter(OUTPUT) as writer:
        report.to_excel(
            writer,
            sheet_name="Candidates",
            index=False,
        )

        summary.to_excel(
            writer,
            sheet_name="Summary",
        )

    print()
    print("Saved:")
    print(OUTPUT)

    print()
    print(summary)


if __name__ == "__main__":
    main()