"""
06_create_smart_candidates.py

Generate candidate points along the road network.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))


import geopandas as gpd
import config.app_config as app_config


ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "processed" / "roads_clean.geojson"
OUTPUT_FILE = ROOT / "data" / "processed" / "road_points.geojson"

TARGET_CRS = app_config.TARGET_CRS
OUTPUT_CRS = app_config.OUTPUT_CRS

# -------------------------------------------------
# Only these road types are considered suitable
# for potential pharmacy locations.
# -------------------------------------------------

VALID_ROAD_TYPES = {

    "trunk",
    "primary",
    "secondary",
    "tertiary",

}


def get_spacing(length: float) -> float:
    """Determine sampling distance based on road length."""

    if length < 100:
        return length + 1

    if length < 250:
        return length / 2

    if length < 500:
        return 125

    if length < 1000:
        return 100

    return 120


def main():

    print("=" * 60)
    print("Creating Smart Candidate Points")
    print("=" * 60)

    roads = (
        gpd.read_file(INPUT_FILE)
        .to_crs(TARGET_CRS)
    )

    print()
    print(f"Road segments before filtering : {len(roads):,}")

    roads = roads[
        roads["road_type"].isin(VALID_ROAD_TYPES)
    ].copy()

    print(f"Road segments after filtering  : {len(roads):,}")

    points = []

    for row in roads.itertuples():

        line = row.geometry

        if line is None:
            continue

        length = line.length

        spacing = get_spacing(length)

        distance = 0

        while distance <= length:

            points.append(
                {
                    "road_type": row.road_type,
                    "road_weight": row.road_weight,
                    "geometry": line.interpolate(distance),
                }
            )

            distance += spacing

        # Always include end point

        points.append(
            {
                "road_type": row.road_type,
                "road_weight": row.road_weight,
                "geometry": line.interpolate(length),
            }
        )

    gdf = gpd.GeoDataFrame(
        points,
        crs=roads.crs,
    )

    # Remove duplicated points (10 cm tolerance)

    gdf["x"] = gdf.geometry.x.round(1)
    gdf["y"] = gdf.geometry.y.round(1)

    gdf = (
        gdf
        .drop_duplicates(subset=["x", "y"])
        .drop(columns=["x", "y"])
        .to_crs(OUTPUT_CRS)
    )

    gdf.to_file(
        OUTPUT_FILE,
        driver="GeoJSON",
    )

    print()
    print("Saved:")
    print(OUTPUT_FILE)

    print()
    print(f"Total Smart Candidates: {len(gdf):,}")


if __name__ == "__main__":
    main()