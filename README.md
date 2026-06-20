# Terafab Decision Twin

**Terafab Decision Twin** is a source-available Python package for scenario simulation of Terafab-scale semiconductor energy, heat, water, yield, cost, governance, and public-policy consequences.

It is built for a simple public decision problem: Terafab-scale planning cannot be judged from manufacturing ambition alone. At this scale, power capacity, heat rejection, cooling reserve, water withdrawal, wastewater discharge, yield learning, contamination loss, capex, opex, governance risk, and public legitimacy become one coupled system.

This repo turns labeled scenario assumptions into auditable consequences.

It is **not** verified Terafab operating data, not an official Terafab model, not a Terafab endorsement, not investment advice, not a permitting forecast, and not a claim of financing, construction, operation, acquisition interest, or adoption. It does not redistribute restricted source documents.

---

## Contents

- [What this repo does](#what-this-repo-does)
- [Who should use it](#who-should-use-it)
- [What questions it answers](#what-questions-it-answers)
- [Quick start](#quick-start)
- [CLI map](#cli-map)
- [Run the included scenarios](#run-the-included-scenarios)
- [Stakeholder workflows](#stakeholder-workflows)
- [Scenario system](#scenario-system)
- [Evidence discipline](#evidence-discipline)
- [Model architecture](#model-architecture)
- [Methods and equations](#methods-and-equations)
- [Outputs and gates](#outputs-and-gates)
- [Reports and export bundles](#reports-and-export-bundles)
- [Notebooks, docs site, and infographic](#notebooks-docs-site-and-infographic)
- [Build new simulations, scenarios, and case studies](#build-new-simulations-scenarios-and-case-studies)
- [Repository map](#repository-map)
- [Tests and release guards](#tests-and-release-guards)
- [What this repo does not claim](#what-this-repo-does-not-claim)
- [Licensing, ownership, and non-affiliation](#licensing-ownership-and-non-affiliation)
- [Citation](#citation)

---

## What this repo does

The package validates evidence-coded scenario JSON files, runs a time-step solver, computes thermodynamic and decision outputs, evaluates due-diligence gates, and exports reproducible decision material.

A typical run follows this path:

```text
scenario JSON
  -> schema validation
  -> evidence audit and status normalization
  -> unknown-value discipline
  -> time-axis expansion
  -> formal equation modules
  -> scalar/vector/matrix outputs
  -> due-diligence gate matrix
  -> JSON / Markdown / CSV export bundle
```

Core implemented files:

```text
terafab_decision_twin/engine.py       simulation coordinator
terafab_decision_twin/schema.py       scenario loading and validation
terafab_decision_twin/evidence.py     evidence-status audit and normalization
terafab_decision_twin/unknowns.py     unresolved-variable discipline
terafab_decision_twin/time_axis.py    annual, quarterly, and monthly periods
terafab_decision_twin/outputs.py      scalar/vector/matrix output registry
terafab_decision_twin/report.py       Markdown decision reports
terafab_decision_twin/cli.py          command-line interface
terafab_decision_twin/models/         equation modules and gates
```

Public package status:

```text
Package: terafab-decision-twin
Model version: 0.3.0
Python: >=3.10
Runtime dependencies: none
CLI entry point: terafab
```

Python API:

```python
from terafab_decision_twin import run_scenario, load_scenario, validate_scenario
```

---

## Who should use it

| Stakeholder | Use the repo to inspect | Primary repo paths |
|---|---|---|
| Engineering and executive board | Firm power margin, heat-rejection margin, cooling reserve, water and wastewater margins, yield, readiness, phase-gate action | `models/power.py`, `models/cooling.py`, `models/water.py`, `models/manufacturing.py`, `models/readiness.py`, `models/gates.py`, `models/real_options.py` |
| Investor or capital allocator | Annualized capex, opex, cost per good die, cost per compute watt, emissions cost, governance risk, gate failures | `models/economics.py`, `models/governance.py`, `outputs.py`, `report.py` |
| Public-policy observer | Water withdrawal, consumptive use, wastewater, emissions, public burden, public benefit, legitimacy margin, evidence labels | `models/water.py`, `models/power.py`, `models/policy.py`, `docs/EVIDENCE_POLICY.md` |
| Researcher or developer | Schema, equations, CLI, tests, docs, notebooks, scenario extensions | `schema/scenario_schema.json`, `docs/EQUATIONS.md`, `docs/ARCHITECTURE.md`, `docs/CLI.md`, `tests/`, `notebooks/` |

The model does not turn assumptions into facts. It turns labeled assumptions into auditable consequences.

---

## What questions it answers

### Physical feasibility

- Does firm power cover modeled site load plus reserve?
- Does cooling capacity cover first-law heat rejection after reserve?
- Do water withdrawal and wastewater discharge remain within modeled permit margins?

### Thermodynamic exposure

- How much heat must be rejected?
- What entropy generation and exergy destruction are implied?
- What average exergy efficiency appears under the scenario?

### Manufacturing exposure

- What effective yield results after learning and contamination loss?
- What modeled good-die output appears?
- What readiness bottleneck dominates the scenario?

### Economic exposure

- What annualized capex and total modeled cost appear?
- What cost per good die and cost per compute watt appear?
- How much do electricity, water, emissions, and capex terms contribute to modeled cost?

### Policy exposure

- Does modeled public benefit exceed modeled public burden?
- Is legitimacy margin positive or negative?
- Does governance risk breach the warning threshold?

### Strategic action

- Does the scenario support `advance`, `hold_or_redesign`, or `stage_and_monitor` as the modeled phase-gate action?
- Which gate failures block a scenario from being treated as decision-ready?

---

## Quick start

From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .

terafab scenario validate scenarios/baseline_2026.json
terafab simulate scenarios/baseline_2026.json \
  --output runs/baseline.json \
  --report runs/baseline.md

terafab outputs list
terafab export scenarios/baseline_2026.json runs/baseline_bundle
```

The package can also be installed normally:

```bash
python -m pip install .
```

---

## CLI map

```text
terafab schema show
terafab schema show --output schema/scenario_schema.copy.json

terafab scenario new <scenario_id> <output.json>
terafab scenario new <scenario_id> <output.json> --title "My Scenario" --scenario-type demonstration
terafab scenario validate <scenario.json>
terafab scenario validate <scenario.json> --strict

terafab simulate <scenario.json> --output result.json --report report.md
terafab gates <scenario.json>
terafab outputs list
terafab outputs list --kind scalar
terafab outputs list --kind vector
terafab outputs list --kind matrix
terafab report <scenario.json> --output report.md
terafab export <scenario.json> <output_dir>
terafab version
```

Exit codes:

```text
0  command succeeded and no error-level gate failed
1  validation or runtime error
2  scenario executed but at least one error-level gate failed
```

Backward-compatible v0.1 command aliases remain available, but the public command group above is the preferred interface.

---

## Run the included scenarios

The repo includes runnable scenario files under `scenarios/`.

| Scenario | Time basis | Purpose | Boundary |
|---|---:|---|---|
| `baseline_2026.json` | Annual 2026 | Baseline demonstration scenario | Uses scenario assumptions; not verified operating data |
| `terawatt_stress_2026.json` | Annual 2026 | One-terawatt stress test | Stress-test case; not verified site load |
| `multi_year_2026_2030.json` | Quarterly 2026-2030 | Multi-period staged demonstration | Demonstrates propagation and gates |
| `worst_case_2026_2030.json` | Quarterly 2026-2030 | Near-failure stress case | Explores adverse thermodynamic, economic, governance, and regulatory conditions |
| `best_case_2026_2030.json` | Quarterly 2026-2030 | Milestone-support case | Explores supportive thermodynamic, economic, governance, and regulatory conditions |

Examples:

```bash
terafab scenario validate scenarios/worst_case_2026_2030.json
terafab gates scenarios/worst_case_2026_2030.json
terafab export scenarios/best_case_2026_2030.json runs/best_case_bundle
```

---

## Stakeholder workflows

### Engineering and executive board workflow

Use the repo as a board-level due-diligence model for physical and operational feasibility.

```bash
terafab scenario validate scenarios/worst_case_2026_2030.json
terafab gates scenarios/worst_case_2026_2030.json
terafab export scenarios/worst_case_2026_2030.json runs/worst_case_board_pack
```

Inspect:

```text
minimum_firm_capacity_margin_MW
minimum_heat_rejection_margin_MW
minimum_water_withdrawal_margin_m3_per_day
minimum_wastewater_discharge_margin_m3_per_day
average_effective_yield
average_readiness_index
recommended_phase_action
gate_matrix.csv
report.md
```

Use this workflow to identify whether a scenario is blocked by power, heat, water, wastewater, yield, economics, evidence, or governance gates.

### Investor workflow

Use the repo as a pre-investment scenario diligence layer.

```bash
terafab export scenarios/baseline_2026.json runs/baseline_investor_pack
terafab export scenarios/terawatt_stress_2026.json runs/stress_investor_pack
```

Inspect:

```text
annualized_capex_USD
total_opex_USD
total_cost_USD
cost_per_good_die_USD
cost_per_compute_watt_USD
emissions_tCO2
maximum_governance_risk_index
legitimacy_margin
passed
```

The model does not predict Terafab's future. It tests whether a declared future is physically, economically, and institutionally coherent under explicit assumptions.

### Public-policy workflow

Use the repo to inspect public infrastructure burden and policy legitimacy under declared scenarios.

```bash
terafab export scenarios/multi_year_2026_2030.json runs/policy_review_pack
terafab export scenarios/worst_case_2026_2030.json runs/worst_case_policy_pack
terafab export scenarios/best_case_2026_2030.json runs/best_case_policy_pack
```

Inspect:

```text
water_withdrawal_m3
water_consumptive_use_m3
wastewater_m3
minimum_water_withdrawal_margin_m3_per_day
minimum_wastewater_discharge_margin_m3_per_day
emissions_tCO2
public_benefit_index
public_burden_index
legitimacy_margin
evidence status counts
assumptions used
unresolved variables
```

### Researcher and developer workflow

Use the repo as an auditable public model with schema, equations, tests, CLI, reports, and notebooks.

```bash
terafab schema show --output schema/scenario_schema.copy.json
terafab scenario new research_case scenarios/research_case.json --scenario-type demonstration
terafab scenario validate scenarios/research_case.json
python -m unittest discover -s tests
```

Start with:

```text
docs/ARCHITECTURE.md
docs/EQUATIONS.md
docs/EVIDENCE_POLICY.md
docs/OUTPUT_REGISTRY.md
docs/REPORTING.md
docs/TRACEABILITY.md
```

---

## Scenario system

Scenarios are JSON files validated against:

```text
schema/scenario_schema.json
terafab_decision_twin/data/scenario_schema.json
```

Required top-level sections:

```text
metadata
time
terafab_phase
energy
cooling
water
manufacturing
economics
governance
policy
control
```

Supported scenario types:

```text
baseline
stress_test
counterfactual
policy
sensitivity
multi_year
demonstration
```

Supported time steps:

```text
annual
quarterly
monthly
```

The `control.allowed_actions` field accepts:

```text
build
delay
scale
redesign
allocate
contract
license
partner
curtail
abandon
```

Control actions are validated as scenario metadata. The current engine evaluates phase-gate recommendations; it should not be described as a finished autonomous control optimizer.

---

## Evidence discipline

Every material scenario value must identify what kind of value it is, where it came from, and whether it may support a conclusion.

Evidence-coded input example:

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

Canonical evidence statuses:

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

Core evidence rules:

```text
A scenario value can drive a simulation without becoming a verified fact.
Scenario assumptions, stress tests, reported values, user inputs, confidential inputs, and derived outputs must not be promoted into verified project facts.
Material unknowns are recorded as unresolved and can make affected conclusions underdetermined.
Restricted source documents are excluded from the public repo.
One-terawatt cases are stress tests unless separately verified by admissible evidence.
```

Relevant files:

```text
terafab_decision_twin/evidence.py
docs/EVIDENCE_POLICY.md
sources/admitted_facts.json
sources/claim_register.json
sources/source_manifest.json
sources/unresolved_variables.json
sources/restricted_sources_exclusion.md
```

---

## Model architecture

The main execution path is coordinated by:

```text
terafab_decision_twin/engine.py
```

The central public function is:

```python
run_scenario(scenario: dict) -> dict
```

It returns a result object with:

```text
metadata
summary
time_series
gates
passed
evidence
unknowns
registries
matrices
formal_modules
interpretation
hashes
output_records
```

The implementation keeps specialized public model domains visible:

```text
terafab_decision_twin/cleanroom/
terafab_decision_twin/contamination/
terafab_decision_twin/packaging/
terafab_decision_twin/qualification/
terafab_decision_twin/evidence_bayes/
```

These are conservative public abstractions and do not imply access to private Terafab operating data.

---

## Methods and equations

Detailed equation coverage is documented in `docs/EQUATIONS.md`. The executable modules are under `terafab_decision_twin/models/`.

| Domain | Implemented modules | Outputs or role |
|---|---|---|
| Mass and species | `models/mass.py` | Species balance and campus mass residual helpers |
| First law / heat | `models/first_law.py` | Heat-rejection requirement |
| Entropy and exergy | `models/entropy.py`, `models/exergy.py` | Entropy generation, exergy destruction, exergy efficiency |
| Power | `models/power.py` | Energy consumption, firm-capacity margin, emissions, electricity cost |
| Cooling | `models/cooling.py` | Auxiliary cooling power, heat-rejection margin, cooling-tower evaporation helper |
| Water | `models/water.py` | Withdrawal, consumptive use, wastewater, UPW demand, permit margins |
| Manufacturing | `models/manufacturing.py` | Learned yield, effective yield, good-die output, compute-output proxy |
| Readiness | `models/readiness.py` | Readiness index and bottleneck logic |
| Economics | `models/economics.py` | Annualized capex, water cost, emissions cost, cost per good die, cost per compute watt |
| Governance | `models/governance.py` | Governance risk and governance readiness |
| Policy | `models/policy.py` | Public benefit, public burden, legitimacy margin |
| Real options | `models/real_options.py` | Phase-gate value and recommended phase action |
| Gates | `models/gates.py` | Due-diligence pass/fail gates |
| Optimization hooks | `models/optimize.py` | Public optimization boundary hooks |

Representative equations:

```text
Q_reject â‰ˆ W_e * heat_rejection_fraction + Q_waste - E_stored_product

firm_capacity_margin = firm_capacity - site_load * (1 + reserve_margin)

water_withdrawal = energy_MWh * withdrawal_intensity + UPW_demand

S_gen = Q * (1/T_c - 1/T_h)

X_destroyed = T_0 * S_gen

legitimacy_margin = public_benefit_index - public_burden_index
```

These equations are scenario equations, not verified operating measurements.

---

## Outputs and gates

Every simulation returns scalar, vector, and matrix outputs.

Registered scalar outputs include:

```text
energy_MWh
average_site_load_MW
peak_site_load_MW
minimum_firm_capacity_margin_MW
heat_rejection_required_MW
minimum_heat_rejection_margin_MW
cooling_auxiliary_energy_MWh
entropy_generation_MW_per_K
exergy_destroyed_MW
average_exergy_efficiency
water_withdrawal_m3
water_consumptive_use_m3
wastewater_m3
minimum_water_withdrawal_margin_m3_per_day
minimum_wastewater_discharge_margin_m3_per_day
good_die
compute_output_proxy_W
average_effective_yield
average_readiness_index
annualized_capex_USD
total_opex_USD
total_cost_USD
cost_per_good_die_USD
cost_per_compute_watt_USD
emissions_tCO2
public_benefit_index
public_burden_index
legitimacy_margin
maximum_governance_risk_index
```

Vector outputs are held in `time_series`. Matrix outputs include:

```text
gate_matrix
module_output_matrix
partner_allocation_matrix
subsystem_state_matrix
```

Gate checks include:

```text
unknown_input_discipline
dimensional
thermodynamic_heat_rejection
power_firm_capacity
water_withdrawal_permit
wastewater_discharge_permit
manufacturing_yield
economic_finiteness
policy_legitimacy
governance_risk
evidence
```

The model passes only when no error-level gate fails.

---

## Reports and export bundles

Generate a Markdown report:

```bash
terafab report scenarios/baseline_2026.json --output runs/baseline_2026.md
```

Generate a full export bundle:

```bash
terafab export scenarios/baseline_2026.json runs/baseline_bundle
```

Export bundles contain:

```text
result.json
report.md
summary.csv
gate_matrix.csv
```

Reports are designed as decision records. They include scenario identity, model/schema/source-bundle versions, executive status, key scalar outputs, gate results, evidence-status counts, assumptions, unresolved variables, formal module outputs, reproducibility hashes, limitations, rights, and non-affiliation boundaries.

Relevant files:

```text
terafab_decision_twin/report.py
terafab_decision_twin/cli.py
docs/REPORTING.md
```

---

## Notebooks, docs site, and infographic

The repo includes a GitHub Pages-ready `/docs` site layer:

```text
docs/index.html
docs/getting-started.html
docs/model.html
docs/scenarios.html
docs/evidence.html
docs/policy.html
docs/researchers.html
```

Technical docs include:

```text
docs/ARCHITECTURE.md
docs/EQUATIONS.md
docs/CLI.md
docs/EVIDENCE_POLICY.md
docs/OUTPUT_REGISTRY.md
docs/REPORTING.md
docs/TRACEABILITY.md
```

Colab notebooks:

```text
notebooks/terafab_colab_dashboard.ipynb
notebooks/terafab_comparative_simulation_reporting_colab.ipynb
```

Public infographic assets:

```text
assets/terafab_one_page_infographic.svg
assets/terafab_one_page_infographic.png
assets/terafab_one_page_infographic.pdf
```

The `/docs` site is included in the repository. Publication status depends on repository hosting and GitHub Pages configuration.

---

## Build new simulations, scenarios, and case studies

A new case study should begin as a scenario file, not as an unlabeled narrative.

### 1. Choose the case purpose

```text
baseline
stress_test
counterfactual
policy
sensitivity
multi_year
demonstration
```

Examples:

```text
Board diligence case:
  Test whether heat, power, water, and yield gates survive a proposed scale-up.

Investor case:
  Compare baseline, stress, and milestone-support assumptions for cost and governance exposure.

Policy case:
  Inspect water, emissions, public burden, public benefit, and legitimacy margin.

Research case:
  Extend an equation module and add tests.
```

### 2. Create or copy a scenario

```bash
terafab scenario new board_case scenarios/board_case.json --scenario-type demonstration
```

Or copy one of:

```text
scenarios/baseline_2026.json
scenarios/multi_year_2026_2030.json
scenarios/worst_case_2026_2030.json
scenarios/best_case_2026_2030.json
```

### 3. Edit evidence-coded inputs

Keep every material number wrapped with:

```text
value
unit
status
source_ref
confidence
notes
```

Do not relabel assumptions as verified facts merely because they are useful to the scenario.

### 4. Validate

```bash
terafab scenario validate scenarios/board_case.json
terafab scenario validate scenarios/board_case.json --strict
```

### 5. Simulate

```bash
terafab simulate scenarios/board_case.json \
  --output runs/board_case.json \
  --report runs/board_case.md
```

### 6. Export decision material

```bash
terafab export scenarios/board_case.json runs/board_case_bundle
```

### 7. Compare scenarios

Use:

```text
notebooks/terafab_comparative_simulation_reporting_colab.ipynb
```

The comparative notebook is designed for baseline / stress / support-style scenario comparison and policymaker-investor reporting.

### 8. Extend with tests

When adding or changing equations, add tests under:

```text
tests/
```

Then run:

```bash
python -m unittest discover -s tests
```

---

## Repository map

```text
terafab_decision_twin/
  Python package: engine, schema, evidence, unknowns, outputs, reports, CLI, units, and time axis.

terafab_decision_twin/models/
  Formal modules for mass, first law, entropy, exergy, power, cooling, water, manufacturing, readiness,
  economics, governance, policy, real options, gates, and optimization hooks.

terafab_decision_twin/cleanroom/
terafab_decision_twin/contamination/
terafab_decision_twin/packaging/
terafab_decision_twin/qualification/
terafab_decision_twin/evidence_bayes/
  Conservative public boundaries for specialized model domains.

schema/
  Public scenario schema.

scenarios/
  Included runnable scenarios.

notebooks/
  Colab dashboard and comparative scenario reporting notebook.

docs/
  GitHub Pages-ready public site and technical documentation.

sources/
  Public source-governance files: admitted facts, claim register, source manifest, unresolved variables,
  and restricted-source exclusion.

assets/
  One-page public infographic assets.

tests/
  Unit tests for schema, engine, equations, evidence, CLI behavior, and release guards.

.github/workflows/
  Tests, scenario schema validation, docs-link guard, and restricted-source guard workflows.
```

---

## Tests and release guards

Run the test suite:

```bash
python -m unittest discover -s tests
```

The included tests cover:

```text
schema validation
engine behavior
equation behavior
evidence discipline
CLI behavior
release guards
```

The repository also includes GitHub Actions workflows for:

```text
.github/workflows/tests.yml
.github/workflows/schema.yml
.github/workflows/docs-links.yml
.github/workflows/restricted-source-guard.yml
```

Restricted-source guard files:

```text
sources/restricted_sources_exclusion.md
FINAL_RESTRICTED_SOURCE_SCAN.json
```

The public package excludes named restricted source documents and allows only the infographic PDF under `assets/` as a committed PDF asset.

---

## What this repo does not claim

This repo should not be read as claiming any of the following:

```text
verified Terafab operating data
official Terafab endorsement or authorization
Terafab employee involvement
private facility telemetry
real-time digital-twin operation
construction status
permitting status
financing status
acquisition interest
investment recommendation
permitting recommendation
guaranteed 2026-2030 forecast
calibrated industrial simulator
finished autonomous control optimizer
```

The package is a public, executable, evidence-gated scenario simulator. Its conclusions are conditional on the scenario inputs and evidence labels supplied to it.

---

## Licensing, ownership, and non-affiliation

Copyright (c) 2026 KNOWDYN.

All rights are reserved except as expressly granted in `LICENSE.md`. Commercial rights require a separate written commercial license from KNOWDYN. See:

```text
LICENSE.md
LICENSE-ACADEMIC.md
LICENSE-COMMERCIAL.md
NOTICE.md
```

Terafab is owned by its official entity. This package is independent and is not affiliated with, endorsed by, authorized by, sponsored by, or connected to Terafab or its employees.

---

## Citation

Citation metadata is provided in:

```text
CITATION.cff
```

When using the package in research, policy analysis, or public discussion, cite the repository and preserve evidence-status boundaries in any derived claims.
