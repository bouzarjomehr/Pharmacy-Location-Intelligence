from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

RAW_GOOGLE_FILE = (
    ROOT
    / "data"
    / "raw"
    / "master_healthcare_google_raw.jsonl"
)

PIPELINE = [

    "13_import_google.py",

    "14_clean_google.py",

    "15_prepare_database.py",

    "18_download_roads.py",

    "19_prepare_roads.py",

    "24_create_urban_mask.py",

]

print("=" * 60)
print("PHASE 1 : DATA PREPARATION")
print("=" * 60)

for script in PIPELINE:

    # -------------------------------------------------
    # Script 13 is optional
    # -------------------------------------------------

    if (
        script == "13_import_google.py"
        and not RAW_GOOGLE_FILE.exists()
    ):

        print()
        print("-" * 60)
        print("Skipping:", script)
        print("-" * 60)
        print(
            "Google raw response not found."
        )
        print(
            "Using existing processed dataset:"
        )
        print(
            ROOT
            / "data"
            / "processed"
            / "google_healthcare.geojson"
        )

        continue

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