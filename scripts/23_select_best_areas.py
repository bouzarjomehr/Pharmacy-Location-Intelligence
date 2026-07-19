"""
Select the best candidate locations while enforcing
a minimum distance.
"""

import json
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "candidate_scores.geojson"

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

    candidates = (
        gpd.read_file(INPUT_FILE)
        .to_crs(TARGET_CRS)
        .sort_values(
            "final_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )

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

    selected = (
        gpd.GeoDataFrame(
            selected,
            crs=TARGET_CRS,
        )
        .to_crs(OUTPUT_CRS)
    )

    score_columns = [
        c
        for c in [
            "prescription_component",
            "competition_component",
            "population_component",
            "road_component",
        ]
        if c in selected.columns
    ]    

    if score_columns:

        selected["main_reason"] = (
            selected[score_columns]
            .idxmax(axis=1)
            .str.replace("_score", "", regex=False)
        )

        selected["main_reason"] = (
            selected["main_reason"]
            .str.replace("_component", "", regex=False)
        )        

    else:

        selected["main_reason"] = ""

    def get_value(row, column):

        if column in row.index:
            return row[column]

        return 0

    selected["score_breakdown"] = selected.apply(

        lambda r:

        f"Prescription={get_value(r,'prescription_norm'):.1f}"
        f" | Competition={get_value(r,'competition_norm'):.1f}"
        f" | Population={get_value(r,'population_norm'):.1f}"
        f" | Road={get_value(r,'road_norm'):.1f}",

        axis=1,

    )    


    preferred = [

        "candidate_id",

        "final_score",

        "main_reason",

        "score_breakdown",

        "prescription_component",
        "competition_component",
        "population_component",
        "road_component",        

        "prescription_norm",
        "competition_norm",
        "population_norm",
        "road_norm",

        "prescription_score",
        "competition_score",
        "population_score",
        "road_score",
        "hospital_score",
        "clinic_score",
        "doctor_score",

        "population",

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