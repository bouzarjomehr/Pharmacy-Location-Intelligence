"""
Select the best candidate locations while enforcing a minimum distance.
"""

from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "candidate_database.geojson"

OUTPUT_GEOJSON = ROOT / "data" / "processed" / "best_areas.geojson"
OUTPUT_EXCEL = ROOT / "data" / "processed" / "best_areas.xlsx"

TARGET_CRS = 32640
OUTPUT_CRS = 4326

MIN_DISTANCE = 250      # meters
TOP_N = 100


def main():

    print("=" * 60)
    print("Selecting Best Areas")
    print("=" * 60)

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

    selected = gpd.GeoDataFrame(
        selected,
        crs=TARGET_CRS,
    )

    selected = selected.to_crs(OUTPUT_CRS)

    # -------------------------------------------------
    # Save outputs
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
        selected[
            [
                "candidate_id",
                "road_type",
                "final_score",
            ]
        ].head(20)
    )

    print()
    print(f"Selected: {len(selected)}")


if __name__ == "__main__":
    main()