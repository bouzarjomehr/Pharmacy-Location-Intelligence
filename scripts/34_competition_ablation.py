"""
34_competition_ablation.py

Competition Ablation Analysis

Goal
----
Evaluate the impact of removing the competition penalty
from the scoring model.

Outputs
-------
outputs/
    validation/
        34_competition_ablation_summary.xlsx
        34_overlap_existing_pharmacies.png
        34_candidate_overlap.xlsx
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import json

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

import config.app_config as app_config
from scripts.phase3_engine import (
    calculate_final_score,
    spatial_selection,
)

ROOT = Path(__file__).resolve().parents[1]

CONFIG_FILE = ROOT / "config" / "scoring.json"

CANDIDATE_FILE = (
    ROOT
    / "data"
    / "processed"
    / "candidate_scores.geojson"
)

BASELINE_FILE = (
    ROOT
    / "data"
    / "processed"
    / "best_areas.geojson"
)

PHARMACY_FILE = (
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


def load_config():

    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def jaccard(a, b):

    a = set(a)
    b = set(b)

    return len(a & b) / len(a | b)


def nearest_distance_to_existing(
    candidates,
    pharmacies,
):

    pharmacy_union = pharmacies.geometry.union_all()

    return candidates.geometry.apply(
        lambda g: g.distance(pharmacy_union)
    )

def evaluate_without_competition(
    gdf,
    prescription_weight,
    population_weight,
    road_weight,
    minimum_distance,
    top_n,
):
    """
    Recalculate final score while removing
    the competition penalty completely.
    """

    tmp = gdf.copy()

    tmp["final_score"] = (

        tmp["prescription_norm"] * prescription_weight

        + tmp["population_norm"] * population_weight

        + tmp["road_norm"] * road_weight

    )

    selected = spatial_selection(
        tmp,
        minimum_distance,
        top_n,
    )

    return selected


def nearest_distance(
    source,
    target,
):
    """
    Distance from each geometry in source
    to nearest geometry in target.
    """

    target_union = target.unary_union

    return source.geometry.apply(
        lambda g: g.distance(target_union)
    )


def jaccard(
    a,
    b,
):

    a = set(a)

    b = set(b)

    return len(a & b) / len(a | b)

def main():

    print("=" * 70)
    print("Competition Ablation Analysis")
    print("=" * 70)

    config = load_config()

    norm_cfg = config["normalization"]
    sel_cfg = config["candidate_selection"]

    candidates = (
        gpd.read_file(CANDIDATE_FILE)
        .to_crs(app_config.TARGET_CRS)
    )

    baseline = (
        gpd.read_file(BASELINE_FILE)
        .to_crs(app_config.TARGET_CRS)
    )

    pharmacies = (
        gpd.read_file(PHARMACY_FILE)
        .to_crs(app_config.TARGET_CRS)
    )

    pharmacies = pharmacies[
        pharmacies["type"] == "Pharmacy"
    ].copy()

    # ==========================================================
    # Run model WITHOUT competition penalty
    # ==========================================================

    selected = evaluate_without_competition(
        candidates,
        prescription_weight=norm_cfg["prescription_weight"],
        population_weight=norm_cfg["population_weight"],
        road_weight=norm_cfg["road_weight"],
        minimum_distance=sel_cfg["minimum_distance"],
        top_n=sel_cfg["top_n"],
    )

    baseline_ids = set(baseline["candidate_id"])
    selected_ids = set(selected["candidate_id"])

    jaccard_score = jaccard(
        baseline_ids,
        selected_ids,
    )

    print()
    print(f"Jaccard similarity = {jaccard_score:.3f}")

    # ==========================================================
    # Distance to nearest existing pharmacy
    # ==========================================================

    selected["nearest_existing_m"] = nearest_distance(
        selected,
        pharmacies,
    )

    distance_stats = (
        selected["nearest_existing_m"]
        .describe()
        .rename("Distance")
    )

    print()
    print(distance_stats)

    # ==========================================================
    # Overlap thresholds
    # ==========================================================

    thresholds = [
        250,
        500,
        750,
        1000,
    ]

    overlap_records = []

    for th in thresholds:

        count = (
            selected["nearest_existing_m"]
            <= th
        ).sum()

        overlap_records.append({

            "threshold_m": th,

            "count": count,

            "percent":
                count
                / len(selected)
                * 100,

        })

    overlap_df = pd.DataFrame(
        overlap_records
    )

    print()
    print(overlap_df)

    # ==========================================================
    # Save tables
    # ==========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    summary = pd.DataFrame({

        "Metric": [

            "Selected candidates",

            "Jaccard similarity",

            "Mean distance (m)",

            "Median distance (m)",

            "Min distance (m)",

            "Max distance (m)",

        ],

        "Value": [

            len(selected),

            jaccard_score,

            selected["nearest_existing_m"].mean(),

            selected["nearest_existing_m"].median(),

            selected["nearest_existing_m"].min(),

            selected["nearest_existing_m"].max(),

        ],

    })

    summary_file = (
        OUTPUT_DIR
        / "34_competition_ablation_summary.xlsx"
    )

    overlap_file = (
        OUTPUT_DIR
        / "34_candidate_overlap.xlsx"
    )

    summary.to_excel(
        summary_file,
        index=False,
    )

    overlap_df.to_excel(
        overlap_file,
        index=False,
    )

    # ==========================================================
    # Figure 1
    # Existing Pharmacy Overlap
    # ==========================================================

    plt.figure(figsize=(7, 4))

    plt.bar(
        overlap_df["threshold_m"].astype(str),
        overlap_df["percent"],
    )

    plt.ylabel("Overlap (%)")

    plt.xlabel("Distance threshold (m)")

    plt.title(
        "Candidate overlap with existing pharmacies"
    )

    plt.tight_layout()

    fig1 = (
        OUTPUT_DIR
        / "34_overlap_existing_pharmacies.png"
    )

    plt.savefig(
        fig1,
        dpi=300,
    )

    plt.close()


    # ==========================================================
    # Figure 2
    # Distance Histogram
    # ==========================================================

    plt.figure(figsize=(7, 4))

    plt.hist(
        selected["nearest_existing_m"],
        bins=20,
    )

    plt.xlabel(
        "Distance to nearest existing pharmacy (m)"
    )

    plt.ylabel("Frequency")

    plt.tight_layout()

    fig2 = (
        OUTPUT_DIR
        / "34_distance_distribution.png"
    )

    plt.savefig(
        fig2,
        dpi=300,
    )

    plt.close()


    # ==========================================================
    # Save selected candidates
    # ==========================================================

    selected_file = (
        OUTPUT_DIR
        / "34_selected_without_competition.xlsx"
    )

    (
        selected
        .drop(columns="geometry")
        .to_excel(
            selected_file,
            index=False,
        )
    )

    print()
    print("Saved:")
    print(summary_file)
    print(overlap_file)
    print(selected_file)
    print(fig1)
    print(fig2)

    print()

    print("=" * 70)
    print("Competition Ablation Summary")
    print("=" * 70)

    print(summary)

    print()

    print("Overlap table")
    print(overlap_df)

    print()
    print("Finished.")
    
if __name__ == "__main__":
    main()