
# Pharmacy Location Intelligence
## Project Architecture

---

# Version
Current Version: 0.5

---

# Pipeline

## Phase 01 — Data Acquisition

✔ Download Study Area

✔ Download Healthcare Facilities

✔ Import Google Data

✔ Merge Databases

Outputs

- master_database.geojson

---

## Phase 02 — Road Network

✔ Download Roads

✔ Clean Roads

Outputs

- roads_clean.geojson

---

## Phase 03 — Candidate Generation

✔ Generate Smart Candidate Points

Outputs

- road_points.geojson

---

## Phase 04 — Spatial Scoring

Current Modules

✔ Road Score

✔ Facility Score

✔ Multi-Criteria Score

Outputs

- road_scores_multicriteria.geojson

---

## Phase 05 — Candidate Database

✔ Generate Candidate Database

Outputs

- candidate_database.geojson

candidate_database.xlsx

---

## Phase 06 — Spatial Optimization

✔ Urban Mask

✔ Minimum Distance Selection

Outputs

- best_areas.geojson

best_areas.xlsx

---

## Phase 07 — Visualization

✔ Interactive Map

Outputs

- best_locations_map.html

---

# Planned Version 1.0

## Scoring Modules

Prescription Model

Competition Model

Accessibility Model

Road Importance Model

Distance Penalty Model

Coverage Model

Population Density Model

Parking Availability

Traffic Volume

Travel Time

Future Demand

Machine Learning Score

---

# Planned Version 2.0

Web Dashboard

Scenario Comparison

Weight Adjustment GUI

Automatic Report Generator

REST API

Interactive Ranking

---

# Future Data Sources

OSM

Google

Neshan

Population Census

Traffic

Land Use

Municipality Data

Insurance Claims

Prescription Data

---

# Design Principles

Each script performs exactly one task.

Each phase reads only saved files.

No script overwrites raw data.

Every phase produces reproducible outputs.

Configuration stays outside source code.

Scoring modules remain independent.

