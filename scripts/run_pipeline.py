from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

PIPELINE = [

    "20_create_smart_candidates.py",

    "21_score_roads.py",

    "22_score_facilities.py",

    "23_score_engine.py",

    "25_generate_candidates.py",

    "26_select_best_areas.py",

    "27_visualize_results.py",

]

print("=" * 60)
print("PHARMACY LOCATION INTELLIGENCE")
print("Running Full Pipeline")
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
print("Pipeline Finished Successfully")
print("=" * 60)