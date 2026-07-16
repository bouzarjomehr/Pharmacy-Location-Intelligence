"""
Project diagnostics.

This script checks the health of the generated datasets
before running further analyses.
"""

from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

FILES = {
    "Facilities": ROOT / "data" / "processed" / "master_database.geojson",
    "Candidates": ROOT / "data" / "processed" / "candidate_database.geojson",
    "Best Areas": ROOT / "data" / "processed" / "best_areas.geojson",
}


def inspect(name, path):

    print("=" * 70)
    print(name)
    print("=" * 70)

    gdf = gpd.read_file(path)

    print(f"Rows          : {len(gdf):,}")
    print(f"CRS           : {gdf.crs}")

    print(f"Duplicates    : {gdf.duplicated().sum():,}")

    print(f"Missing Cells : {gdf.isna().sum().sum():,}")

    if "type" in gdf.columns:

        print("\nFacility Types")

        print(gdf["type"].value_counts())

    if "final_score" in gdf.columns:

        print("\nScore Summary")

        print(gdf["final_score"].describe())

    print()


def main():

    print("=" * 70)
    print("PROJECT DIAGNOSTICS")
    print("=" * 70)
    print()

    for name, path in FILES.items():
        inspect(name, path)


if __name__ == "__main__":
    main()