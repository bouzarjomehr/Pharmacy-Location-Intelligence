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

    outfile = app_config.DATA_PROCESSED / "roads.geojson"

    # -------------------------------------------------
    # Use cached file if available
    # -------------------------------------------------

    if outfile.exists():

        print("Road network already exists.")
        print("Skipping download.")

        roads = gpd.read_file(outfile)

    else:

        tags = {
            "highway": True,
        }

        roads = ox.features_from_point(
            app_config.MAP_CENTER,
            tags=tags,
            dist=18000,
        )

        roads = roads[
            roads.geometry.type.isin(
                [
                    "LineString",
                    "MultiLineString",
                ]
            )
        ].copy()

        roads = roads.to_crs(app_config.TARGET_CRS)

        roads.to_file(
            outfile,
            driver="GeoJSON",
        )

        print()
        print("Saved:")
        print(outfile)

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