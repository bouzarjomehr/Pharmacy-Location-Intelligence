# Decision Log

This document records the major architectural and methodological decisions made during the development of the Pharmacy Location Intelligence project.

---

# D001 — Rename the Project

**Status:** Accepted

### Context

The project was initially developed specifically for Yazd Province under the name **Yazd Pharmacies**.

### Decision

The project was renamed to **Pharmacy Location Intelligence**.

### Reason

The scoring engine, preprocessing pipeline and visualization workflow were designed to become reusable for any city rather than remaining specific to Yazd.

---

# D002 — Define the Study Area Using a Functional Urban Mask

**Status:** Accepted

### Context

Administrative city boundaries contain large undeveloped areas that are not relevant for pharmacy site selection.

### Decision

Candidate locations are generated only inside a functional urban mask derived from the road network.

### Reason

Pharmacy demand is determined by actual urban accessibility rather than municipal borders.

This significantly reduces false candidate locations in deserts, agricultural land and industrial outskirts.

---

# D003 — Use Multiple Data Sources for Healthcare Facilities

**Status:** Accepted

### Context

Neither OpenStreetMap nor Google Maps alone provides sufficiently complete healthcare data.

### Decision

The project combines multiple data sources into a single master healthcare database.

Current workflow:

- OpenStreetMap (primary spatial dataset)
- Google Maps (completeness improvement)
- Manual verification and cleaning

### Consequences

**Positive**

- Better coverage of physicians, clinics and hospitals.
- Reduced missing healthcare facilities.
- Higher confidence in demand estimation.

**Trade-off**

Google data requires manual extraction and cleaning rather than direct API integration because of licensing and cost considerations.

---

# D004 — Exclude Residential Roads from Candidate Generation

**Status:** Accepted

### Context

Initial versions generated candidate locations on residential streets.

Visual inspection showed that many recommendations were placed inside narrow residential streets or dead-end roads despite having high healthcare demand nearby.

### Decision

Candidate generation is limited to higher-order roads:

- trunk
- primary
- secondary
- tertiary

### Consequences

**Positive**

- Better real-world accessibility.
- More realistic pharmacy locations.
- Approximately 80% reduction in candidate points.
- Faster pipeline execution.

**Trade-off**

Some residential neighborhoods may receive fewer candidate locations and should be evaluated in future versions using a dedicated accessibility model.

---

# D005 — Centralize All Model Parameters

**Status:** Accepted

### Context

Early versions stored parameters across several Python files, making calibration difficult.

### Decision

All model calibration parameters are stored in:

```
config/scoring.json
```

including:

- facility weights
- road bonuses
- search radius
- Gaussian decay
- competition radius
- score weights
- candidate selection parameters

### Consequences

The scoring model can now be calibrated without modifying Python source code.