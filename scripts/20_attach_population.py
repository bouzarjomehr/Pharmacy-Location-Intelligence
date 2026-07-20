from pathlib import Path
import json
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import xy
from scipy.spatial import cKDTree

import config.app_config as app_config


def main():

    print("=" * 60)
    print("Building Candidate Database")
    print("=" * 60)

    # -------------------------------------------------
    # Inputs
    # -------------------------------------------------

    road_points = gpd.read_file(
        app_config.DATA_PROCESSED / "road_points.geojson"
    )

    urban_mask = gpd.read_file(
        app_config.DATA_PROCESSED / "urban_mask.geojson"
    )

    population_raster = (
        app_config.DATA_PROCESSED
        / "population.tif"
    )

    # -------------------------------------------------
    # Keep only points inside urban mask
    # -------------------------------------------------

    candidates = gpd.sjoin(
        road_points,
        urban_mask,
        predicate="within",
        how="inner",
    )

    candidates = candidates.drop(
        columns=["index_right"],
        errors="ignore",
    )

    print()
    print(f"Urban candidates: {len(candidates):,}")

    # -------------------------------------------------
    # Attach population
    #
    # Sum all populated raster cells within the
    # configurable radius around each candidate
    # (population.radius in config/scoring.json).
    # -------------------------------------------------

    with open(
        app_config.CONFIG / "scoring.json",
        encoding="utf8",
    ) as f:
        scoring = json.load(f)

    radius = scoring["population"]["radius"]

    print(f"Population radius : {radius} m")

    with rasterio.open(population_raster) as src:

        arr = src.read(1)

        rows, cols = np.where(arr > 0)

        values = arr[rows, cols].astype(float)

        xs, ys = xy(
            src.transform,
            rows,
            cols,
            offset="center",
        )

        pixels = gpd.GeoDataFrame(
            {"pixel_population": values},
            geometry=gpd.points_from_xy(xs, ys),
            crs=src.crs,
        )

    pixels = pixels.to_crs(app_config.TARGET_CRS)

    candidates = candidates.to_crs(app_config.TARGET_CRS)

    tree = cKDTree(
        np.c_[
            pixels.geometry.x,
            pixels.geometry.y,
        ]
    )

    candidate_xy = np.c_[
        candidates.geometry.x,
        candidates.geometry.y,
    ]

    neighbor_ids = tree.query_ball_point(
        candidate_xy,
        radius,
    )

    pixel_population = pixels["pixel_population"].to_numpy()

    candidates["population"] = [
        float(pixel_population[ids].sum())
        for ids in neighbor_ids
    ]

    # -------------------------------------------------
    # Back to geographic CRS for storage
    # -------------------------------------------------

    candidates = candidates.to_crs(
        app_config.OUTPUT_CRS
    )

    # -------------------------------------------------
    # Candidate IDs
    # -------------------------------------------------

    candidates = candidates.reset_index(drop=True)

    candidates["candidate_id"] = [

        f"C{i:06d}"

        for i in range(
            1,
            len(candidates) + 1,
        )

    ]

    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    geojson_file = (
        app_config.DATA_PROCESSED
        / "candidate_database.geojson"
    )

    excel_file = (
        app_config.DATA_PROCESSED
        / "candidate_database.xlsx"
    )

    candidates.to_file(
        geojson_file,
        driver="GeoJSON",
    )

    (
        candidates
        .drop(columns="geometry")
        .to_excel(
            excel_file,
            index=False,
        )
    )

    print()
    print("=" * 60)
    print("Finished")
    print("=" * 60)

    print(f"Candidates : {len(candidates):,}")
    print(f"Mean population : {candidates.population.mean():.2f}")
    print(f"Max population  : {candidates.population.max():.2f}")

    print()
    print("Saved:")
    print(geojson_file)
    print(excel_file)


if __name__ == "__main__":
    main()