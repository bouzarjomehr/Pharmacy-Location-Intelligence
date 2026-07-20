from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import geopandas as gpd
import rasterio
from rasterio.mask import mask
from shapely.geometry import Point

import config.app_config as app_config


def main():

    print("=" * 60)
    print("Preparing Population Raster")
    print("=" * 60)

    input_raster = (
        app_config.DATA_RAW
        / "GHS_POP_E2030_GLOBE_R2023A_54009_100_V1_0_R6_C23.tif"
    )

    output_raster = (
        app_config.DATA_PROCESSED
        / "population.tif"
    )

    if not input_raster.exists():
        raise FileNotFoundError(input_raster)

    # --------------------------------------------
    # Study Area (Circle)
    # --------------------------------------------

    center = gpd.GeoSeries(
        [Point(app_config.MAP_CENTER[1], app_config.MAP_CENTER[0])],
        crs=app_config.OUTPUT_CRS,
    )

    study_area = (
        center
        .to_crs(app_config.TARGET_CRS)
        .buffer(app_config.STUDY_RADIUS)
    )

    # --------------------------------------------
    # Clip Raster
    # --------------------------------------------

    with rasterio.open(input_raster) as src:

        study_area = study_area.to_crs(src.crs)

        clipped, transform = mask(
            src,
            study_area.geometry,
            crop=True,
        )

        meta = src.meta.copy()

    meta.update(
        {
            "height": clipped.shape[1],
            "width": clipped.shape[2],
            "transform": transform,
        }
    )

    with rasterio.open(
        output_raster,
        "w",
        **meta,
    ) as dst:

        dst.write(clipped)

    # --------------------------------------------
    # Summary
    # --------------------------------------------

    arr = clipped[0]
    arr = arr[arr >= 0]

    print()
    print("Population Raster Prepared")
    print("-" * 60)
    print(f"Shape          : {clipped.shape}")
    print(f"Minimum        : {arr.min():.2f}")
    print(f"Maximum        : {arr.max():.2f}")
    print(f"Mean           : {arr.mean():.2f}")
    print(f"Population Sum : {arr.sum():,.0f}")

    print()
    print("Saved:")
    print(output_raster)


if __name__ == "__main__":
    main()