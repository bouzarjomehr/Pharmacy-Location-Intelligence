"""
05_prepare_roads.py

Clean and classify the downloaded road network.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import geopandas as gpd

import config.app_config as app_config

KEEP = {
    "motorway": 5,
    "motorway_link": 5,
    "trunk": 5,
    "trunk_link": 5,
    "primary": 4,
    "primary_link": 4,
    "secondary": 3,
    "secondary_link": 3,
    "tertiary": 2,
    "tertiary_link": 2,
    "residential": 1,
    "living_street": 1,
    "unclassified": 1,
    "service": 0.5,
}


def get_type(value):

    if isinstance(value, list):
        for item in value:
            if item in KEEP:
                return item
        return None

    if value in KEEP:
        return value

    return None


def main():

    print("=" * 60)
    print("Preparing Road Network")
    print("=" * 60)

    roads = gpd.read_file(
        app_config.DATA_PROCESSED / "roads.geojson"
    )

    # -------------------------------------------------
    # Keep only supported road categories
    # -------------------------------------------------

    roads["road_type"] = roads["highway"].apply(get_type)

    roads = roads[
        roads["road_type"].notna()
    ].copy()

    roads["road_weight"] = roads["road_type"].map(KEEP)

    roads = roads.to_crs(app_config.TARGET_CRS)

    outfile = (
        app_config.DATA_PROCESSED
        / "roads_clean.geojson"
    )

    roads.to_file(
        outfile,
        driver="GeoJSON",
    )

    print()
    print("Saved:")
    print(outfile)

    print()
    print("Road counts")
    print("-" * 40)
    print(roads["road_type"].value_counts())

    print()
    print(f"Total roads: {len(roads):,}")


if __name__ == "__main__":
    main()