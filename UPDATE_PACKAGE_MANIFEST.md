# Terafab Decision Twin Advanced Simulation Update Package

This overlay package adds two root-level directories to the existing repository:

```text
strategic_simulation/
validation_lab/
```

It is designed to be extracted at the repository root. It does not replace the deterministic `terafab_decision_twin` kernel. The advanced layer imports and reuses the existing package functions, especially `terafab_decision_twin.run_scenario()` and scenario validation.

## Added capabilities

- Monte Carlo uncertainty propagation over evidence-coded scenario values.
- Finite normal-form game analysis for stakeholder strategy assumptions.
- Transparent reduced-order model trajectory simulation.
- Stakeholder decision-surface synthesis for board, investor, policy, and research views.
- Validation-readiness checks: structure, public-reference ranges, and calibration-gap reporting.
- Tests for the advanced layer.
- Documentation and a lightweight advanced simulation notebook.

## Validation boundary

This update does not claim official Terafab validation, private-data calibration, investment advice, permitting adequacy, or real operating-data fidelity. It adds reproducible screening and validation-readiness tools that can later be calibrated with authoritative stakeholder data.

## Recommended post-extraction checks

```bash
python -m unittest discover -s tests
```

Expected result after extraction into the current repo state: existing tests continue to pass, and new advanced-layer tests pass.
