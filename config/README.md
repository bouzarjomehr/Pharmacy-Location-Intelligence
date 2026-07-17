# Configuration

The project intentionally separates configuration into two categories.

## app_config.py

Contains project constants.

Examples:

- project paths
- CRS
- map defaults
- visualization colors

These values rarely change.

---

## scoring.json

Contains the scoring model parameters.

Examples:

- facility weights
- road bonuses
- Gaussian decay
- search radius
- candidate selection

This file is expected to be modified during calibration experiments.

Changing this file does not require modifying any Python code.