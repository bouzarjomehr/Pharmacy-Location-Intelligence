from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import geopandas as gpd
import osmnx as ox

import config.app_config as app_config


def main():

    print("=" * 60)
    print("Downloading Road Network")
    print("=" * 60)

    # ---------- RAW ----------
    raw_file = app_config.DATA_RAW / "roads.geojson"

    # ---------- PROCESSED ----------
    processed_file = app_config.DATA_PROCESSED / "roads.geojson"

    # -------------------------------------------------
    # Use cached RAW file if available
    # -------------------------------------------------

    if raw_file.exists():

        print("Road network already exists (RAW).")
        print("Skipping download.")

        roads = gpd.read_file(raw_file)

    else:

        tags = {
            "highway": True,
        }

        roads = ox.features_from_point(
            app_config.MAP_CENTER,
            tags=tags,
            dist=app_config.STUDY_RADIUS,
        )

        roads = roads[
            roads.geometry.type.isin(
                [
                    "LineString",
                    "MultiLineString",
                ]
            )
        ].copy()

        roads.to_file(
            raw_file,
            driver="GeoJSON",
        )

        print()
        print("Saved RAW:")
        print(raw_file)

    # -------------------------------------------------
    # Prepare processed version
    # -------------------------------------------------

    roads = roads.to_crs(app_config.TARGET_CRS)

    roads.to_file(
        processed_file,
        driver="GeoJSON",
    )

    print()
    print("Saved PROCESSED:")
    print(processed_file)

    print()
    print("Highway types:")

    print(
        roads["highway"]
        .explode()
        .value_counts()
        .head(30)
    )


if __name__ == "__main__":
    main()