from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

PIPELINE = [

    "30_spatial_diagnostics.py",

    "31_sensitivity_analysis.py",

    "32_component_contribution_analysis.py",

    "33_variance_decomposition.py",

    "34_competition_ablation.py",

]

print("=" * 60)
print("PHASE 3 : VALIDATION ANALYSIS")
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
print("Phase 3 Finished Successfully")
print("=" * 60)