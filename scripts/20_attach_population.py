from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import geopandas as gpd
import rasterio

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
    # -------------------------------------------------

    with rasterio.open(population_raster) as src:

        candidates = candidates.to_crs(src.crs)

        coords = [
            (geom.x, geom.y)
            for geom in candidates.geometry
        ]

        population = []

        for value in src.sample(coords):

            v = float(value[0])

            if v < 0:
                v = 0

            population.append(v)

    candidates["population"] = population

    # -------------------------------------------------
    # Back to project CRS
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