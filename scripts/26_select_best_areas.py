from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parents[1]

print("=" * 60)
print("Selecting Best Areas")
print("=" * 60)

INPUT = ROOT / "data" / "processed" / "candidate_database.geojson"

gdf = gpd.read_file(INPUT)

# برای محاسبه فاصله
gdf = gdf.to_crs(32640)

gdf = gdf.sort_values(
    "final_score",
    ascending=False
).reset_index(drop=True)

MIN_DISTANCE = 250      # متر
TOP_N = 100

selected = []

while len(gdf) > 0 and len(selected) < TOP_N:

    best = gdf.iloc[0]

    selected.append(best)

    distances = gdf.distance(best.geometry)

    gdf = gdf.loc[
        distances > MIN_DISTANCE
    ].reset_index(drop=True)

selected = gpd.GeoDataFrame(
    selected,
    crs=gdf.crs
)

selected = selected.to_crs(4326)

out_geo = ROOT / "data" / "processed" / "best_areas.geojson"
out_xlsx = ROOT / "data" / "processed" / "best_areas.xlsx"

selected.to_file(
    out_geo,
    driver="GeoJSON"
)

selected.drop(
    columns="geometry"
).to_excel(
    out_xlsx,
    index=False
)

print()
print("Saved:")
print(out_geo)
print(out_xlsx)

print()
print(selected[[
    "candidate_id",
    "road_type",
    "final_score"
]].head(20))

print()
print("Selected:", len(selected))