from pathlib import Path
import sys
import requests

# -----------------------------
# Add project root
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

query = f"""
[out:json][timeout:120];

(
  nwr
    ["amenity"="pharmacy"]
    (around:15000,{config.MAP_CENTER[0]},{config.MAP_CENTER[1]});
);

out center tags;
"""

print("Downloading pharmacies...")

response = requests.post(
    OVERPASS_URL,
    data=query.encode("utf-8"),
    headers={
        "Content-Type": "text/plain",
        "User-Agent": "PharmacyLocationIntelligence/0.1"
    },
    timeout=120
)

response.raise_for_status()

data = response.json()

print()

print("Success!")

print(f"Found {len(data['elements'])} pharmacies.")