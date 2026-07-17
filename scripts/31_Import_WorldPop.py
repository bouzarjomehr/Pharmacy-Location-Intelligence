"""
31_import_worldpop.py

Download WorldPop for Iran (once),
clip to the study area,
and save a local raster for Yazd.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import requests
import geopandas as gpd
import rasterio
from rasterio.mask import mask

import config.app_config as app_config


WORLDPOP_URL = (
    "https://data.worldpop.org/GIS/Population/Global_2000_2020/"
    "2020/IRN/irn_ppp_2020_UNadj.tif"
)

RAW_RASTER = app_config.DATA_RAW / "worldpop_iran_2020.tif"

BOUNDARY = app_config.DATA_RAW / "study_area_boundary.geojson"

OUTPUT = app_config.DATA_PROCESSED / "worldpop_yazd.tif"


def download_file(url, outfile):

    print("Downloading WorldPop...")

    response = requests.get(
        url,
        stream=True,
        timeout=120,
    )

    response.raise_for_status()

    with open(outfile, "wb") as f:

        for chunk in response.iter_content(1024 * 1024):

            if chunk:
                f.write(chunk)

    print("Download completed.")


def main():

    print("=" * 60)
    print("Importing WorldPop")
    print("=" * 60)

    # ------------------------------------------
    # Already prepared
    # ------------------------------------------

    if OUTPUT.exists():

        print()
        print("Clipped raster already exists.")
        print(OUTPUT)

        return

    # ------------------------------------------
    # Download Iran raster once
    # ------------------------------------------

    if not RAW_RASTER.exists():

        download_file(
            WORLDPOP_URL,
            RAW_RASTER,
        )

    else:

        print("Using existing Iran raster.")

    # ------------------------------------------
    # Read study boundary
    # ------------------------------------------

    boundary = gpd.read_file(BOUNDARY)

    # ------------------------------------------
    # Clip
    # ------------------------------------------

    with rasterio.open(RAW_RASTER) as src:

        boundary = boundary.to_crs(src.crs)

        clipped, transform = mask(
            src,
            boundary.geometry,
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
        OUTPUT,
        "w",
        **meta,
    ) as dst:

        dst.write(clipped)

    valid = clipped[0]
    valid = valid[valid >= 0]

    print()
    print("Saved:")
    print(OUTPUT)

    print()
    print("Raster summary")
    print("-" * 40)
    print(f"Shape : {clipped.shape}")
    print(f"Min   : {valid.min():.3f}")
    print(f"Max   : {valid.max():.3f}")
    print(f"Mean  : {valid.mean():.3f}")
    print(f"Total : {valid.sum():,.0f}")


if __name__ == "__main__":
    main()