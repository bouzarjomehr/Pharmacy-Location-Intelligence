from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

PIPELINE = [

    "20_score_engine.py",

    "21_select_best_areas.py",

    "22_visualize_results.py",

]

print("=" * 60)
print("PHASE 2 : SCENARIO ANALYSIS")
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
print("Phase 2 Finished Successfully")
print("=" * 60)