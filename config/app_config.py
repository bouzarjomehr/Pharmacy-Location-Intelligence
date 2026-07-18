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

# City center (latitude, longitude)
MAP_CENTER = (31.8974, 54.3569)

# Initial map zoom level (visualization only)
MAP_ZOOM = 13

# Radius of the study area around MAP_CENTER (meters)
STUDY_RADIUS = 25000

# ==========================
# Coordinate Reference Systems
# ==========================

# Project CRS used for all spatial analysis (meters)
# UTM Zone 40N (suitable for Yazd)
TARGET_CRS = 32640

# Geographic CRS used for exporting GeoJSON and web maps
# WGS84 latitude / longitude
OUTPUT_CRS = 4326