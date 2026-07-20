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
- population radius and transform
- normalization and criterion weights
- candidate selection

This file is expected to be modified during calibration experiments.

Changing this file does not require modifying any Python code.

### Calibration notes

- **Facility weights are ratios.** Raw criterion scores are min-max
  normalized before weighting, so only the *relative* proportions of
  `Hospital : Clinic : Doctor` matter (6:3:2 behaves identically to
  12:6:4). Competition uses raw Gaussian influence with no weight for
  the same reason — any constant factor cancels during normalization.
- **Criterion importance** is controlled exclusively by the four
  `*_weight` values in the `normalization` block. Competition is
  subtracted from the final score, so a larger `competition_weight`
  means a stronger penalty.