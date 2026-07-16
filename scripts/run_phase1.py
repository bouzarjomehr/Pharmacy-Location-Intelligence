from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

PIPELINE = [

    "13_import_google.py",

    "14_clean_google.py",

    "15_prepare_database.py",

    "18_download_roads.py",

    "19_prepare_roads.py",

    "20_create_smart_candidates.py",

    "21_score_roads.py",    

    "24_create_urban_mask.py",

]

print("=" * 60)
print("PHASE 1 : DATA PREPARATION")
print("=" * 60)

for script in PIPELINE:

    print()
    print("-" * 60)
    print("Running:", script)
    print("-" * 60)

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script)]
    )

    if result.returncode != 0:
        print()
        print("ERROR:", script)
        sys.exit(1)

print()
print("=" * 60)
print("Phase 1 Finished Successfully")
print("=" * 60)