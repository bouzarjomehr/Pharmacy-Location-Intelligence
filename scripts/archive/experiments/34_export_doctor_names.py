from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "raw" / "master_healthcare_google_raw.jsonl"

OUTPUT = ROOT / "docs" / "doctor_names.xlsx"

rows = []

with open(INPUT, "r", encoding="utf-8") as f:

    for line in f:

        record = json.loads(line)

        primary = record.get("primaryType", "")

        if primary != "doctor":
            continue

        display = record.get("displayName", {})

        name = display.get("text", "")

        rows.append({

            "id": record.get("id", ""),

            "name": name,

            "primaryType": primary,

            "types": ", ".join(record.get("types", []))

        })

df = pd.DataFrame(rows)

print("=" * 60)
print("Doctor Records")
print("=" * 60)
print()

print("Doctors:", len(df))
print()

print(df.head(20))

df.to_excel(OUTPUT, index=False)

print()
print("Saved:")
print(OUTPUT)