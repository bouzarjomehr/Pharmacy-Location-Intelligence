from pathlib import Path

# ==========================
# Project Paths
# ==========================

ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parent

DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"

OUTPUTS = ROOT / "outputs"
LOGS = ROOT / "logs"

# ==========================
# Study Area
# ==========================

CITY = "Yazd"
COUNTRY = "Iran"

# مرکز تقریبی شهر یزد
MAP_CENTER = (31.8974, 54.3569)

MAP_ZOOM = 13

# ==========================
# Categories
# ==========================

CATEGORIES = {
    "pharmacy": "blue",
    "doctor": "red",
    "clinic": "green",
    "hospital": "purple",
}