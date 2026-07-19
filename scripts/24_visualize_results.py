"""
Create an interactive map of recommended pharmacy locations.
"""

from pathlib import Path

import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import HeatMap

ROOT = Path(__file__).resolve().parents[1]

BEST_AREAS = ROOT / "data" / "processed" / "best_areas.geojson"

MASTER_DATABASE = (
    ROOT
    / "data"
    / "processed"
    / "master_database.geojson"
)

ROADS = (
    ROOT
    / "data"
    / "processed"
    / "roads_clean.geojson"
)

POPULATION = (
    ROOT
    / "data"
    / "processed"
    / "population_heatmap.geojson"
)

OUTPUT_MAP = (
    ROOT
    / "outputs"
    / "PLI_candidate_locations_map.html"
)

MAP_CENTER = [31.8974, 54.3569]
MAP_ZOOM = 13


def main():

    print("=" * 60)
    print("Creating Interactive Map")
    print("=" * 60)

    # -------------------------------------------------
    # Load datasets
    # -------------------------------------------------

    candidates = gpd.read_file(BEST_AREAS)

    facilities = gpd.read_file(
        MASTER_DATABASE
    )

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

    population = (
        gpd.read_file(
            POPULATION
        )
        .to_crs(4326)
    )

    # -------------------------------------------------
    # Create base map
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
        name="Road Network",
        show=False,
    )

    folium.GeoJson(
        roads,
        style_function=lambda _: {
            "color": "#808080",
            "weight": 1,
            "opacity": 0.40,
        },
    ).add_to(road_layer)

    road_layer.add_to(m)

    # =================================================
    # Population Heatmap
    # =================================================

    population_layer = folium.FeatureGroup(
        name="Population Density",
        show=False,
    )

    heat_data = [
        [
            row.geometry.y,
            row.geometry.x,
            row.population
        ]
        for row in population.itertuples()
        if row.population > 0
    ]

    HeatMap(
        heat_data,
        radius=18,
        blur=15,
        min_opacity=0.20,
        max_zoom=18,
    ).add_to(population_layer)

    population_layer.add_to(m)

    # =================================================
    # Pharmacies
    # =================================================

    pharmacy_layer = folium.FeatureGroup(
        name="Existing Pharmacies",
        show=True,
    )

    # =================================================
    # Healthcare
    # =================================================

    healthcare_layer = folium.FeatureGroup(
        name="Healthcare Facilities",
        show=True,
    )

    colors = {

        "Doctor": "#8ecae6",

        "Clinic": "#219ebc",

        "Hospital": "#023047",

        "Pharmacy": "#dd0000",

    }

    for facility in facilities.itertuples():

        popup = folium.Popup(
            f"""
            <b>{facility.name}</b><br>

            Type : {facility.type}
            """,
            max_width=250,
        )

        marker = folium.CircleMarker(
            [
                facility.geometry.y,
                facility.geometry.x,
            ],
            radius=4,
            color=colors.get(
                facility.type,
                "black",
            ),
            fill=True,
            fill_color=colors.get(
                facility.type,
                "black",
            ),
            fill_opacity=0.95,
            popup=popup,
        )

        if facility.type == "Pharmacy":

            marker.add_to(
                pharmacy_layer
            )

        else:

            marker.add_to(
                healthcare_layer
            )

    pharmacy_layer.add_to(m)

    healthcare_layer.add_to(m)

    # =================================================
    # Recommended Locations
    # =================================================

    candidate_layer = folium.FeatureGroup(
        name="Recommended Pharmacy Locations",
        show=True,
    )

    # =================================================
    # Recommended Candidate Locations
    # =================================================

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

        popup = folium.Popup(
            f"""
            <div style="width:320px">

            <h4>{candidate.candidate_id}</h4>

            <b>Rank:</b> {idx+1}<br>
            <b>Final Weighted Score:</b> {candidate.final_score:.2f}

            <hr>

            <table style="width:100%;font-size:13px">

            <tr><td><b>Score Details (0-100):</b></td></tr>

            <tr>
                <td>Prescription Score</td>
                <td align="right"><b>{candidate.prescription_norm:.1f}</b></td>
            </tr>

            <tr>
                <td>Competition Penalty</td>
                <td align="right">-{candidate.competition_norm:.1f}</td>
            </tr>

            <tr>
                <td>Road Score</td>
                <td align="right">{candidate.road_norm:.1f}</td>
            </tr>

            <tr>
                <td>Population Score</td>
                <td align="right">{candidate.population_norm:.1f}</td>
            </tr>

            </table>

            <hr>

            <b>Main Driver:</b>
            {candidate.main_reason}<br>

            <b>Road Type:</b>
            {candidate.road_type}<br>

            <b>Population (n):</b>
            {candidate.population}<br>

            <hr>

            <b>Raw Values</b><br>

            Prescription:
            {candidate.prescription_score:.1f}<br>

            Competition:
            {candidate.competition_score:.1f}<br>

            Population:
            {candidate.population_score:.1f}<br>

            Road:
            {candidate.road_score:.1f}            

            <br>            
            
            </div>
            """,
            max_width=360,
        )

        folium.CircleMarker(
            [
                candidate.geometry.y,
                candidate.geometry.x,
            ],
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
    # Legend
    # =================================================

    legend = """
    <div style="
        position: fixed;
        bottom: 25px;
        left: 25px;
        width: 285px;
        background:white;
        border:2px solid gray;
        z-index:9999;
        padding:12px;
        font-size:13px;
    ">

    <b>Recommended Pharmacy Locations</b><br>

    <span style="color:#00441b;">●</span> Rank 1–20<br>
    <span style="color:#1b7837;">●</span> Rank 21–40<br>
    <span style="color:#5aae61;">●</span> Rank 41–60<br>
    <span style="color:#a6d96a;">●</span> Rank 61–80<br>
    <span style="color:#d9f0d3;">●</span> Rank 81–100

    <hr>

    <b>Healthcare Facilities</b><br>

    <span style="color:#023047;">●</span> Hospital<br>
    <span style="color:#219ebc;">●</span> Clinic<br>
    <span style="color:#8ecae6;">●</span> Doctor<br>
    <span style="color:#dd0000;">●</span> Pharmacy

    <hr>

    Heatmap = Population Density

    </div>
    """

    m.get_root().html.add_child(
        folium.Element(legend)
    )

    # =================================================
    # Layer Control
    # =================================================

    folium.LayerControl(
        collapsed=False
    ).add_to(m)

    # -------------------------------------------------
    # Save
    # -------------------------------------------------

    OUTPUT_MAP.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    m.save(OUTPUT_MAP)

    print()
    print("Saved:")
    print(OUTPUT_MAP)


if __name__ == "__main__":
    main()