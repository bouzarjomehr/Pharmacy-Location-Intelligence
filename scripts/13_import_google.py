import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import geopandas as gpd

import config

print("=" * 60)
print("Importing Google Healthcare Database")
print("=" * 60)

input_file = config.DATA_RAW / "master_healthcare_google_raw.jsonl"

if not input_file.exists():
    raise FileNotFoundError(input_file)

records = []

with open(input_file, "r", encoding="utf-8") as f:

    for line in f:

        if not line.strip():
            continue

        obj = json.loads(line)

        lat = obj.get("location", {}).get("latitude")
        lon = obj.get("location", {}).get("longitude")

        if lat is None or lon is None:
            continue

        name = obj.get("displayName", {}).get("text", "")

        records.append({

            "google_id":
                obj.get("id"),

            "name":
                name,

            "primary_type":
                obj.get("primaryType"),

            "types":
                ",".join(obj.get("types", [])),

            "lat":
                lat,

            "lon":
                lon,

            "rating":
                obj.get("rating"),

            "reviews":
                obj.get("userRatingCount"),

            "address":
                obj.get("formattedAddress"),

            "phone":
                obj.get("nationalPhoneNumber"),

            "website":
                obj.get("websiteUri"),

            "maps":
                obj.get("googleMapsUri"),

        })

df = pd.DataFrame(records)

print()
print("Loaded:", len(df), "records")

# ---------------------------------------------------
# Keep only healthcare
# ---------------------------------------------------

allowed = {

    "doctor",
    "dentist",
    "hospital",
    "medical_center",
    "medical_clinic",
    "dental_clinic",
    "medical_lab",
    "pharmacy",
    "drugstore",
    "physiotherapist",
    "chiropractor",
    "skin_care_clinic",

}

df = df[df["primary_type"].isin(allowed)].copy()

print("Healthcare records:", len(df))

# ---------------------------------------------------
# Standardize type
# ---------------------------------------------------

mapping = {

    "doctor": "Doctor",

    "dentist": "Doctor",

    "physiotherapist": "Doctor",

    "chiropractor": "Doctor",

    "hospital": "Hospital",

    "medical_center": "Clinic",

    "medical_clinic": "Clinic",

    "dental_clinic": "Clinic",

    "skin_care_clinic": "Clinic",

    "medical_lab": "Clinic",

    "pharmacy": "Pharmacy",

    "drugstore": "Pharmacy",

}

df["type"] = df["primary_type"].map(mapping)

print()
print(df["type"].value_counts())

# ---------------------------------------------------
# GeoDataFrame
# ---------------------------------------------------

geometry = gpd.points_from_xy(df.lon, df.lat)

gdf = gpd.GeoDataFrame(

    df,

    geometry=geometry,

    crs="EPSG:4326",

)

# ---------------------------------------------------
# Save
# ---------------------------------------------------

out_excel = config.DATA_PROCESSED / "google_healthcare.xlsx"

out_geojson = config.DATA_PROCESSED / "google_healthcare.geojson"

gdf.drop(columns="geometry").to_excel(

    out_excel,

    index=False,

)

gdf.to_file(

    out_geojson,

    driver="GeoJSON",

)

print()
print("Saved:")
print(out_excel)
print(out_geojson)