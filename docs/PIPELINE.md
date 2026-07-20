Phase 1 — Data Preparation
(run_phase1_DATA_PREPARATION.py)

Google Raw Data (optional)
    ↓
01 Google Import
    ↓
02 Cleaning
    ↓
03 Master Database
    ↓
04 Road Download
    ↓
05 Road Preparation
    ↓
06 Candidate Generation (road points)
    ↓
07 Urban Mask
    ↓
08 Population Download (GHSL)
    ↓
09 Population Raster Clip
    ↓
10 Population Heatmap

Phase 2 — Scenario Analysis
(run_phase2_SCENARIO_ANALYSIS.py)

20 Attach Population (sum within configurable radius)
    ↓
21 Raw Multi-Criteria Scoring
    ↓
22 Normalization + Weighted Final Score
    ↓
23 Best-Area Selection (top-N, minimum spacing)
    ↓
24 Interactive Map
