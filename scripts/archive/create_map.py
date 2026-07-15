from pathlib import Path
import sys

import folium
import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

# ----------------------------

gdf = gpd.read_file(config.DATA_RAW / "healthcare.geojson")

m = folium.Map(
    location=config.MAP_CENTER,
    zoom_start=12,
    tiles="OpenStreetMap"
)

colors = {
    "pharmacy": "blue",
    "doctor": "red",
    "doctors": "red",
    "clinic": "green",
    "hospital": "purple",
}

for _, row in gdf.iterrows():

    geom = row.geometry

    if geom.geom_type != "Point":
        geom = geom.centroid

    amenity = row.get("amenity", "")

    color = colors.get(amenity, "gray")

    folium.CircleMarker(
        location=[geom.y, geom.x],
        radius=5,
        color=color,
        fill=True,
        fill_opacity=0.8,
        popup=f"""
<b>{row.get('name','بدون نام')}</b><br>
{amenity}
"""
    ).add_to(m)

outfile = config.OUTPUTS / "healthcare_map.html"

m.save(outfile)

print()
print("Saved map:")
print(outfile)