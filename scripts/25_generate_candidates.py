from pathlib import Path

import geopandas as gpd

print("=" * 60)
print("Generating Candidate Locations")
print("=" * 60)

ROOT = Path(__file__).resolve().parents[1]

# -----------------------------
# Load scored road points
# -----------------------------
candidate = gpd.read_file(
    ROOT / "data" / "processed" / "road_scores_multicriteria.geojson"
)

# -----------------------------
# Keep only urban area
# -----------------------------
mask = gpd.read_file(
    ROOT / "data" / "processed" / "urban_mask.geojson"
)

candidate = gpd.sjoin(
    candidate,
    mask,
    predicate="within",
    how="inner"
)

candidate = candidate.drop(
    columns=["index_right"],
    errors="ignore"
)

# -----------------------------
# Sort by score
# -----------------------------
candidate = candidate.sort_values(
    "final_score",
    ascending=False
).reset_index(drop=True)

# -----------------------------
# Candidate IDs
# -----------------------------
candidate["candidate_id"] = [
    f"C{i:06d}"
    for i in range(1, len(candidate) + 1)
]

# -----------------------------
# Columns
# -----------------------------
cols = [
    "candidate_id",
    "geometry",
    "road_type",
    "road_weight",
    "prescription_score",
    "competition_score",
    "accessibility_score",
    "road_score",
    "final_score",
]

candidate = candidate[cols]

# -----------------------------
# Save
# -----------------------------
out_geo = ROOT / "data" / "processed" / "candidate_database.geojson"
out_xlsx = ROOT / "data" / "processed" / "candidate_database.xlsx"

candidate.to_file(
    out_geo,
    driver="GeoJSON"
)

candidate.drop(
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
print(candidate.head())

print()
print("Total candidates:", len(candidate))