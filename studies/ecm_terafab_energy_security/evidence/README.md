# Step 2 Evidence Foundation

This directory is the frozen public-evidence and parameter foundation for the
`ecm_terafab_us_energy_security` study. It supports a prospective constraint
analysis. It does not contain verified Terafab operating data and does not
establish affiliation, endorsement, engineering certification, or an official
feasibility determination.

## Evidence rules

- Public project statements are claims or filed claims, not operating facts.
- `1 TW/year` is an annual production target interpretation, never a facility
  electrical load.
- Parameters derived from comparator products or facilities remain reference
  ranges or scenario assumptions; they are not promoted to Terafab facts.
- Unknown project values remain `null` and may trigger an indeterminate result.
- Final paper runs use only frozen extracted datasets in `snapshots/`; they do
  not retrieve live web content.
- Every extracted snapshot is hashed in `snapshot_manifest.json`.

## Contents

- `source_registry.json`: bibliographic, provenance, and admissibility records.
- `parameter_registry.json`: calculation inputs, bounds, roles, and evidence
  status.
- `uncertainty_dependencies.json`: distributions and dependence rules fixed
  before simulations.
- `validation_contract.json`: calibration/validation separation and locked
  acceptance thresholds.
- `evidence_review.md`: decisions on the six empirical kill tests and the
  resulting permissible scientific claim.
- `snapshots/`: small, machine-readable extractions from admitted public data.
- `snapshot_manifest.json`: SHA-256 checksums for the frozen extractions.
- `validate_evidence.py`: offline structural and cross-reference validator.

The repository is source-available, not open-source software. Use remains
subject to the root Academic and Commercial licenses.
