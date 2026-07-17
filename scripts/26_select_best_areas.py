"""
Select the best candidate locations while enforcing
a minimum distance.
"""
import json
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "candidate_database.geojson"
CONFIG_FILE = ROOT / "config" / "scoring.json"
OUTPUT_GEOJSON = ROOT / "data" / "processed" / "best_areas.geojson"
OUTPUT_EXCEL = ROOT / "data" / "processed" / "best_areas.xlsx"

TARGET_CRS = 32640
OUTPUT_CRS = 4326


def main():

    with open(CONFIG_FILE, encoding="utf8") as f:
        settings = json.load(f)

    MIN_DISTANCE = settings["candidate_selection"]["minimum_distance"]
    TOP_N = settings["candidate_selection"]["top_n"]

    print("=" * 60)
    print("Selecting Best Areas")
    print("=" * 60)

    print()
    print(f"Minimum spacing : {MIN_DISTANCE} m")
    print(f"Top candidates  : {TOP_N}")
    print()

    # -------------------------------------------------
    # Load candidates
    # -------------------------------------------------

    candidates = (
        gpd.read_file(INPUT_FILE)
        .to_crs(TARGET_CRS)
        .sort_values(
            "final_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    # -------------------------------------------------
    # Greedy spatial selection
    # -------------------------------------------------

    selected = []

    while len(candidates) > 0 and len(selected) < TOP_N:

        best = candidates.iloc[0]

        selected.append(best)

        distances = candidates.distance(best.geometry)

        candidates = (
            candidates.loc[
                distances > MIN_DISTANCE
            ]
            .reset_index(drop=True)
        )

    selected = gpd.GeoDataFrame(
        selected,
        crs=TARGET_CRS,
    ).to_crs(OUTPUT_CRS)

    # -------------------------------------------------
    # Main score component
    # -------------------------------------------------

    score_columns = [
        c for c in [
            "hospital_score",
            "clinic_score",
            "doctor_score",
            "road_score",
            "accessibility_score",
        ]
        if c in selected.columns
    ]

    if score_columns:

        selected["main_reason"] = (
            selected[score_columns]
            .idxmax(axis=1)
            .str.replace("_score", "", regex=False)
        )

    else:

        selected["main_reason"] = ""

    # -------------------------------------------------
    # Human readable score explanation
    # -------------------------------------------------

    def get_value(row, column):

        if column in row.index:
            return row[column]
        return 0

    selected["score_breakdown"] = selected.apply(

        lambda r:

        f"H={get_value(r,'hospital_score'):.1f}"
        f" | C={get_value(r,'clinic_score'):.1f}"
        f" | D={get_value(r,'doctor_score'):.1f}"
        f" | P=-{get_value(r,'competition_score'):.1f}"
        f" | A={get_value(r,'accessibility_score'):.1f}"
        f" | R={get_value(r,'road_score'):.1f}",

        axis=1

    )

    # -------------------------------------------------
    # Put important columns first
    # -------------------------------------------------

    preferred = [

        "candidate_id",

        "final_score",

        "main_reason",

        "score_breakdown",

        "hospital_score",

        "clinic_score",

        "doctor_score",

        "competition_score",

        "accessibility_score",

        "road_score",

        "road_type",

        "road_weight",

    ]

    existing = [

        c

        for c in preferred

        if c in selected.columns

    ]

    remaining = [

        c

        for c in selected.columns

        if c not in existing + ["geometry"]

    ]

    selected = selected[
        existing + remaining + ["geometry"]
    ]

    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    selected.to_file(
        OUTPUT_GEOJSON,
        driver="GeoJSON",
    )

    (
        selected
        .drop(columns="geometry")
        .to_excel(
            OUTPUT_EXCEL,
            index=False,
        )
    )

    print()
    print("Saved:")
    print(OUTPUT_GEOJSON)
    print(OUTPUT_EXCEL)

    print()

    print(

        selected.head(20)[

            [

                c

                for c in [

                    "candidate_id",

                    "final_score",

                    "main_reason",

                    "score_breakdown",

                ]

                if c in selected.columns

            ]

        ]

    )

    print()

    print(f"Selected : {len(selected)}")


if __name__ == "__main__":
    main()