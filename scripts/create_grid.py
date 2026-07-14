from pathlib import Path
import sys

import geopandas as gpd
import numpy as np
from shapely.geometry import Point

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

# ---------------------------------------

print("Loading study area...")

boundary = gpd.read_file(
    config.DATA_RAW / "study_area_boundary.geojson"
)

# ---------------------------------------

# تبدیل به سیستم متریک
boundary = boundary.to_crs(32640)

xmin, ymin, xmax, ymax = boundary.total_bounds

spacing = 250  # متر

xs = np.arange(xmin, xmax, spacing)
ys = np.arange(ymin, ymax, spacing)

points = []

polygon = boundary.unary_union

for x in xs:
    for y in ys:

        p = Point(x, y)

        if polygon.contains(p):
            points.append(p)

grid = gpd.GeoDataFrame(
    geometry=points,
    crs=32640
)

grid = grid.to_crs(4326)

outfile = config.DATA_PROCESSED / "analysis_grid.geojson"

grid.to_file(outfile, driver="GeoJSON")

print()

print(f"Created {len(grid)} grid points")

print(outfile)