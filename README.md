# Pharmacy Location Intelligence
Current Version: v1.0  
Status: Stable

# Overview

Pharmacy Location Intelligence (PLI) is a GIS-based decision support system designed to identify the most suitable locations for establishing new pharmacies.

Instead of relying solely on population density or simple distance measures, the system combines multiple spatial criteria into a configurable multi-criteria decision model.

The complete workflow consists of two independent phases:

- **Phase 1 – Data Preparation**
  - Import and clean healthcare facilities
  - Download and process road network
  - Generate candidate locations
  - Process population raster
  - Attach population information to candidate locations

- **Phase 2 – Decision Engine**
  - Recalculate population (configurable search radius)
  - Compute raw criterion scores
  - Normalize all criteria
  - Apply configurable criterion weights
  - Select the best candidate locations using minimum-distance constraints
  - Generate interactive maps and Excel reports

Every decision parameter (weights, search radius, normalization limits, minimum spacing, etc.) is stored in a single JSON configuration file.

Therefore, the complete scoring behavior can be modified **without editing any Python source code**.

---

# Workflow Diagram

```text
                         Pharmacy Location Intelligence Workflow

┌──────────────────────────────────────────────────────────────────────┐
│                         Phase 1 — Data Preparation                   │
└──────────────────────────────────────────────────────────────────────┘

01_import_google.py
        │
        ▼
02_clean_google.py
        │
        ▼
03_prepare_database.py
        │
        ├─────────────────────────────────────────────┐
        ▼                                             │
master_database.geojson                              │
                                                      │
04_download_roads.py                                 │
        │                                             │
        ▼                                             │
05_prepare_roads.py                                  │
        │                                             │
        ▼                                             │
roads_clean.geojson                                  │
        │                                             │
        ▼                                             │
06_create_smart_candidates.py                         │
        │                                             │
        ▼                                             │
candidate_database.geojson                            │
                                                      │
07_create_urban_mask.py                               │
        │                                             │
        ▼                                             │
urban_mask.geojson                                    │
                                                      │
08_import_population.py                               │
        │                                             │
        ▼                                             │
09_prepare_population.py                              │
        │                                             │
        ▼                                             │
population_heatmap.geojson                            │
                                                      │
Outputs of Phase 1
(master_database, roads, candidates, population)
────────────────────────────────────────────────────────────────────────

┌──────────────────────────────────────────────────────────────────────┐
│                    Phase 2 — Spatial Decision Model                  │
└──────────────────────────────────────────────────────────────────────┘

20_attach_population.py
        │
        ▼
candidate_database + population
        │
        ▼
21_score_engine.py
        │
        ▼
Raw component scores
        │
        ▼
22_normalize_scores.py
        │
        ▼
Normalized components
        │
        ▼
23_select_best_areas.py
        │
        ▼
Top-N spatial filtering
        │
        ▼
best_areas.geojson
best_areas.xlsx
        │
        ▼
24_visualize_results.py
        │
        ▼
outputs/best_locations_map.html
```

Phase 1 generates all reusable spatial datasets and only needs to be executed when the underlying geographic data change.

Phase 2 contains the decision model. Users can freely modify the scoring parameters in `config/scoring.json` and rerun Phase 2 to immediately evaluate different planning scenarios without rebuilding the spatial datasets.


# Final Output

![Map](docs/output-screenshot.png)

---

# Quick Start (View Results Only)

If you only want to explore the final results, you only need:

```text
outputs/
    best_locations_map.html
```

Simply open

```text
outputs/best_locations_map.html
```

using any modern web browser.

No Python installation is required.

---

# Running Phase 2 Only

If you want to experiment with different scoring strategies, you do **not** need to rebuild the GIS datasets.

Simply modify:

```text
config/scoring.json
```

and execute:

```text
python scripts/run_phase2.py
```

The decision engine will recompute all scores and generate new recommended locations in a few seconds.

---

# Scoring Methodology

The scoring process is intentionally divided into two stages.

## Stage 1 — Raw Spatial Scores

Each candidate location receives four independent raw scores.

### 1. Prescription Potential

Hospitals, clinics and physicians are searched within the configurable radius.

Each nearby facility contributes according to:

- Facility type weight
- Gaussian distance decay

```
Prescription =
HospitalScore +
ClinicScore +
DoctorScore
```

---

### 2. Competition Penalty

Nearby pharmacies are searched within the same radius.

Each pharmacy subtracts score according to the same Gaussian distance function.

Higher values indicate stronger competition.

---

### 3. Population

Population is calculated by summing all population points inside the configurable radius.

The raw population is transformed using

```
log(1 + population)
```

to reduce the influence of extreme values.

---

### 4. Road Accessibility

