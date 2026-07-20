from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import xy
from shapely.geometry import Point

import config.app_config as app_config


INPUT_RASTER = (
    app_config.DATA_PROCESSED
    / "population.tif"
)

OUTPUT_FILE = (
    app_config.DATA_PROCESSED
    / "population_heatmap.geojson"
)

OUTPUT_CRS = app_config.OUTPUT_CRS

# -------------------------------------------------
# Keep one pixel every N pixels
# (100 m × 5 = 500 m visualization)
# -------------------------------------------------

DOWNSAMPLE = 5


def main():

    print("=" * 60)
    print("Preparing Population Heatmap")
    print("=" * 60)

    with rasterio.open(INPUT_RASTER) as src:

        arr = src.read(1)

        rows, cols = np.where(arr > 0)

        values = arr[rows, cols]

        # ---------------------------------------------
        # Downsample
        # ---------------------------------------------

        rows = rows[::DOWNSAMPLE]
        cols = cols[::DOWNSAMPLE]
        values = values[::DOWNSAMPLE]

        xs = []
        ys = []

        for r, c in zip(rows, cols):

            x, y = xy(
                src.transform,
                r,
                c,
                offset="center",
            )

            xs.append(x)
            ys.append(y)

        gdf = gpd.GeoDataFrame(

            {

                "population": values,

            },

            geometry=gpd.points_from_xy(
                xs,
                ys,
            ),

            crs=src.crs,

        )

    gdf = gdf.to_crs(OUTPUT_CRS)

    gdf.to_file(
        OUTPUT_FILE,
        driver="GeoJSON",
    )

    print()
    print("=" * 60)
    print("Finished")
    print("=" * 60)

    print(f"Pixels kept : {len(gdf):,}")

    print(
        f"Mean population : "
        f"{gdf.population.mean():.2f}"
    )

    print(
        f"Maximum population : "
        f"{gdf.population.max():.2f}"
    )

    print()

    print("Saved:")

    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()