# Terafab Decision Twin

**Terafab Decision Twin** is a source-available KNOWDYN Python package for evidence-gated scenario analysis of Terafab-scale semiconductor energy, water, exergy, yield, economics, governance, and policy consequences.

It is a public strategic model, not a claim of verified Terafab operating data. It does not redistribute restricted source documents and does not imply Terafab endorsement, authorization, employee involvement, acquisition interest, financing, permitting, construction, or adoption.

## What the package does

- validates evidence-coded scenarios against `schema/scenario_schema.json`;
- runs 2026-forward simulations through a time-step solver;
- computes power, cooling, water, exergy, yield, readiness, cost, governance, policy, and real-option outputs;
- separates verified project facts, model identity, filed claims, reported claims, user-provided values, scenario assumptions, stress-test assumptions, unknowns, confidential private inputs, and derived outputs;
- fails or marks outputs as underdetermined when material values are unknown;
- emits scalar, vector, and matrix outputs with metadata and reproducibility hashes;
- exports JSON, Markdown, CSV summaries, and gate matrices.

## What it does not do

- It does not verify any Terafab site load, water permit, yield, cost, financing, grid interconnection, or operating status.
- It does not convert stress tests or assumptions into facts.
- It does not include restricted or proprietary Terafab source documents.
- It does not claim affiliation with Terafab or its employees.

## Package status

Public release: `0.3.0`.

This public-release package includes the runnable Python model and the GitHub Pages `/docs` site layer. It remains evidence-gated and source-governed.

## Public website

The GitHub Pages site is included under `/docs` and is designed to publish at:

```text
https://knowdyn.github.io/terafab-decision-twin/
```

It is a minimal public landing site with one external call to action: the GitHub repository icon.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
terafab scenario validate scenarios/baseline_2026.json
terafab simulate scenarios/baseline_2026.json --output runs/baseline.json --report runs/baseline.md
terafab outputs list
terafab export scenarios/baseline_2026.json runs/baseline_bundle
```

Legacy v0.1 aliases still work:

```bash
terafab validate scenarios/baseline_2026.json
terafab run scenarios/baseline_2026.json
```

## CLI map

```text
terafab schema show
terafab scenario new <scenario_id> <output.json>
terafab scenario validate <scenario.json>
terafab simulate <scenario.json> --output result.json --report report.md
terafab gates <scenario.json>
terafab outputs list
terafab report <scenario.json>
terafab export <scenario.json> <output_dir>
terafab version
```

## Evidence-coded input format

Material scenario values must be evidence-coded:

```json
{
  "value": 150,
  "unit": "MW",
  "status": "scenario_assumption",
  "source_ref": "scenario_author",
  "confidence": "declared",
  "notes": "Scenario-declared value; not a verified Terafab operating fact."
}
```

Canonical statuses:

```text
verified_project_fact
model_identity
filed_claimed
reported
user_provided
scenario_assumption
stress_test_assumption
unknown
confidential_private_input
derived_output
```

## Public-release model boundaries

The package contains first-class formal modules for:

```text
cleanroom
contamination
packaging
qualification
evidence_bayes
```

These modules are intentionally evidence-aware and conservative. They provide formal public model boundaries without pretending to hold private Terafab operating data.

## Outputs and gates

Every simulation returns:

- `summary`: high-level scalar outputs;
- `time_series`: time-indexed vectors;
- `output_records`: scalar output metadata, units, equation refs, assumptions, warnings, and hashes;
- `matrices.gate_matrix`: gate-by-time pass/fail structure;
- `matrices.module_output_matrix`: module output table;
- `matrices.partner_allocation_matrix`: governance allocation matrix;
- `matrices.subsystem_state_matrix`: power/cooling/water/readiness state matrix;
- `unknowns`: unresolved variables and underdetermination policy;
- `evidence`: assumptions, verified/reported inputs, warnings, and errors.

## Visual summary

A one-page public infographic is included in `assets/terafab_one_page_infographic.svg`, `assets/terafab_one_page_infographic.png`, and `assets/terafab_one_page_infographic.pdf`. It summarizes the public model boundary without asserting verified Terafab operating data.

## Licensing and ownership

Copyright (c) 2026 KNOWDYN. All rights reserved except as expressly granted in `LICENSE.md`.

Commercial rights require a separate written license from KNOWDYN. Terafab is owned by its official entity. This package is independent and is not affiliated with, endorsed by, authorized by, sponsored by, or connected to Terafab or its employees.
