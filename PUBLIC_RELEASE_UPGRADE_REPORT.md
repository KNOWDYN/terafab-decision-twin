# Public-Release Readiness Upgrade Report

Scope: Python package only. The GitHub Pages site was not merged, and no final public-release ZIP was produced in this pass.

## Implemented upgrades

1. Evidence/schema hardening
   - Replaced v0.1 evidence dialect with canonical statuses: `verified_project_fact`, `model_identity`, `filed_claimed`, `reported`, `user_provided`, `scenario_assumption`, `stress_test_assumption`, `unknown`, `confidential_private_input`, and `derived_output`.
   - Added alias normalization for v0.1 terms such as `verified_fact`, `filed_claim`, `reported_claim`, `user_input`, `assumption`, and `confidential_input`.
   - Made material scenario inputs require evidence-coded objects with `value`, `unit`, `status`, `source_ref`, `confidence`, and `notes`.
   - Expanded scenario metadata fields and control action validation.

2. Unknown-value discipline
   - Added explicit underdetermination tracking.
   - Unknown material inputs now produce unresolved-variable records, failed `unknown_input_discipline` gates, and underdetermined cost outputs instead of silently becoming numeric defaults.

3. Formal module coverage
   - Added first-class public modules for `cleanroom`, `contamination`, `packaging`, `qualification`, and `evidence_bayes`.
   - Integrated cleanroom, contamination, packaging, and qualification readiness proxies into the main simulation engine.
   - Added Bayesian update logic with a no-auto-verification rule.

4. Reserve-margin conventions
   - Preserved power convention: firm capacity must cover `peak_load * (1 + reserve_margin)`.
   - Added cooling and water conventions: demand must remain below `capacity * (1 - reserve_margin)`.
   - Added cooling, withdrawal, and wastewater reserve-margin fields to sample scenarios.

5. Output metadata and matrices
   - Added scalar/vector/matrix registries.
   - Added `output_records` with units, source status, equation references, assumptions used, warning flags, and reproducibility hashes.
   - Added `gate_matrix`, `module_output_matrix`, `partner_allocation_matrix`, and `subsystem_state_matrix`.

6. Reports and interpretation guardrails
   - Expanded Markdown reports with scenario identity, evidence summary, assumptions, unresolved variables, formal module outputs, can/cannot conclude sections, high-value next-data fields, and reproducibility hashes.

7. CLI expansion
   - Added blueprint-aligned commands: `schema show`, `scenario new`, `scenario validate`, `simulate`, `gates`, `outputs list`, `report`, `export`, and `version`.
   - Preserved v0.1 aliases: `validate` and `run`.

8. Source governance and rights files
   - Added/updated `admitted_facts.json`, `source_manifest.json`, `claim_register.json`, `unresolved_variables.json`, and restricted-source exclusion policy.
   - Added KNOWDYN-aligned `LICENSE.md`, `LICENSE-ACADEMIC.md`, `LICENSE-COMMERCIAL.md`, `NOTICE.md`, and `CITATION.cff`.

9. CI and tests
   - Added GitHub Actions workflows for tests, scenario validation/export, and restricted-source guard.
   - Expanded tests from 16 to 28.

## Validation

```text
python -m unittest discover -s tests -v
Ran 28 tests
OK
```

Additional smoke checks:

```text
python -m terafab_decision_twin.cli schema show
python -m terafab_decision_twin.cli outputs list
python -m terafab_decision_twin.cli export scenarios/baseline_2026.json /tmp/terafab_export
```

Export files produced: `result.json`, `report.md`, `summary.csv`, `gate_matrix.csv`.

## Remaining before final public ZIP

- Review and optionally polish long-form documentation.
- Decide whether to add infographic assets to the Python repo, or keep visual material only in the GitHub Pages layer.
- Merge the final `/docs` website only after package review.
- Run one final restricted-source scan before packaging the public ZIP.
