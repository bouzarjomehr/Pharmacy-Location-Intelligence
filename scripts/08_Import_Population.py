from pathlib import Path
import sys
import requests
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import config.app_config as app_config

# --------------------------------------------------
# GHSL Tile
# --------------------------------------------------

GHSL_TILE = "GHS_POP_E2030_GLOBE_R2023A_54009_100_V1_0_R6_C23"

GHSL_URL = (
    "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/"
    "GHSL/GHS_POP_GLOBE_R2023A/"
    "GHS_POP_E2030_GLOBE_R2023A_54009_100/"
    "V1-0/tiles/"
    f"{GHSL_TILE}.zip"
)

ZIP_FILE = app_config.DATA_RAW / f"{GHSL_TILE}.zip"

TIF_FILE = app_config.DATA_RAW / f"{GHSL_TILE}.tif"


def download_file(url, destination):

    response = requests.get(url, stream=True)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(destination, "wb") as f:

        for chunk in response.iter_content(chunk_size=1024 * 1024):

            if not chunk:
                continue

            f.write(chunk)

            downloaded += len(chunk)

            if total > 0:

                percent = downloaded / total * 100

                print(
                    f"\rDownloading: {percent:5.1f}%",
                    end="",
                    flush=True,
                )

    print()


def main():

    print("=" * 60)
    print("Preparing GHSL Population Dataset")
    print("=" * 60)

    if TIF_FILE.exists():

        print("\nGHSL raster already exists.")
        print(TIF_FILE)
        return

    if not ZIP_FILE.exists():

        print("\nDownloading GHSL tile...\n")

        download_file(
            GHSL_URL,
            ZIP_FILE,
        )

    else:

        print("\nZIP file already exists.")

    print("\nExtracting...")

    with zipfile.ZipFile(ZIP_FILE) as z:

        z.extractall(app_config.DATA_RAW)

    if not TIF_FILE.exists():

        raise RuntimeError(
            "Raster was not extracted correctly."
        )

    print("\nFinished.")
    print(TIF_FILE)


if __name__ == "__main__":
    main()