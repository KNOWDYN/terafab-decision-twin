# Advanced Update Package QA Report

Package target: `update_package.zip`

## Scope

This overlay adds:

```text
strategic_simulation/
validation_lab/
docs/ADVANCED_SIMULATION.md
docs/VALIDATION_LAB.md
docs/STAKEHOLDER_DECISION_SURFACES.md
notebooks/terafab_advanced_simulation_lab.ipynb
tests/test_strategic_simulation.py
tests/test_validation_lab.py
pyproject.toml package-discovery update
```

## Validation performed before delivery

The overlay was copied into a fresh extraction of `terafab-decision-twin-main.zip` and tested from the repository root.

```text
python -m unittest discover -s tests
Ran 42 tests
OK
```

The 42 tests include the existing 34 tests plus 8 advanced-layer tests.

## Boundary

The update adds advanced screening capabilities. It does not claim official Terafab validation, private-data calibration, investment advice, or permitting adequacy.
