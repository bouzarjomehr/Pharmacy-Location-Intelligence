from pathlib import Path

import folium
import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

print("="*60)
print("Creating Interactive Map")
print("="*60)

candidates = gpd.read_file(
    ROOT/"data"/"processed"/"best_areas.geojson"
)

facilities = gpd.read_file(
    ROOT/"data"/"processed"/"master_database.geojson"
)

roads = gpd.read_file(
    ROOT/"data"/"processed"/"roads_clean.geojson"
)

roads = roads[["geometry","road_type","road_weight"]].copy()

roads = roads.to_crs(4326)

m = folium.Map(
    location=[31.8974,54.3569],
    zoom_start=13,
    tiles="CartoDB positron"
)

# ---------------- Roads ----------------

road_layer = folium.FeatureGroup(
    name="Roads",
    show=False
)

folium.GeoJson(
    roads,
    style_function=lambda x:{
        "color":"gray",
        "weight":1,
        "opacity":0.4
    }
).add_to(road_layer)

road_layer.add_to(m)

# ---------------- Facilities ----------------

facility_layer = folium.FeatureGroup(
    name="Healthcare"
)

colors = {

    "Doctor":"blue",

    "Clinic":"green",

    "Hospital":"red",

    "Pharmacy":"purple"

}

for _,r in facilities.iterrows():

    folium.CircleMarker(

        [r.geometry.y,r.geometry.x],

        radius=4,

        color=colors.get(r.type,"black"),

        fill=True,

        popup=f"{r['name']}<br>{r['type']}"

    ).add_to(facility_layer)

facility_layer.add_to(m)

# ---------------- Candidates ----------------

candidate_layer = folium.FeatureGroup(
    name="Top 100"
)

max_score = candidates.final_score.max()

for _,r in candidates.iterrows():

    ratio = r.final_score/max_score

    if ratio>0.8:
        color="red"
    elif ratio>0.6:
        color="orange"
    elif ratio>0.4:
        color="yellow"
    else:
        color="green"

    folium.CircleMarker(

        [r.geometry.y,r.geometry.x],

        radius=7,

        color=color,

        fill=True,

        fill_opacity=0.9,

        popup=f"""
        <b>{r.candidate_id}</b><br>
        Score : {r.final_score:.1f}<br>
        Road : {r.road_type}
        """

    ).add_to(candidate_layer)

candidate_layer.add_to(m)

folium.LayerControl().add_to(m)

outfile = ROOT/"outputs"/"best_locations_map.html"

m.save(outfile)

print()
print("Saved:")
print(outfile)