"""
30_spatial_diagnostics.py

Validation Phase

Generate descriptive statistics and spatial diagnostics
for the selected pharmacy locations.

Outputs
-------
outputs/validation/

30_spatial_summary.xlsx
30_score_distribution.png
30_driver_distribution.png
30_validation_report.md
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
from scipy.spatial import cKDTree

import config.app_config as app_config


# ==========================================================
# Files
# ==========================================================

BEST_FILE = (
    ROOT
    / "data"
    / "processed"
    / "best_areas.geojson"
)

MASTER_FILE = (
    ROOT
    / "data"
    / "processed"
    / "master_database.geojson"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "validation"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

EXCEL_FILE = OUTPUT_DIR / "30_spatial_summary.xlsx"

HISTOGRAM_FILE = OUTPUT_DIR / "30_score_distribution.png"

DRIVER_FILE = OUTPUT_DIR / "30_driver_distribution.png"

REPORT_FILE = OUTPUT_DIR / "30_validation_report.md"


# ==========================================================
# Utility
# ==========================================================

def nearest_distance(
    source_gdf,
    target_gdf,
):
    """
    Distance (meters) to nearest target feature.
    """

    tree = cKDTree(
        np.c_[
            target_gdf.geometry.x,
            target_gdf.geometry.y,
        ]
    )

    distances = []

    for geom in source_gdf.geometry:

        d, _ = tree.query(
            [
                geom.x,
                geom.y,
            ],
            k=1,
        )

        distances.append(float(d))

    return np.array(distances)


# ==========================================================
# Main
# ==========================================================

def main():

    print("=" * 70)
    print("Spatial Diagnostics")
    print("=" * 70)

    selected = (
        gpd.read_file(BEST_FILE)
        .to_crs(app_config.TARGET_CRS)
    )

    facilities = (
        gpd.read_file(MASTER_FILE)
        .to_crs(app_config.TARGET_CRS)
    )

    print()
    print(f"Selected locations : {len(selected)}")
    print()

    # ------------------------------------------------------
    # Distance analysis
    # ------------------------------------------------------

    summary_tables = {}

    distance_table = pd.DataFrame(
        {
            "candidate_id": selected["candidate_id"]
        }
    )

    for facility_type in [

        "Hospital",

        "Clinic",

        "Doctor",

        "Pharmacy",

    ]:

        subset = facilities[
            facilities["type"] == facility_type
        ]

        if len(subset) == 0:
            continue

        d = nearest_distance(
            selected,
            subset,
        )

        distance_table[
            f"{facility_type.lower()}_distance_m"
        ] = d

        summary_tables[
            facility_type
        ] = pd.Series(
            {
                "mean": d.mean(),
                "median": np.median(d),
                "min": d.min(),
                "max": d.max(),
                "std": d.std(),
            }
        )

    distance_summary = (
        pd.DataFrame(summary_tables)
        .T
        .round(1)
    )

    # ------------------------------------------------------
    # Score summary
    # ------------------------------------------------------

    score_columns = [

        "final_score",

        "prescription_norm",

        "competition_norm",

        "population_norm",

        "road_norm",

    ]

    score_summary = (
        selected[
            score_columns
        ]
        .describe()
        .T[
            [
                "mean",
                "50%",
                "std",
                "min",
                "25%",
                "75%",
                "max",
            ]
        ]
        .rename(
            columns={
                "50%": "median",
                "25%": "Q1",
                "75%": "Q3",
            }
        )
        .round(2)
    )

    # ------------------------------------------------------
    # Main driver distribution
    # ------------------------------------------------------

    driver_counts = (
        selected["main_reason"]
        .value_counts()
        .rename_axis("Driver")
        .to_frame("Count")
    )

    driver_counts["Percent"] = (
        driver_counts["Count"]
        / driver_counts["Count"].sum()
        * 100
    ).round(1)

    # ------------------------------------------------------
    # Road type distribution
    # ------------------------------------------------------

    road_counts = (
        selected["road_type"]
        .value_counts()
        .rename_axis("Road Type")
        .to_frame("Count")
    )

    road_counts["Percent"] = (
        road_counts["Count"]
        / road_counts["Count"].sum()
        * 100
    ).round(1)

    # -------------------------------------------------
    # Score distribution
    # -------------------------------------------------

    plt.figure(figsize=(8, 5))

    plt.hist(
        selected["final_score"],
        bins=30,
    )

    plt.xlabel("Final Score")
    plt.ylabel("Candidate Count")
    plt.title("Distribution of Final Scores")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "30_score_distribution.png",
        dpi=300,
    )

    plt.close()

    # -------------------------------------------------
    # Road type distribution
    # -------------------------------------------------

    plt.figure(figsize=(7, 5))

    (
        selected["road_type"]
        .value_counts()
        .sort_values()
        .plot(kind="barh")
    )

    plt.xlabel("Candidate Count")
    plt.ylabel("Road Type")
    plt.title("Selected Candidates by Road Type")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "30_road_type_distribution.png",
        dpi=300,
    )

    plt.close()

    # -------------------------------------------------
    # Main driver distribution
    # -------------------------------------------------

    plt.figure(figsize=(7, 5))

    (
        selected["main_reason"]
        .fillna("Unknown")
        .value_counts()
        .sort_values()
        .plot(kind="barh")
    )

    plt.xlabel("Candidate Count")
    plt.ylabel("Main Driver")
    plt.title("Dominant Driver of Final Score")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "30_main_driver_distribution.png",
        dpi=300,
    )

    plt.close()

    # -------------------------------------------------
    # Nearest pharmacy distance
    # -------------------------------------------------

    pharmacies = facilities[
        facilities["type"] == "Pharmacy"
    ].copy()

    tree = cKDTree(
        np.c_[
            pharmacies.geometry.x,
            pharmacies.geometry.y,
        ]
    )

    distances = []

    for geom in selected.geometry:

        d, _ = tree.query(
            [geom.x, geom.y],
            k=1,
        )

        distances.append(d)

    selected["nearest_pharmacy_m"] = distances

    plt.figure(figsize=(8, 5))

    plt.hist(
        selected["nearest_pharmacy_m"],
        bins=30,
    )

    plt.xlabel("Nearest Existing Pharmacy (m)")
    plt.ylabel("Candidate Count")
    plt.title("Distance to Nearest Existing Pharmacy")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "30_nearest_pharmacy_distance.png",
        dpi=300,
    )

    plt.close()

    # -------------------------------------------------
    # Correlation matrix
    # -------------------------------------------------

    corr_columns = [
        c
        for c in [
            "prescription_norm",
            "competition_norm",
            "population_norm",
            "road_norm",
            "final_score",
        ]
        if c in selected.columns
    ]

    corr = selected[corr_columns].corr()

    corr.to_excel(
        OUTPUT_DIR / "30_correlation_matrix.xlsx"
    )

    # -------------------------------------------------
    # Summary report
    # -------------------------------------------------

    summary = pd.DataFrame({

        "Metric": [

            "Total candidates",

            "Selected candidates",

            "Mean final score",

            "Median final score",

            "Maximum final score",

            "Minimum final score",

            "Mean nearest pharmacy distance (m)",

        ],

        "Value": [

            len(selected),

            len(selected),

            selected["final_score"].mean(),

            selected["final_score"].median(),

            selected["final_score"].max(),

            selected["final_score"].min(),

            selected["nearest_pharmacy_m"].mean(),

        ],

    })

    with pd.ExcelWriter(
        OUTPUT_DIR / "30_spatial_diagnostics.xlsx"
    ) as writer:

        summary.to_excel(
            writer,
            sheet_name="Summary",
            index=False,
        )

        selected.drop(
            columns="geometry",
        ).to_excel(
            writer,
            sheet_name="Candidates",
            index=False,
        )

        corr.to_excel(
            writer,
            sheet_name="Correlation",
        )

    print()
    print("=" * 60)
    print("Diagnostics completed")
    print("=" * 60)

    print()
    print("Saved files:")

    for f in sorted(OUTPUT_DIR.glob("30_*")):
        print(f.name)


if __name__ == "__main__":
    main()    