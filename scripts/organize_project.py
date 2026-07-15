from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

ARCHIVE = SCRIPTS / "archive"
DEV = SCRIPTS / "dev"

ARCHIVE.mkdir(exist_ok=True)
DEV.mkdir(exist_ok=True)

archive_files = [

    "16_score_grid.py",
    "17_heatmap.py",
    "17_download_buildings.py",
    "18_download_buildings_tiles.py",
    "20_create_road_points.py",

    "create_grid.py",
    "create_map.py",
    "clean_healthcare.py",

]

dev_files = [

    "project_inventory.py",
    "setup_project.py",

    "test_osm.py",
    "test_osmnx_download.py",
    "test_overpass.py",

]

delete_files = [

    "download_osm.py",
    "download_neshan.py",

]

print("=" * 60)
print("Organizing Project")
print("=" * 60)

# ---------- Archive ----------

for f in archive_files:

    src = SCRIPTS / f

    if src.exists():

        dst = ARCHIVE / f

        shutil.move(src, dst)

        print("ARCHIVE :", f)

# ---------- Dev ----------

for f in dev_files:

    src = SCRIPTS / f

    if src.exists():

        dst = DEV / f

        shutil.move(src, dst)

        print("DEV     :", f)

# ---------- Delete ----------

for f in delete_files:

    src = SCRIPTS / f

    if src.exists():

        src.unlink()

        print("DELETE  :", f)

print()
print("=" * 60)
print("Done")
print("=" * 60)