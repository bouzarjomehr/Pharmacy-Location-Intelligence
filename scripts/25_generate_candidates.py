"""
Generate the final candidate database inside the urban mask.
"""

from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "road_scores_multicriteria.geojson"
URBAN_MASK = ROOT / "data" / "processed" / "urban_mask.geojson"

OUTPUT_GEOJSON = ROOT / "data" / "processed" / "candidate_database.geojson"
OUTPUT_EXCEL = ROOT / "data" / "processed" / "candidate_database.xlsx"

OUTPUT_COLUMNS = [
    "candidate_id",
    "geometry",
    "road_type",
    "road_weight",
    "prescription_score",
    "competition_score",
    "accessibility_score",
    "road_score",
    "final_score",
]


def main():

    print("=" * 60)
    print("Generating Candidate Locations")
    print("=" * 60)

    # -------------------------------------------------
    # Load data
    # -------------------------------------------------

    candidates = gpd.read_file(INPUT_FILE)
    urban_mask = gpd.read_file(URBAN_MASK)

    # -------------------------------------------------
    # Keep only urban candidates
    # -------------------------------------------------

    candidates = gpd.sjoin(
        candidates,
        urban_mask,
        predicate="within",
        how="inner",
    )

    candidates = candidates.drop(
        columns=["index_right"],
        errors="ignore",
    )

    # -------------------------------------------------
    # Rank candidates
    # -------------------------------------------------

    candidates = (
        candidates
        .sort_values(
            "final_score",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    # -------------------------------------------------
    # Generate IDs
    # -------------------------------------------------

    candidates["candidate_id"] = [
        f"C{i:06d}"
        for i in range(1, len(candidates) + 1)
    ]

    candidates = candidates[OUTPUT_COLUMNS]

    # -------------------------------------------------
    # Save outputs
    # -------------------------------------------------

    candidates.to_file(
        OUTPUT_GEOJSON,
        driver="GeoJSON",
    )

    (
        candidates
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
    print(candidates.head())

    print()
    print(f"Total candidates: {len(candidates):,}")


if __name__ == "__main__":
    main()