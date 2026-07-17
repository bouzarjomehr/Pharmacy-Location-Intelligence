from pathlib import Path

# ==========================
# Project Paths
# ==========================

ROOT = Path(__file__).resolve().parents[1]

OUTPUTS = ROOT / "outputs"
CONFIG = ROOT / "config"
LOGS = ROOT / "logs"
DATA = ROOT / "data"

DATA_RAW = DATA / "raw"
DATA_PROCESSED = DATA / "processed"
DATA_MANUAL = DATA / "manual"
DATA_CACHE = DATA / "cache"

# ==========================
# Study Area
# ==========================

CITY = "Yazd"
COUNTRY = "Iran"

# Yazd City Center
MAP_CENTER = (31.8974, 54.3569)
MAP_ZOOM = 13

# Coordinate Reference Systems
TARGET_CRS = 32640
OUTPUT_CRS = 4326