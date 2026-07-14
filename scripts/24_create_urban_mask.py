from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent

print("=" * 60)
print("Creating Urban Mask")
print("=" * 60)

roads = gpd.read_file(
    ROOT/"data"/"processed"/"roads_clean.geojson"
)

roads = roads.to_crs(32640)

# فقط خیابان‌هایی که جزو بافت شهری هستند
urban = roads[
    roads.road_type.isin([
        "residential",
        "tertiary",
        "secondary",
        "primary",
        "service",
        "living_street",
        "unclassified"
    ])
].copy()

# ایجاد بافر برای هر خیابان
urban["geometry"] = urban.buffer(120)

# ادغام همه پلیگون‌ها
urban_mask = urban.dissolve()

# حذف سوراخ‌های کوچک
urban_mask = urban.explode(index_parts=False)

urban_mask = urban[
    ["geometry"]
].dissolve()

urban_mask = urban_mask.buffer(0)

urban_mask = gpd.GeoDataFrame(
    geometry=urban_mask.geometry,
    crs=roads.crs
)

urban_mask = urban_mask.to_crs(4326)

outfile = ROOT/"data"/"processed"/"urban_mask.geojson"

urban_mask.to_file(
    outfile,
    driver="GeoJSON"
)

print()
print("Saved:")
print(outfile)