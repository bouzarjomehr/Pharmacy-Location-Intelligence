from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import geopandas as gpd
import pandas as pd

import config.app_config as app_config


def main():

    print("=" * 60)
    print("Cleaning Google Healthcare Database")
    print("=" * 60)

    input_file = app_config.DATA_PROCESSED / "google_healthcare.geojson"

    gdf = gpd.read_file(input_file)

    print(f"\nLoaded: {len(gdf):,}")

    # -------------------------------------------------
    # Remove empty names
    # -------------------------------------------------

    gdf["name"] = (
        gdf["name"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    gdf = gdf[gdf["name"] != ""].copy()

    print(f"After removing empty names: {len(gdf):,}")

    # -------------------------------------------------
    # Remove duplicates
    # -------------------------------------------------

    gdf = (
        gdf
        .drop_duplicates(
            subset=["name", "lat", "lon"]
        )
        .copy()
    )

    print(f"After duplicate removal: {len(gdf):,}")

    # -------------------------------------------------
    # Sort
    # -------------------------------------------------

    gdf = (
        gdf
        .sort_values(
            by=["type", "name"]
        )
        .reset_index(drop=True)
    )

    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    output_geojson = (
        app_config.DATA_PROCESSED
        / "google_healthcare_clean.geojson"
    )

    output_excel = (
        app_config.DATA_PROCESSED
        / "google_healthcare_clean.xlsx"
    )

    gdf.to_file(
        output_geojson,
        driver="GeoJSON",
    )

    (
        gdf
        .drop(columns="geometry")
        .to_excel(
            output_excel,
            index=False,
        )
    )

    print("\nSaved:")
    print(output_geojson)
    print(output_excel)

    print("\nCounts:")
    print(gdf["type"].value_counts())


if __name__ == "__main__":
    main()