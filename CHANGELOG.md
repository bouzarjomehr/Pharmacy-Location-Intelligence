# Changelog

## Unreleased

### Fixed

- Population is now aggregated by summing all populated GHSL cells
  within the configurable `population.radius` around each candidate,
  as documented — previously only the single 100 m pixel under the
  candidate point was sampled, leaving ~25% of candidates with
  population 0 regardless of their surroundings.
- Phase 1 now correctly skips the Google import step when the raw
  Google Places file is absent (the skip check referenced an old
  script name and never fired).
- `main_reason` no longer considers the competition penalty as a
  possible positive driver of a location's rank.
- Removed dead configuration that silently had no effect:
  `score_weights` (the engine's provisional final score was always
  overwritten by the normalization stage), `competition_radius`,
  `facility_weights.Pharmacy` (any positive value cancels out during
  min-max normalization), and `road_bonus` entries for road types
  that can never become candidates. `population.normalization` is now
  actually read by the scoring engine.
- README corrected: orchestrator file names, output map file name,
  GHSL (not WorldPop) as the population source, dependency list.
- `requirements.txt` re-encoded as UTF-8.

## v1.0

- Initial public release.