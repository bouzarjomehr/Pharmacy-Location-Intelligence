from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "master_database.geojson"

print("=" * 70)
print("SPECIALTY ANALYSIS")
print("=" * 70)

gdf = gpd.read_file(INPUT)

doctors = gdf[gdf["type"] == "Doctor"].copy()

print()
print(f"Total Doctors : {len(doctors)}")

# -------------------------------------------------
# بررسی ستون specialty
# -------------------------------------------------

if "specialty" not in doctors.columns:

    print()
    print("Column 'specialty' not found.")
    raise SystemExit

doctors["specialty"] = (
    doctors["specialty"]
    .fillna("")
    .astype(str)
    .str.strip()
)

filled = (doctors["specialty"] != "").sum()
empty = (doctors["specialty"] == "").sum()

print(f"With specialty : {filled}")
print(f"Without specialty : {empty}")

# -------------------------------------------------
# فراوانی تخصص‌ها
# -------------------------------------------------

freq = (
    doctors.loc[
        doctors["specialty"] != "",
        "specialty"
    ]
    .value_counts()
    .rename_axis("specialty")
    .reset_index(name="count")
)

print()
print("Unique specialties :", len(freq))
print()

print(freq.head(50))

# -------------------------------------------------
# ذخیره اکسل
# -------------------------------------------------

OUT = ROOT / "docs" / "specialty_analysis.xlsx"

with pd.ExcelWriter(OUT) as writer:

    freq.to_excel(
        writer,
        sheet_name="Frequency",
        index=False
    )

    doctors[
        [
            "name",
            "specialty",
            "rating",
            "reviews",
            "address",
        ]
    ].to_excel(
        writer,
        sheet_name="Doctors",
        index=False
    )

print()
print("Saved:")
print(OUT)