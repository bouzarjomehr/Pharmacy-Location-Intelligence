"""
32_component_contribution_analysis.py

Analyze which scoring components contribute most to the final
selection of pharmacy candidate locations.

Outputs
-------
outputs/
    validation/
        32_component_statistics.xlsx
        32_driver_frequency.png
        32_component_stacked.png
        32_component_heatmap.png
        32_component_vs_finalscore.png
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import config.app_config as app_config


# ==========================================================
# Files
# ==========================================================

INPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "best_areas.geojson"
)

OUTPUT_DIR = (
    ROOT
    / "outputs"
    / "validation"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# Load
# ==========================================================

print("=" * 70)
print("Component Contribution Analysis")
print("=" * 70)

gdf = (
    gpd.read_file(INPUT_FILE)
    .to_crs(app_config.TARGET_CRS)
)

print()
print(f"Selected locations : {len(gdf)}")


# ==========================================================
# Components
# ==========================================================

components = [

    "prescription_component",

    "competition_component",

    "population_component",

    "road_component",

]

for c in components:

    if c not in gdf.columns:

        raise ValueError(f"{c} not found.")


# ==========================================================
# Driver Frequency
# ==========================================================

driver_count = (

    gdf["main_reason"]

    .value_counts()

    .rename_axis("Driver")

    .reset_index(name="Count")

)

driver_count["Percent"] = (

    driver_count["Count"]

    / len(gdf)

    * 100

)

print()
print(driver_count)

# ==========================================================
# Export contribution table
# ==========================================================

contribution_table = gdf[
    [
        "candidate_id",
        "final_score",
        "main_reason",
        "prescription_component",
        "competition_component",
        "population_component",
        "road_component",
    ]
].copy()

outfile = (
    OUTPUT_DIR
    / "32_component_statistics.xlsx"
)

with pd.ExcelWriter(outfile) as writer:

    contribution_table.to_excel(
        writer,
        sheet_name="Candidate Contributions",
        index=False,
    )

    driver_count.to_excel(
        writer,
        sheet_name="Driver Summary",
        index=False,
    )

print()
print("Saved:")
print(outfile)


# ==========================================================
# Figure 1
# Driver Frequency
# ==========================================================

plt.figure(figsize=(7,4))

bars = plt.bar(
    driver_count["Driver"],
    driver_count["Count"],
)

plt.ylabel("Number of Selected Locations")

plt.xlabel("Main Driver")

plt.title("Dominant Driver of Selected Locations")

for bar in bars:

    height = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width()/2,
        height + 0.5,
        f"{int(height)}",
        ha="center",
    )

plt.tight_layout()

fig1 = (
    OUTPUT_DIR
    / "32_driver_frequency.png"
)

plt.savefig(
    fig1,
    dpi=300,
)

plt.close()

print(fig1)


# ==========================================================
# Figure 2
# Stacked Component Contribution
# ==========================================================

plot_df = contribution_table.sort_values(
    "final_score",
    ascending=False,
).reset_index(drop=True)

x = np.arange(len(plot_df))

plt.figure(figsize=(14,6))

plt.bar(
    x,
    plot_df["prescription_component"],
    label="Prescription",
)

plt.bar(
    x,
    plot_df["population_component"],
    bottom=plot_df["prescription_component"],
    label="Population",
)

plt.bar(
    x,
    plot_df["road_component"],
    bottom=(
        plot_df["prescription_component"]
        + plot_df["population_component"]
    ),
    label="Road",
)

plt.bar(
    x,
    -plot_df["competition_component"],
    color="red",
    alpha=0.45,
    label="Competition Penalty",
)

plt.xlabel("Selected Candidate Rank")

plt.ylabel("Contribution to Final Score")

plt.title("Component Contribution for Selected Candidates")

plt.legend()

plt.tight_layout()

fig2 = (
    OUTPUT_DIR
    / "32_component_stacked.png"
)

plt.savefig(
    fig2,
    dpi=300,
)

plt.close()

print(fig2)

# ==========================================================
# Correlation between components
# ==========================================================

corr = contribution_table[
    [
        "prescription_component",
        "competition_component",
        "population_component",
        "road_component",
        "final_score",
    ]
].corr()

corr.to_excel(
    OUTPUT_DIR / "32_component_correlation.xlsx"
)

print(
    OUTPUT_DIR / "32_component_correlation.xlsx"
)

# ==========================================================
# Scatter plots
# ==========================================================

component_names = [

    "prescription_component",
    "competition_component",
    "population_component",
    "road_component",

]

for component in component_names:

    plt.figure(figsize=(5,4))

    plt.scatter(

        contribution_table[component],

        contribution_table["final_score"],

        alpha=0.70,

    )

    plt.xlabel(component.replace("_", " ").title())

    plt.ylabel("Final Score")

    plt.title(component.replace("_", " ").title())

    plt.tight_layout()

    outfile = (

        OUTPUT_DIR

        / f"32_{component}_scatter.png"

    )

    plt.savefig(

        outfile,

        dpi=300,

    )

    plt.close()

    print(outfile)


# ==========================================================
# Summary statistics
# ==========================================================

summary = contribution_table.describe().T

summary.to_excel(

    OUTPUT_DIR / "32_component_summary.xlsx"

)

print(

    OUTPUT_DIR / "32_component_summary.xlsx"

)

print()

print("="*70)

print("Driver distribution")

print("="*70)

print(driver_count)

print()

print("="*70)

print("Mean component contribution")

print("="*70)

print(

    contribution_table[
        [
            "prescription_component",
            "competition_component",
            "population_component",
            "road_component",
        ]
    ].mean()

)

print()

print("="*70)

print("Finished")

print("="*70)