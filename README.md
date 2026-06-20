# Terafab Decision Twin

**Terafab Decision Twin** is a source-available, evidence-gated, forward-looking simulation package for testing Terafab-scale consequences across U.S. energy, water, semiconductor manufacturing, economics, governance, and public-policy systems.

The repository implements a runnable v1 of the locked Terafab Decision Twin blueprint. It does **not** claim access to proprietary Terafab operating data, does **not** redistribute restricted project sources, and does **not** promote scenario assumptions into verified facts.

## What this repo does

The package lets users:

- define scenarios through `schema/scenario_schema.json`;
- validate scenario structure and evidence status;
- run a time-step decision-twin solver from 2026 onward;
- compute thermodynamic, exergy, cooling, water, yield, economic, governance, readiness, and policy outputs;
- apply due-diligence gates before interpreting results;
- export JSON and Markdown reports;
- reproduce sample baseline and stress-test runs.

## What this repo does not do

This repo does not assert that any Terafab site is financed, permitted, contracted, operational, connected to a specific grid node, consuming a specific verified water volume, or running at a verified one-terawatt electrical load. One terawatt is treated only as a declared scenario or stress-test assumption unless verified evidence is later supplied.

## Install and run locally

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
terafab validate scenarios/baseline_2026.json
terafab run scenarios/baseline_2026.json --output runs/baseline_2026.json --report runs/baseline_2026.md
terafab gates scenarios/terawatt_stress_2026.json
```

Without installing:

```bash
python -m terafab_decision_twin.cli validate scenarios/baseline_2026.json
python -m terafab_decision_twin.cli run scenarios/baseline_2026.json --output runs/baseline_2026.json
```

## Repository map

```text
terafab-decision-twin/
├── README.md
├── pyproject.toml
├── LICENSE.md
├── schema/scenario_schema.json
├── scenarios/
│   ├── baseline_2026.json
│   ├── terawatt_stress_2026.json
│   └── multi_year_2026_2030.json
├── terafab_decision_twin/
│   ├── cli.py
│   ├── engine.py
│   ├── evidence.py
│   ├── schema.py
│   ├── report.py
│   ├── outputs.py
│   └── models/
├── tests/
├── docs/
└── sources/
```

## Model structure

A scenario is evaluated as:

```text
verified facts + declared assumptions + time-step solver
→ thermodynamics + exergy + power + water + yield + economics + governance + policy
→ outputs + gates + reproducibility bundle
```

The implementation preserves the blueprint's core gates:

- dimensional sanity;
- thermodynamic heat-rejection realism;
- power and firm-capacity adequacy;
- water withdrawal and discharge permit margins;
- manufacturing yield and readiness;
- cost sanity;
- policy/public-benefit sanity;
- governance complexity risk;
- evidence-status discipline.

## Evidence discipline

Every scenario input may be given as a scalar or as an evidence-coded object:

```json
{
  "value": 150,
  "unit": "MW",
  "status": "assumption",
  "source": "scenario author",
  "rationale": "Declared v1 baseline input; not a verified Terafab operating value."
}
```

Allowed statuses are listed in `terafab_decision_twin/evidence.py` and the JSON schema. A `verified_fact` must carry a source. Unverified values are allowed only as declared assumptions, reported claims, filed claims, stress tests, user inputs, unknowns, or confidential inputs.

## Reproducibility

Every run returns:

- scenario metadata;
- normalized inputs;
- time-indexed outputs;
- scalar summary outputs;
- gate pass/fail status;
- evidence warnings;
- SHA-256 hashes for scenario and result payloads.

## Restricted-source policy

The package intentionally excludes restricted/non-redistributable project documents. `sources/source_manifest.json` records source categories and redistribution status without embedding restricted source text.
