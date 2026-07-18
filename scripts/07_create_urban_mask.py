"""
24_create_urban_mask.py

Create a continuous urban mask from the road network.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon

import config.app_config as app_config


BUFFER_DISTANCE = 120      # meters
MIN_HOLE_AREA = 5000       # m²


def remove_small_holes(geometry, min_area):
    """
    Remove interior holes smaller than min_area.
    """

    if geometry.is_empty:
        return geometry

    if isinstance(geometry, Polygon):

        holes = [
            ring
            for ring in geometry.interiors
            if Polygon(ring).area >= min_area
        ]

        return Polygon(
            geometry.exterior,
            holes,
        )

    if isinstance(geometry, MultiPolygon):

        return MultiPolygon(
            [
                remove_small_holes(
                    poly,
                    min_area,
                )
                for poly in geometry.geoms
            ]
        )

    return geometry


def main():

    print("=" * 60)
    print("Creating Urban Mask")
    print("=" * 60)

    roads = (
        gpd.read_file(
            app_config.DATA_PROCESSED / "roads_clean.geojson"
        )
        .to_crs(app_config.TARGET_CRS)
    )

    urban = roads[
        roads.road_type.isin(
            [
                "residential",
                "tertiary",
                "secondary",
                "primary",
                "service",
                "living_street",
                "unclassified",
            ]
        )
    ].copy()

    # -------------------------------------------------
    # Create road buffers
    # -------------------------------------------------

    urban["geometry"] = urban.buffer(BUFFER_DISTANCE)

    # -------------------------------------------------
    # Merge all polygons
    # -------------------------------------------------

    urban_mask = urban[["geometry"]].dissolve()

    # -------------------------------------------------
    # Repair topology
    # -------------------------------------------------

    urban_mask["geometry"] = urban_mask.buffer(0)

    # -------------------------------------------------
    # Remove small interior holes
    # -------------------------------------------------

    urban_mask["geometry"] = urban_mask.geometry.apply(
        lambda geom: remove_small_holes(
            geom,
            MIN_HOLE_AREA,
        )
    )

    urban_mask = urban_mask.to_crs(4326)

    output_file = (
        app_config.DATA_PROCESSED
        / "urban_mask.geojson"
    )

    urban_mask.to_file(
        output_file,
        driver="GeoJSON",
    )

    print()
    print("Saved:")
    print(output_file)


if __name__ == "__main__":
    main()