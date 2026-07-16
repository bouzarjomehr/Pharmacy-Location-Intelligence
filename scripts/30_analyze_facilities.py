from pathlib import Path

import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

gdf = gpd.read_file(
    ROOT / "data" / "processed" / "master_database.geojson"
)

print("=" * 70)
print("FACILITY ANALYSIS")
print("=" * 70)

print("\nFacility Types")
print(gdf["type"].value_counts())

print("\nColumns")
print(gdf.columns.tolist())

print("\nMissing Values")
print(gdf.isna().sum())

if "doctor_count" in gdf.columns:

    print("\nDoctor Count Summary")

    print(gdf["doctor_count"].describe())

    print("\nTop Facilities")

    cols = [
        c for c in [
            "name",
            "type",
            "doctor_count"
        ]
        if c in gdf.columns
    ]

    print(
        gdf[cols]
        .sort_values(
            "doctor_count",
            ascending=False
        )
        .head(30)
    )

outfile = ROOT / "docs" / "facility_analysis.xlsx"

pd.DataFrame(gdf.drop(columns="geometry")).to_excel(
    outfile,
    index=False,
)

print("\nSaved:")
print(outfile)