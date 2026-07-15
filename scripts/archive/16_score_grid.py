import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

print("="*60)
print("Scoring Analysis Grid")
print("="*60)

grid = gpd.read_file(ROOT/"data/processed/analysis_grid.geojson").to_crs(32640)
db = gpd.read_file(ROOT/"data/processed/master_database.geojson").to_crs(32640)

weights = {
    "Hospital": 8,
    "Clinic": 5,
    "Doctor": 2,
    "Pharmacy": -10
}

db["weight"] = db["type"].map(weights).fillna(0)

grid_xy = np.column_stack([grid.geometry.x, grid.geometry.y])
db_xy = np.column_stack([db.geometry.x, db.geometry.y])

tree = cKDTree(db_xy)

print(f"Grid points : {len(grid)}")
print(f"Facilities  : {len(db)}")

scores = []

for p in grid_xy:

    dist, idx = tree.query(
        p,
        k=30,               # فقط 30 مرکز نزدیک
        distance_upper_bound=5000
    )

    score = 0

    for d, i in zip(np.atleast_1d(dist), np.atleast_1d(idx)):

        if np.isinf(d):
            continue

        score += db.iloc[i]["weight"] / (d + 100)

    scores.append(score)

grid["score"] = np.round(scores,4)

grid = grid.to_crs(4326)

outfile = ROOT/"data/processed/scored_grid.geojson"
grid.to_file(outfile, driver="GeoJSON")

print()
print("Saved:")
print(outfile)

print()
print(grid["score"].describe())