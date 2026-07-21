"""
phase3_engine.py

Shared utility functions for Phase 3 validation analyses.

This module intentionally contains only the minimum functionality
required by the validation scripts.

Current utilities
-----------------
- calculate_final_score()
- spatial_selection()
"""

from __future__ import annotations

import geopandas as gpd


# ==========================================================
# Final score calculation
# ==========================================================

def calculate_final_score(
    gdf: gpd.GeoDataFrame,
    prescription_weight: float,
    competition_weight: float,
    population_weight: float,
    road_weight: float,
) -> gpd.GeoDataFrame:
    """
    Recalculate the weighted final score.

    Notes
    -----
    Competition is a penalty and is therefore subtracted.

    Returns
    -------
    GeoDataFrame
        Copy of the input dataframe with an updated
        'final_score' column.
    """

    result = gdf.copy()

    result["final_score"] = (

        result["prescription_norm"] * prescription_weight

        - result["competition_norm"] * competition_weight

        + result["population_norm"] * population_weight

        + result["road_norm"] * road_weight

    )

    return result


# ==========================================================
# Greedy spatial selection
# ==========================================================

def spatial_selection(
    gdf: gpd.GeoDataFrame,
    minimum_distance: float,
    top_n: int,
) -> gpd.GeoDataFrame:
    """
    Greedy spatial filtering identical to Phase 2.

    Parameters
    ----------
    gdf
        Candidate dataframe containing a 'final_score' column.

    minimum_distance
        Minimum spacing between selected candidates (meters).

    top_n
        Maximum number of selected candidates.

    Returns
    -------
    GeoDataFrame
        Selected candidate locations.
    """

    candidates = (

        gdf.sort_values(
            "final_score",
            ascending=False,
        )

        .reset_index(drop=True)

        .copy()

    )

    selected = []

    while (

        len(candidates) > 0

        and len(selected) < top_n

    ):

        best = candidates.iloc[0]

        selected.append(best)

        distances = candidates.distance(best.geometry)

        candidates = (

            candidates.loc[
                distances > minimum_distance
            ]

            .reset_index(drop=True)

        )

    return gpd.GeoDataFrame(
        selected,
        geometry="geometry",
        crs=gdf.crs,
    )