Road class contributes a fixed bonus.

For example:

```
Primary road      > Secondary road > Residential road
```

This criterion intentionally has a much smaller influence than healthcare demand.

---

## Stage 2 — Robust Normalization

Each raw criterion is normalized independently.

Before normalization, extreme outliers are clipped using configurable percentiles.

```
2nd percentile  ← default lower limit
98th percentile ← default upper limit
```

Then Min–Max normalization converts every criterion to:

```
0 — 100
```

Therefore:

- 100 represents the strongest candidate for that criterion.
- 0 represents the weakest candidate.

---

## Stage 3 — Final Decision Score

The normalized criteria are combined using configurable weights.

Default configuration:

| Criterion | Weight |
|-----------|--------:|
| Prescription | 30% |
| Competition | 30% |
| Population | 30% |
| Road | 10% |

The final score is computed as:

```
Final Score =
 Prescription
− Competition
+ Population
+ Road
```

Because competition is a penalty, it is subtracted from the final score.

---

## Main Driver

For every recommended location, the system also reports the dominant criterion ("Main Driver").

This is determined **after normalization and weighting**, meaning it reflects the actual contribution of each criterion to the final ranking rather than the raw values.

This greatly improves interpretability when comparing candidate locations.
# For Developers

To reproduce the complete workflow:

```bash
python scripts/run_phase1.py
python scripts/run_phase2.py
```

Phase 1 prepares all spatial datasets.

Phase 2 performs the complete decision analysis, including:

- population attachment
- raw scoring
- score normalization
- candidate selection
- interactive visualization

---

# Project Structure

```text
config/
    app_config.py
    scoring.json

data/
    raw/
        ...
    processed/
        ...

docs/
    output-screenshot.png

outputs/
    best_locations_map.html

scripts/

    run_phase1.py
    run_phase2.py

    01_import_google.py
    ...
    11_prepare_population_heatmap.py

    20_attach_population.py
    21_score_engine.py
    22_normalize_scores.py
    23_select_best_areas.py
    24_visualize_results.py
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/pharmacy-location-intelligence.git

cd pharmacy-location-intelligence
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

Windows:

```bash
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Python Version

Tested with

- Python 3.13+

---

# Main Dependencies

Core libraries:

- geopandas
- shapely
- osmnx
- folium
- scipy
- pandas
- numpy
- matplotlib
- openpyxl
- pyproj
- requests

Complete versions are listed in:

```text
requirements.txt
```

---

# Data Sources

The project integrates four spatial datasets:

- Google Places healthcare facilities
- OpenStreetMap road network
- WorldPop population raster
- Generated urban boundary

All intermediate datasets are stored in:

```text
data/processed/
```

---

# Google Places Data

The raw Google Places response file

```text
master_healthcare_google_raw.jsonl
```

is intentionally excluded from the repository.

Users must generate this file using their own Google Maps Platform API key before executing the full Phase 1 pipeline.

This complies with Google Maps Platform Terms of Service.

If the raw file is not available, Script 01 is skipped automatically and the pipeline continues using the existing processed healthcare database.

---

# Pipeline Overview

## Phase 1 — Data Preparation

Purpose:

- Import Google Places
- Clean healthcare facilities
- Download road network
- Prepare road network
- Generate candidate locations
- Generate urban mask
- Import population raster
- Prepare population raster
- Generate population heatmap

Main output:

```text
data/processed/
```

---

## Phase 2 — Spatial Decision Engine

Purpose:

- Attach population using the current search radius
- Compute raw criterion scores
- Normalize criteria
- Apply weighted scoring
- Select best candidate locations
- Generate interactive outputs

Main outputs:

```text
outputs/best_locations_map.html

data/processed/best_areas.geojson

data/processed/best_areas.xlsx
```

---

# Configuration

All model parameters are stored in

```text
config/scoring.json
```

This file controls:

- facility weights
- search radius
- Gaussian sigma
- road bonuses
- normalization settings
- final criterion weights
- candidate selection parameters

No Python source code needs to be modified when calibrating the model.

---

# Model Philosophy

The system is intentionally transparent and fully interpretable.

Instead of using black-box machine learning models, every recommendation is produced from explicit spatial rules whose contribution can be inspected individually.

This allows planners to understand:

- why a location receives a high score,
- which criterion is responsible,
- how changing model parameters affects the recommendations.

The modular architecture also allows additional criteria (traffic, socioeconomic variables, medical specialties, etc.) to be incorporated in future versions without redesigning the pipeline.

---

# Citation

If this repository contributes to your research, please cite the repository and acknowledge the original author.

---

# License

Released under the MIT License.

Commercial use is permitted under the license terms.

If this work contributes to a commercial product, acknowledgement of the original repository is appreciated.