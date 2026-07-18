"""
Prepare the master healthcare database.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import geopandas as gpd

import config.app_config as app_config


def main():

    print("=" * 60)
    print("Preparing Master Database")
    print("=" * 60)

    # -------------------------------------------------
    # Load
    # -------------------------------------------------

    input_file = (
        app_config.DATA_PROCESSED
        / "google_healthcare_clean.geojson"
    )

    gdf = gpd.read_file(input_file)

    # -------------------------------------------------
    # Standardize columns
    # -------------------------------------------------

    columns = {
        "google_id": "id",
        "name": "name",
        "type": "type",
        "lat": "lat",
        "lon": "lon",
        "rating": "rating",
        "reviews": "reviews",
        "address": "address",
        "phone": "phone",
        "website": "website",
    }

    gdf = gdf[list(columns.keys()) + ["geometry"]]
    gdf = gdf.rename(columns=columns)

    # -------------------------------------------------
    # Placeholder fields for future extensions
    # -------------------------------------------------

    gdf["score"] = 0.0
    gdf["weight"] = 0.0
    gdf["specialty"] = ""
    gdf["population"] = None
    gdf["nearest_pharmacy"] = None
    gdf["nearest_hospital"] = None
    gdf["nearest_doctor"] = None

    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    out_geo = (
        app_config.DATA_PROCESSED
        / "master_database.geojson"
    )

    out_xlsx = (
        app_config.DATA_PROCESSED
        / "master_database.xlsx"
    )

    gdf.to_file(
        out_geo,
        driver="GeoJSON",
    )

    (
        gdf
        .drop(columns="geometry")
        .to_excel(
            out_xlsx,
            index=False,
        )
    )

    print()
    print("Saved:")
    print(out_geo)
    print(out_xlsx)

    print()
    print(gdf.head())

    print()
    print(f"Total records: {len(gdf):,}")


if __name__ == "__main__":
    main()