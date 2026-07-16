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
        "Pharmacy": "#dd0000",    # Red
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

        popup = folium.Popup(
        f"""
        <div style="width:270px">

        <h4>{candidate.candidate_id}</h4>

        <b>Rank:</b> {idx+1}<br>
        <b>Final Score:</b> {candidate.final_score:.2f}

        <br><br>

        <b>Score Details:</b><br>
        <table style="width:100%">

        <tr>
        <td>Hospital</td>
        <td align="right">{candidate.hospital_score:.1f}</td>
        </tr>

        <tr>
        <td>Clinic</td>
        <td align="right">{candidate.clinic_score:.1f}</td>
        </tr>

        <tr>
        <td>Doctor</td>
        <td align="right">{candidate.doctor_score:.1f}</td>
        </tr>

        <tr>
        <td>Competition</td>
        <td align="right">-{candidate.competition_score:.1f}</td>
        </tr>

        <tr>
        <td>Accessibility</td>
        <td align="right">{candidate.accessibility_score:.1f}</td>
        </tr>

        <tr>
        <td>Road</td>
        <td align="right">{candidate.road_score:.1f}</td>
        </tr>

        </table>

        <br>

        <b>Main Driver:</b>

        {candidate.main_reason.title()}

        <br>

        <b>Road Type:</b>

        {candidate.road_type}

        </div>
        """,
        max_width=320
        )

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
    legend = """
    <div style="
    position: fixed;
    bottom: 30px;
    left: 30px;
    width: 260px;
    z-index:9999;
    background:white;
    padding:12px;
    border:2px solid grey;
    font-size:13px;
    ">

    <b>Recommended Locations</b><br>

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

    </div>
    """

    m.get_root().html.add_child(
        folium.Element(legend)
    )

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