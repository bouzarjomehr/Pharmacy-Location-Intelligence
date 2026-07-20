"""
31_sensitivity_analysis.py

Sensitivity analysis for the Pharmacy Location Intelligence model.

Purpose
-------
Evaluate how robust the selected pharmacy locations are when the
final aggregation weights are perturbed.

Outputs
-------
outputs/
    validation/
        31_sensitivity_results.xlsx
        31_weight_vs_similarity.png
        31_rank_stability.png
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

ROOT = Path(__file__).resolve().parents[1]

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

CONFIG_FILE = (
    ROOT
    / "config"
    / "scoring.json"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "validation"
)


def load_config():

    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def spatial_selection(
    gdf,
    minimum_distance,
    top_n,
):
    """
    Reproduce the greedy spatial filtering used in
    23_select_best_areas.py
    """

    gdf = (
        gdf.sort_values(
            "final_score",
            ascending=False,
        )
        .copy()
    )

    selected = []

    for row in gdf.itertuples():

        keep = True

        for prev in selected:

            if (
                row.geometry.distance(
                    prev.geometry
                )
                < minimum_distance
            ):
                keep = False
                break

        if keep:

            selected.append(row)

        if len(selected) >= top_n:
            break

    return gpd.GeoDataFrame(
        [r._asdict() for r in selected],
        geometry="geometry",
        crs=gdf.crs,
    )

def evaluate_weights(
    gdf,
    prescription_weight,
    competition_weight,
    population_weight,
    road_weight,
    minimum_distance,
    top_n,
):

    tmp = gdf.copy()

    positive_score = (

        tmp["prescription_norm"] * prescription_weight

        + tmp["population_norm"] * population_weight

        + tmp["road_norm"] * road_weight

    )

    competition_penalty = (

        tmp["competition_norm"] * competition_weight

    )

    tmp["final_score"] = positive_score - competition_penalty    

    selected = spatial_selection(
        tmp,
        minimum_distance,
        top_n,
    )

    return selected


def jaccard(a, b):

    a = set(a)

    b = set(b)

    return len(a & b) / len(a | b)


def main():


    print("=" * 70)
    print("Sensitivity Analysis")
    print("=" * 70)

    candidates = (
        gpd.read_file(CANDIDATE_FILE)
        .to_crs(app_config.TARGET_CRS)
    )

    baseline = (
        gpd.read_file(BASELINE_FILE)
        .to_crs(app_config.TARGET_CRS)
    )

    baseline_ids = set(
        baseline["candidate_id"]
    )

    config = load_config()

    cfg = config["normalization"]
    selection_cfg = config["candidate_selection"]

    base_weights = {

        "prescription": cfg["prescription_weight"],
        "competition": cfg["competition_weight"],
        "population": cfg["population_weight"],
        "road": cfg["road_weight"],

    }

    print("\nBaseline weights")

    for k, v in base_weights.items():

        print(f"{k:15s}: {v:.2f}")

    records = []

    variations = []

    for delta in [0.05, 0.10, 0.20]:

        variations.extend([
            ("prescription", +delta),
            ("prescription", -delta),

            ("competition", +delta),
            ("competition", -delta),

            ("population", +delta),
            ("population", -delta),

            ("road", +delta),
            ("road", -delta),
        ])

    for variable, delta in variations:

        weights = base_weights.copy()

        weights[variable] += delta

        # جلوگیری از منفی شدن وزن
        for k in weights:
            weights[k] = max(weights[k], 0.0)            

        selected = evaluate_weights(
            candidates,
            weights["prescription"],
            weights["competition"],
            weights["population"],
            weights["road"],
            selection_cfg["minimum_distance"],
            selection_cfg["top_n"],
        )

        similarity = jaccard(
            baseline_ids,
            selected["candidate_id"],
        )

        mean_score = selected[
            "final_score"
        ].mean()

        records.append({

            "scenario":
                f"{variable} {delta:+.02f}",

            "prescription_weight":
                weights["prescription"],

            "competition_weight":
                weights["competition"],

            "population_weight":
                weights["population"],

            "road_weight":
                weights["road"],

            "jaccard_similarity":
                similarity,

            "changed_locations":
                100 - round(
                    similarity * 100,
                    1,
                ),

            "mean_final_score":
                mean_score,

        })

        print(
            f"{variable:15s}"
            f"{delta:+.02f}"
            f"  Jaccard={similarity:.3f}"
        )

    # -------------------------------------------------
    # Save results
    # -------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = pd.DataFrame(records)

    outfile = (
        OUTPUT_DIR
        / "31_sensitivity_results.xlsx"
    )

    results.to_excel(
        outfile,
        index=False,
    )

    print()
    print("Saved:")
    print(outfile)

    # =====================================================
    # Figure 1
    # Jaccard Similarity
    # =====================================================

    plt.figure(figsize=(9, 4))

    plt.bar(
        results["scenario"],
        results["jaccard_similarity"],
    )

    plt.ylabel("Jaccard Similarity")

    plt.ylim(0, 1)

    plt.xticks(
        rotation=35,
        ha="right",
    )

    plt.tight_layout()

    fig1 = (
        OUTPUT_DIR
        / "31_weight_vs_similarity.png"
    )

    plt.savefig(
        fig1,
        dpi=300,
    )

    plt.close()

    # =====================================================
    # Figure 2
    # Changed locations
    # =====================================================

    plt.figure(figsize=(9, 4))

    plt.bar(
        results["scenario"],
        results["changed_locations"],
    )

    plt.ylabel(
        "Changed Locations (%)"
    )

    plt.xticks(
        rotation=35,
        ha="right",
    )

    plt.tight_layout()

    fig2 = (
        OUTPUT_DIR
        / "31_rank_stability.png"
    )

    plt.savefig(
        fig2,
        dpi=300,
    )

    plt.close()

    print(fig1)
    print(fig2)

    print()

    print("=" * 70)
    print("Sensitivity summary")
    print("=" * 70)

    print(
        results[
            [
                "scenario",
                "jaccard_similarity",
                "changed_locations",
            ]
        ]
        .sort_values(
            "jaccard_similarity",
            ascending=False,
        )
    )


if __name__ == "__main__":
    main()        

        