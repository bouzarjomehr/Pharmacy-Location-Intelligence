"""
Normalize raw scores to 0-100 and apply configurable weights.
"""


import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import json

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "candidate_scores.geojson"
CONFIG_FILE = ROOT / "config" / "scoring.json"

OUTPUT_FILE = ROOT / "data" / "processed" / "candidate_scores.geojson"


def clip_series(series, lower_pct, upper_pct):
    lower = series.quantile(lower_pct / 100)
    upper = series.quantile(upper_pct / 100)
    return series.clip(lower=lower, upper=upper)


def normalize(series):
    mn = series.min()
    mx = series.max()

    if mx == mn:
        return series * 0

    return (series - mn) / (mx - mn) * 100


def main():

    print("=" * 60)
    print("Normalize Candidate Scores")
    print("=" * 60)

    with open(CONFIG_FILE, encoding="utf8") as f:
        settings = json.load(f)

    cfg = settings["normalization"]

    lower_pct = cfg["clip_lower_percentile"]
    upper_pct = cfg["clip_upper_percentile"]

    gdf = gpd.read_file(INPUT_FILE)

    # -------------------------------------------------
    # Robust normalization (Percentile Clipping)
    # -------------------------------------------------

    prescription = normalize(
        clip_series(
            gdf["prescription_score"],
            lower_pct,
            upper_pct,
        )
    )

    competition = normalize(
        clip_series(
            gdf["competition_score"],
            lower_pct,
            upper_pct,
        )
    )

    population = normalize(
        clip_series(
            gdf["population_score"],
            lower_pct,
            upper_pct,
        )
    )

    road = normalize(
        clip_series(
            gdf["road_score"],
            lower_pct,
            upper_pct,
        )
    )

    gdf["prescription_norm"] = prescription
    gdf["competition_norm"] = competition
    gdf["population_norm"] = population
    gdf["road_norm"] = road

    # ----------------------------------------
    # Weighted components (for interpretation)
    # ----------------------------------------

    gdf["prescription_component"] = (
        gdf["prescription_norm"]
        * cfg["prescription_weight"]
    )

    gdf["competition_component"] = (
        gdf["competition_norm"]
        * cfg["competition_weight"]
    )

    gdf["population_component"] = (
        gdf["population_norm"]
        * cfg["population_weight"]
    )

    gdf["road_component"] = (
        gdf["road_norm"]
        * cfg["road_weight"]
    )


    # -------------------------------------------------
    # Final weighted score
    # -------------------------------------------------

    gdf["final_score"] = (

        gdf["prescription_component"]
        - gdf["competition_component"]
        + gdf["population_component"]
        + gdf["road_component"]

    )

    gdf.to_file(
        OUTPUT_FILE,
        driver="GeoJSON",
    )

    print()
    print("Saved:")
    print(OUTPUT_FILE)

    print()
    print(f"Percentile clipping : {lower_pct}% - {upper_pct}%")

    print()

    print(
        gdf[
            [
                "prescription_norm",
                "competition_norm",
                "population_norm",
                "road_norm",
                "final_score",
            ]
        ].describe()
    )


if __name__ == "__main__":
    main()