# ==========================================
# General
# ==========================================

TOP_CANDIDATES = 100

CLUSTER_DISTANCE = 300  # meters

# ==========================================
# Candidate generation
# ==========================================

ROAD_SAMPLE_DISTANCE = {

    "trunk": 40,
    "trunk_link": 40,

    "primary": 45,
    "primary_link": 45,

    "secondary": 50,
    "secondary_link": 50,

    "tertiary": 60,
    "tertiary_link": 60,

    "residential": 80,

    "service": 100,

    "living_street": 120,

    "unclassified": 90,
}

# ==========================================
# Road importance
# ==========================================

ROAD_WEIGHT = {

    "trunk":4,

    "primary":4,

    "secondary":3,

    "tertiary":2,

    "residential":1,

    "service":1,

    "living_street":1,

    "unclassified":1

}

# ==========================================
# Distance decay
# ==========================================

DOCTOR_DECAY = 400

PHARMACY_DECAY = 350

ACCESSIBILITY_RADIUS = 500