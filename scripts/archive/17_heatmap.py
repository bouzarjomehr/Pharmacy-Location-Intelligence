import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import geopandas as gpd
import folium
from branca.colormap import LinearColormap

print("=" * 60)
print("Creating Heatmap")
print("=" * 60)

gdf = gpd.read_file(ROOT / "data/processed/scored_grid.geojson")

m = folium.Map(
    location=[31.8974, 54.3569],
    zoom_start=12,
    tiles="CartoDB positron"
)

colormap = LinearColormap(
    colors=[
        "darkred",
        "red",
        "orange",
        "yellow",
        "lightgreen",
        "green",
        "darkgreen"
    ],
    vmin=gdf.score.min(),
    vmax=gdf.score.max()
)

for _, row in gdf.iterrows():

    folium.CircleMarker(
        location=[
            row.geometry.y,
            row.geometry.x
        ],
        radius=2,
        color=colormap(row.score),
        fill=True,
        fill_opacity=0.8,
        weight=0
    ).add_to(m)

colormap.caption = "Suitability Score"
colormap.add_to(m)

outfile = ROOT / "outputs" / "heatmap.html"

m.save(outfile)

print()
print("Saved:")
print(outfile)