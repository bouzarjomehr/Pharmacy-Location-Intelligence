"""
Create an interactive map of recommended pharmacy locations.
"""

from pathlib import Path

import folium
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

BEST_AREAS = ROOT / "data" / "processed" / "best_areas.geojson"
MASTER_DATABASE = ROOT / "data" / "processed" / "master_database.geojson"
ROADS = ROOT / "data" / "processed" / "roads_clean.geojson"

OUTPUT_MAP = ROOT / "outputs" / "best_locations_map.html"

MAP_CENTER = [31.8974, 54.3569]
MAP_ZOOM = 13


def main():

    print("=" * 60)
    print("Creating Interactive Map")
    print("=" * 60)

    # -------------------------------------------------
    # Load data
    # -------------------------------------------------

    candidates = gpd.read_file(BEST_AREAS)

    facilities = gpd.read_file(MASTER_DATABASE)

    roads = (
        gpd.read_file(ROADS)[
            [
                "geometry",
                "road_type",
                "road_weight",
            ]
        ]
        .copy()
        .to_crs(4326)
    )

    # -------------------------------------------------
    # Create map
    # -------------------------------------------------

    m = folium.Map(
        location=MAP_CENTER,
        zoom_start=MAP_ZOOM,
        tiles="CartoDB positron",
    )

    # =================================================
    # Roads
    # =================================================

    road_layer = folium.FeatureGroup(
        name="Roads",
        show=False,
    )

    folium.GeoJson(
        roads,
        style_function=lambda _: {
            "color": "#888888",
            "weight": 1,
            "opacity": 0.40,
        },
    ).add_to(road_layer)

    road_layer.add_to(m)

    # =================================================
    # Pharmacies
    # =================================================

    pharmacy_layer = folium.FeatureGroup(
        name="Pharmacies",
        show=True,
    )

    # =================================================
    # Healthcare (Doctors / Clinics / Hospitals)
    # =================================================

    healthcare_layer = folium.FeatureGroup(
        name="Healthcare",
        show=True,
    )

    colors = {
        "Doctor": "#8ecae6",      # Light Blue
        "Clinic": "#219ebc",      # Medium Blue
        "Hospital": "#023047",    # Dark Blue
        "Pharmacy": "#8e44ad",    # Purple
    }

    for facility in facilities.itertuples():

        marker = folium.CircleMarker(
            [facility.geometry.y, facility.geometry.x],
            radius=4,
            color=colors.get(facility.type, "black"),
            fill=True,
            fill_color=colors.get(facility.type, "black"),
            fill_opacity=0.95,
            popup=f"""
            <b>{facility.name}</b><br>
            Type: {facility.type}
            """,
        )

        if facility.type == "Pharmacy":
            marker.add_to(pharmacy_layer)
        else:
            marker.add_to(healthcare_layer)

    pharmacy_layer.add_to(m)
    healthcare_layer.add_to(m)

    # =================================================
    # Recommended Locations
    # =================================================

    candidate_layer = folium.FeatureGroup(
        name="Recommended Pharmacy Locations",
        show=True,
    )

    for idx, candidate in enumerate(candidates.itertuples()):

        if idx < 20:
            color = "#00441b"

        elif idx < 40:
            color = "#1b7837"

        elif idx < 60:
            color = "#5aae61"

        elif idx < 80:
            color = "#a6d96a"

        else:
            color = "#d9f0d3"

        popup = f"""
        <b>{candidate.candidate_id}</b><br>
        <b>Rank:</b> {idx + 1}<br>
        <b>Score:</b> {candidate.final_score:.2f}<br>
        <b>Road:</b> {candidate.road_type}
        """

        folium.CircleMarker(
            [candidate.geometry.y, candidate.geometry.x],
            radius=7,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.95,
            weight=2,
            popup=popup,
        ).add_to(candidate_layer)

    candidate_layer.add_to(m)

    # =================================================
    # Layer Control
    # =================================================

    folium.LayerControl(
        collapsed=False
    ).add_to(m)

    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    m.save(OUTPUT_MAP)

    print()
    print("Saved:")
    print(OUTPUT_MAP)


if __name__ == "__main__":
    main()