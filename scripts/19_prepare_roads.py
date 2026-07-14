from pathlib import Path
import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent

print("=" * 60)
print("Preparing Road Network")
print("=" * 60)

roads = gpd.read_file(
    ROOT / "data" / "processed" / "roads.geojson"
)

# ----------------------------------------
# فقط معابر مناسب برای احداث داروخانه
# ----------------------------------------

KEEP = {
    "motorway":5,
    "motorway_link":5,

    "trunk":5,
    "trunk_link":5,

    "primary":4,
    "primary_link":4,

    "secondary":3,
    "secondary_link":3,

    "tertiary":2,
    "tertiary_link":2,

    "residential":1,

    "living_street":1,

    "unclassified":1,

    "service":0.5
}


def get_type(v):

    if isinstance(v, list):
        for x in v:
            if x in KEEP:
                return x
        return None

    if v in KEEP:
        return v

    return None


roads["road_type"] = roads["highway"].apply(get_type)

roads = roads[
    roads["road_type"].notna()
].copy()

roads["road_weight"] = roads["road_type"].map(KEEP)

roads = roads.to_crs(32640)

outfile = ROOT / "data" / "processed" / "roads_clean.geojson"

roads.to_file(outfile, driver="GeoJSON")

print()
print("Saved:")
print(outfile)

print()
print("Road counts")
print("-"*40)

print(
    roads["road_type"]
    .value_counts()
)

print()
print("Total roads:", len(roads))