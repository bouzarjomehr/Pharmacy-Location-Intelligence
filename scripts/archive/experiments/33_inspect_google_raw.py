from pathlib import Path
import json
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "raw" / "master_healthcare_google_raw.jsonl"

print("=" * 70)
print("INSPECT GOOGLE RAW DATA")
print("=" * 70)

records = []

with open(INPUT, "r", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))

print()
print("Total records:", len(records))

# -------------------------------------------------
# Keys
# -------------------------------------------------

keys = Counter()

for r in records:
    keys.update(r.keys())

print("\nAvailable fields:\n")

for k in sorted(keys):
    print(k)

# -------------------------------------------------
# First record
# -------------------------------------------------

print("\n")
print("=" * 70)
print("FIRST RECORD")
print("=" * 70)

for k, v in records[0].items():

    print("\n--------------------------------------")
    print(k)
    print(type(v))
    print(v)

# -------------------------------------------------
# Search possible specialty fields
# -------------------------------------------------

keywords = [
    "special",
    "type",
    "category",
    "doctor",
    "medical",
    "clinic",
    "hospital",
    "description",
    "about",
    "editorial",
    "primary",
    "tag",
]

print("\n")
print("=" * 70)
print("FIELDS CONTAINING POSSIBLE MEDICAL INFO")
print("=" * 70)

for k in sorted(keys):

    lower = k.lower()

    if any(x in lower for x in keywords):

        print(k)