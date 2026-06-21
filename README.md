# Terafab Decision Twin

**Terafab Decision Twin** is a source-available Python package for scenario simulation of Terafab-scale semiconductor energy, heat, water, yield, cost, governance, and public-policy consequences.

It is built for a simple public decision problem: Terafab-scale planning cannot be judged from manufacturing ambition alone. At this scale, power capacity, heat rejection, cooling reserve, water withdrawal, wastewater discharge, yield learning, contamination loss, capex, opex, governance risk, and public legitimacy become one coupled system.

This repo turns labeled scenario assumptions into auditable consequences.

The base package is a deterministic, evidence-gated decision twin. The advanced update adds two root-level overlay packages:

```text
strategic_simulation/
validation_lab/
```

Together they extend the repo from single-scenario deterministic analysis into uncertainty propagation, stakeholder strategy analysis, reduced-order trajectory simulation, stakeholder decision-surface synthesis, and validation-readiness screening.

It is **not** verified Terafab operating data, not an official Terafab model, not a Terafab endorsement, not investment advice, not a permitting forecast, and not a claim of financing, construction, operation, acquisition interest, adoption, real-time operation, private-data calibration, or official validation. It does not redistribute restricted source documents.

---

## Contents

- [What this repo does](#what-this-repo-does)
- [Who should use it](#who-should-use-it)
- [What questions it answers](#what-questions-it-answers)
- [Quick start](#quick-start)
- [CLI map](#cli-map)
- [Run the included scenarios](#run-the-included-scenarios)
- [Advanced simulation and validation update](#advanced-simulation-and-validation-update)
- [Monte Carlo uncertainty propagation](#monte-carlo-uncertainty-propagation)
- [Game-theory stakeholder analysis](#game-theory-stakeholder-analysis)
- [Reduced-order model simulation](#reduced-order-model-simulation)
- [Stakeholder decision surfaces](#stakeholder-decision-surfaces)
- [Validation lab](#validation-lab)
- [Stakeholder workflows](#stakeholder-workflows)
- [Scenario system](#scenario-system)
- [Evidence discipline](#evidence-discipline)
- [Model architecture](#model-architecture)
- [Methods and equations](#methods-and-equations)
- [Outputs and gates](#outputs-and-gates)
- [Reports and export bundles](#reports-and-export-bundles)
- [Notebooks, docs site, and infographic](#notebooks-docs-site-and-infographic)
- [Build new simulations, scenarios, and case studies](#build-new-simulations-scenarios-and-case-studies)
- [Build advanced simulations and validation studies](#build-advanced-simulations-and-validation-studies)
- [Repository map](#repository-map)
- [Tests and release guards](#tests-and-release-guards)
- [What this repo does not claim](#what-this-repo-does-not-claim)
- [Licensing, ownership, and non-affiliation](#licensing-ownership-and-non-affiliation)
- [Citation](#citation)

---

## What this repo does

The package validates evidence-coded scenario JSON files, runs a time-step solver, computes thermodynamic and decision outputs, evaluates due-diligence gates, and exports reproducible decision material.

A typical deterministic run follows this path:

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

The advanced update keeps the deterministic model as the kernel and adds this path:

```text
scenario JSON
  -> terafab_decision_twin.validate_scenario()
  -> terafab_decision_twin.run_scenario()
  -> strategic_simulation/monte_carlo.py
  -> strategic_simulation/game_theory.py
  -> strategic_simulation/reduced_order_model.py
  -> strategic_simulation/stakeholder_surface.py
  -> validation_lab/
  -> advanced screening outputs and stakeholder decision surfaces
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
strategic_simulation/                 advanced simulation overlay
validation_lab/                       validation-readiness overlay
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

Advanced overlay API:

```python
from strategic_simulation import (
    run_monte_carlo,
    sample_distribution,
    analyze_normal_form_game,
    simulate_reduced_order_model,
    build_stakeholder_decision_surface,
)

from validation_lab import (
    validate_result_structure,
    validate_reference_ranges,
    validation_scorecard,
    build_validation_report,
)
```

---

## Who should use it

| Stakeholder | Use the repo to inspect | Primary repo paths |
|---|---|---|
| Engineering and executive board | Firm power margin, heat-rejection margin, cooling reserve, water and wastewater margins, yield, readiness, phase-gate action, probability of gate failure, reduced-order stress trajectory | `models/power.py`, `models/cooling.py`, `models/water.py`, `models/manufacturing.py`, `models/readiness.py`, `models/gates.py`, `models/real_options.py`, `strategic_simulation/monte_carlo.py`, `strategic_simulation/reduced_order_model.py` |
| Investor or capital allocator | Annualized capex, opex, cost per good die, cost per compute watt, emissions cost, governance risk, gate failures, cost quantiles, conflict index | `models/economics.py`, `models/governance.py`, `outputs.py`, `report.py`, `strategic_simulation/monte_carlo.py`, `strategic_simulation/game_theory.py`, `strategic_simulation/stakeholder_surface.py` |
| Public-policy observer | Water withdrawal, consumptive use, wastewater, emissions, public burden, public benefit, legitimacy margin, evidence labels, range flags, validation-readiness | `models/water.py`, `models/power.py`, `models/policy.py`, `docs/EVIDENCE_POLICY.md`, `validation_lab/`, `docs/VALIDATION_LAB.md` |
| Researcher or developer | Schema, equations, CLI, tests, docs, notebooks, scenario extensions, uncertainty sampling, game analysis, ROM trajectories, validation reports | `schema/scenario_schema.json`, `docs/EQUATIONS.md`, `docs/ARCHITECTURE.md`, `docs/CLI.md`, `docs/ADVANCED_SIMULATION.md`, `docs/VALIDATION_LAB.md`, `tests/`, `notebooks/` |

The model does not turn assumptions into facts. It turns labeled assumptions into auditable consequences. The advanced layer does not turn uncertainty into truth; it propagates declared uncertainty, declared payoffs, and declared reduced-order dynamics through an inspectable model.

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

### Advanced uncertainty questions

- Under declared uncertainty ranges, how often does a scenario pass or fail?
- Which gates fail most often across sampled futures?
- What p10, p50, and p90 ranges appear for cost, yield, emissions, water, power margin, heat margin, and legitimacy?
- Which uncertain inputs appear most associated with a selected output metric?

### Stakeholder strategy questions

- Which actor strategy profiles are pure-strategy Nash equilibria under declared payoff assumptions?
- Which actor has which best responses?
- Does the declared game contain coordination failure?
- How high is the strategic conflict index?

### Reduced-order trajectory questions

- How does a low-dimensional system state evolve under declared coupling matrices and control actions?
- Do power stress, heat-rejection stress, water stress, yield maturity, and policy legitimacy move toward or away from acceptable regions?
- Does the reduced-order model trigger a stability or boundary warning?

### Validation-readiness questions

- Does a result contain the required output structure?
- Are key outputs finite and within declared screening ranges?
- Which calibration gaps remain before the model could be treated as expert-validated?
- What validation level is supported by current public evidence and available inputs?

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

Run the deterministic test suite and advanced-layer tests:

```bash
python -m unittest discover -s tests
```

Expected result after the advanced update is applied to the current repo state:

```text
Ran 42 tests
OK
```

The 42 tests include the original deterministic package tests plus the advanced simulation and validation-lab tests.

---

## CLI map

The deterministic package is exposed through the `terafab` CLI:

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

The advanced update is provided as Python modules and a notebook, not as new CLI commands. Use:

```text
strategic_simulation/
validation_lab/
notebooks/terafab_advanced_simulation_lab.ipynb
```

for Monte Carlo, game-theory, reduced-order-model, stakeholder-surface, and validation-readiness workflows.

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

## Advanced simulation and validation update

The advanced update adds two root-level packages:

```text
strategic_simulation/
validation_lab/
```

It also adds:

```text
docs/ADVANCED_SIMULATION.md
docs/VALIDATION_LAB.md
docs/STAKEHOLDER_DECISION_SURFACES.md
notebooks/terafab_advanced_simulation_lab.ipynb
tests/test_strategic_simulation.py
tests/test_validation_lab.py
UPDATE_PACKAGE_MANIFEST.md
ADVANCED_UPDATE_QA_REPORT.md
```

The update extends the existing model without replacing it:

```text
Existing repo:
  one declared scenario -> deterministic evidence-gated result

Advanced update:
  uncertainty distributions + strategy assumptions + reduced-order dynamics
    -> many plausible futures
    -> strategic interaction analysis
    -> trajectory screening
    -> stakeholder decision surfaces
    -> validation-readiness report
```

The advanced update is intentionally dependency-free. It uses the Python standard library and the existing `terafab_decision_twin` package. The Colab notebook may use notebook-side convenience libraries if the user chooses to add them, but the repo core does not require them.

Advanced example files:

```text
strategic_simulation/examples/uncertainty_baseline_2026.json
strategic_simulation/examples/strategic_game_2026.json
strategic_simulation/examples/rom_transition_2026_2030.json
strategic_simulation/examples/integrated_advanced_2026_2030.json
validation_lab/examples/public_reference_validation_case.json
```

These examples are demonstrations. They do not claim official stakeholder preferences, official utility commitments, official water-authority conclusions, official permitting outcomes, or private Terafab calibration.

---

## Monte Carlo uncertainty propagation

Monte Carlo propagates declared uncertainty through the deterministic model.

It supports dependency-free distributions:

```text
fixed
uniform
triangular
normal_clipped
lognormal
discrete
```

Primary module:

```text
strategic_simulation/monte_carlo.py
```

Example configuration:

```text
strategic_simulation/examples/uncertainty_baseline_2026.json
```

Python example:

```python
import json
from pathlib import Path
from strategic_simulation import run_monte_carlo

config = json.loads(
    Path("strategic_simulation/examples/uncertainty_baseline_2026.json").read_text()
)

result = run_monte_carlo(
    "scenarios/baseline_2026.json",
    config,
    retain_runs=False,
)

print(result["runs_completed"])
print(result["passed_probability"])
print(result["gate_failure_probability"])
print(result["metric_quantiles"]["total_cost_USD"])
```

Monte Carlo outputs include:

```text
runs_requested
runs_completed
passed_probability
failed_probability
gate_failure_probability
metric_quantiles
sensitivity
```

Typical stakeholder uses:

```text
Board:
  Estimate gate-failure probability across declared engineering uncertainty.

Investor:
  Inspect p10/p50/p90 cost, yield, and phase-risk exposure.

Policy observer:
  Inspect the probability of water, wastewater, emissions, or legitimacy stress.

Researcher:
  Study which uncertain parameters most affect selected outputs.
```

Boundary:

```text
Monte Carlo does not turn assumptions into facts. It only propagates declared uncertainty through the evidence-gated deterministic model.
```

---

## Game-theory stakeholder analysis

The game-theory layer analyzes declared stakeholder actors, strategies, and payoffs.

Primary module:

```text
strategic_simulation/game_theory.py
```

Example configuration:

```text
strategic_simulation/examples/strategic_game_2026.json
```

Capabilities:

```text
finite normal-form games
actor strategy enumeration
payoff lookup
best-response calculation
pure-strategy Nash-equilibrium detection
coordination-failure warnings
conflict index
policy-alignment interpretation
```

Python example:

```python
import json
from pathlib import Path
from strategic_simulation import analyze_normal_form_game

config = json.loads(
    Path("strategic_simulation/examples/strategic_game_2026.json").read_text()
)

game = analyze_normal_form_game(config)

print(game["actors"])
print(game["pure_strategy_nash_equilibria"])
print(game["conflict_index"])
print(game["coordination_failures"])
```

Typical stakeholder uses:

```text
Board:
  Inspect whether sponsor strategy and utility/regulatory strategy are aligned or conflict-prone.

Investor:
  Inspect whether funding depends on fragile coordination between actors.

Policy observer:
  Inspect whether public-policy alignment requires conditional commitments.

Researcher:
  Explore how different payoff assumptions change equilibrium profiles.
```

Boundary:

```text
The game-theory layer does not claim to know real stakeholder preferences. Payoffs are declared scenario assumptions unless separately sourced and documented.
```

---

## Reduced-order model simulation

The reduced-order model simulates a transparent low-dimensional system state.

Primary module:

```text
strategic_simulation/reduced_order_model.py
```

Example configuration:

```text
strategic_simulation/examples/rom_transition_2026_2030.json
```

Core reduced-order equation:

```text
x[t+1] = A x[t] + B u[t] + c + shock[t]
```

Example state variables:

```text
power_stress
heat_rejection_stress
water_stress
yield_maturity
policy_legitimacy
```

Example control variables:

```text
grid_upgrade
cooling_redesign
water_reuse
yield_learning_program
community_benefit_package
```

Python example:

```python
import json
from pathlib import Path
from strategic_simulation import simulate_reduced_order_model

config = json.loads(
    Path("strategic_simulation/examples/rom_transition_2026_2030.json").read_text()
)

rom = simulate_reduced_order_model(config)

print(rom["state_variables"])
print(rom["final_state"])
print(rom["diagnostics"])
```

Typical stakeholder uses:

```text
Board:
  See whether modeled controls reduce power, heat, and water stress over time.

Investor:
  Inspect whether cost and maturity proxies move toward a lower-risk state.

Policy observer:
  Inspect whether water reuse, staged development, or community-benefit controls improve legitimacy.

Researcher:
  Test transparent coupling matrices and stability diagnostics.
```

Boundary:

```text
The reduced-order model is a decision abstraction. It is not a high-fidelity fab physics simulator and does not replace engineering design, utility studies, or permitting analysis.
```

---

## Stakeholder decision surfaces

A stakeholder decision surface combines:

```text
Monte Carlo result
game-theory result
reduced-order-model trajectory
validation-lab report
```

Primary module:

```text
strategic_simulation/stakeholder_surface.py
```

Documentation:

```text
docs/STAKEHOLDER_DECISION_SURFACES.md
```

Python example:

```python
from strategic_simulation import build_stakeholder_decision_surface

surface = build_stakeholder_decision_surface(
    monte_carlo=mc_result,
    game=game_result,
    rom=rom_result,
    validation=validation_report,
)

print(surface["board_view"])
print(surface["investor_view"])
print(surface["policy_view"])
print(surface["research_view"])
```

The four views are:

```text
board_view
  gate-failure probability, dominant gate risks, recommended phase posture

investor_view
  cost distribution medians and strategic conflict index

policy_view
  water/wastewater/legitimacy indicators and range flags

research_view
  run counts, game profile count, ROM steps, and validation level
```

Boundary:

```text
A stakeholder decision surface is a screening artifact. It is not investment advice, official project validation, a permitting conclusion, or a final board decision.
```

---

## Validation lab

The validation lab provides validation-readiness tooling.

Primary package:

```text
validation_lab/
```

Documentation:

```text
docs/VALIDATION_LAB.md
```

Core files:

```text
validation_lab/validators.py
validation_lab/validation_report.py
validation_lab/reference_ranges.json
validation_lab/examples/public_reference_validation_case.json
```

Validation levels:

```text
Level 0 - Code and schema execution
  The model runs and produces finite outputs.

Level 1 - Structural validation
  Required result fields, matrices, gates, and output structures are present.

Level 2 - Public-reference screening
  Outputs are checked against declared public-reference or dimensional ranges.

Level 3 - Benchmark comparison
  Requires curated public benchmark cases.

Level 4 - Expert/calibrated validation
  Requires official project data, stakeholder data, expert review, or proprietary calibration evidence.
```

The included update supports Level 1 and Level 2 screening. It does not claim Level 4 validation.

Python example:

```python
import json
from pathlib import Path

from terafab_decision_twin.schema import load_scenario
from terafab_decision_twin.engine import run_scenario
from validation_lab import build_validation_report

scenario = load_scenario("scenarios/baseline_2026.json")
result = run_scenario(scenario)

ranges = json.loads(Path("validation_lab/reference_ranges.json").read_text())
report = build_validation_report(result, ranges)

print(report["validation_level"])
print(report["scorecard"])
print(report["calibration_gaps"])
```

Validation-lab outputs include:

```text
structure checks
range flags
scorecard
validation level
calibration gaps
screening interpretation
```

Boundary:

```text
Validation-lab checks are screening tools. They do not replace utility interconnection studies, water-authority records, permitting documents, official project data, expert engineering review, or investment diligence.
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

Advanced board workflow:

```python
import json
from pathlib import Path
from strategic_simulation import run_monte_carlo, simulate_reduced_order_model

mc_config = json.loads(Path("strategic_simulation/examples/uncertainty_baseline_2026.json").read_text())
mc = run_monte_carlo("scenarios/baseline_2026.json", mc_config)

rom_config = json.loads(Path("strategic_simulation/examples/rom_transition_2026_2030.json").read_text())
rom = simulate_reduced_order_model(rom_config)

print(mc["gate_failure_probability"])
print(rom["final_state"])
```

Use this workflow to inspect gate-failure probability and whether controls reduce stress trajectories.

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

Advanced investor workflow:

```python
import json
from pathlib import Path
from strategic_simulation import run_monte_carlo, analyze_normal_form_game

mc_config = json.loads(Path("strategic_simulation/examples/uncertainty_baseline_2026.json").read_text())
mc = run_monte_carlo("scenarios/baseline_2026.json", mc_config)

game_config = json.loads(Path("strategic_simulation/examples/strategic_game_2026.json").read_text())
game = analyze_normal_form_game(game_config)

print(mc["metric_quantiles"].get("total_cost_USD"))
print(mc["metric_quantiles"].get("cost_per_good_die_USD"))
print(game["conflict_index"])
```

Use this workflow to inspect cost quantiles and strategic coordination risk.

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

Advanced public-policy workflow:

```python
import json
from pathlib import Path

from terafab_decision_twin.schema import load_scenario
from terafab_decision_twin.engine import run_scenario
from validation_lab import build_validation_report

scenario = load_scenario("scenarios/multi_year_2026_2030.json")
result = run_scenario(scenario)
ranges = json.loads(Path("validation_lab/reference_ranges.json").read_text())

validation = build_validation_report(result, ranges)

print(validation["validation_level"])
print(validation["range_flags"])
print(validation["calibration_gaps"])
```

Use this workflow to inspect structural validity, range flags, and calibration gaps before public interpretation.

### Researcher and developer workflow

Use the repo as an auditable public model with schema, equations, tests, CLI, reports, notebooks, advanced simulation modules, and validation-readiness checks.

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
docs/ADVANCED_SIMULATION.md
docs/VALIDATION_LAB.md
docs/STAKEHOLDER_DECISION_SURFACES.md
```

Advanced researcher workflow:

```python
from strategic_simulation import sample_distribution

for i in range(5):
    print(sample_distribution({"distribution": "triangular", "low": 0.8, "mode": 1.0, "high": 1.4}, seed=i))
```

When adding advanced methods, add tests under:

```text
tests/test_strategic_simulation.py
tests/test_validation_lab.py
```

or add new focused test files under `tests/`.

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

Advanced simulation configuration files are intentionally separate from the core scenario schema. They live under:

```text
strategic_simulation/examples/
validation_lab/examples/
```

This keeps the deterministic scenario schema strict while allowing advanced workflows to perturb, interpret, and validate existing scenarios through external configuration.

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

Advanced-layer evidence rules:

```text
Uncertainty distributions are assumptions unless independently sourced.
Game-theory payoffs are assumptions unless independently sourced.
Reduced-order matrices are assumptions unless calibrated with admissible evidence.
Validation-lab reference ranges are screening references, not proof of real-world calibration.
Stakeholder decision surfaces are screening artifacts, not official decisions.
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
strategic_simulation/examples/
validation_lab/reference_ranges.json
validation_lab/examples/public_reference_validation_case.json
```

---

## Model architecture

The main deterministic execution path is coordinated by:

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

Advanced architecture:

```text
terafab_decision_twin/
  deterministic evidence-gated kernel

strategic_simulation/
  uncertainty propagation
  finite game analysis
  reduced-order trajectory simulation
  stakeholder decision-surface synthesis

validation_lab/
  structural checks
  public-reference range checks
  validation scorecards
  calibration-gap reporting
```

The advanced packages import the existing deterministic kernel. They should not duplicate or bypass the evidence-gated model.

---

## Methods and equations

Detailed equation coverage is documented in `docs/EQUATIONS.md`. The executable deterministic modules are under `terafab_decision_twin/models/`.

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

Representative deterministic equations:

```text
Q_reject â‰ˆ W_e * heat_rejection_fraction + Q_waste - E_stored_product

firm_capacity_margin = firm_capacity - site_load * (1 + reserve_margin)

water_withdrawal = energy_MWh * withdrawal_intensity + UPW_demand

S_gen = Q * (1/T_c - 1/T_h)

X_destroyed = T_0 * S_gen

legitimacy_margin = public_benefit_index - public_burden_index
```

Representative advanced methods:

```text
Monte Carlo:
  sampled scenario_i -> run_scenario(sampled scenario_i) -> ensemble statistics

Game theory:
  actors x strategies x declared payoffs -> best responses -> pure-strategy Nash candidates

Reduced-order model:
  x[t+1] = A x[t] + B u[t] + c + shock[t]

Validation lab:
  result structure + reference ranges + evidence status -> validation scorecard and calibration gaps
```

These equations and methods are scenario methods, not verified operating measurements.

---

## Outputs and gates

Every deterministic simulation returns scalar, vector, and matrix outputs.

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

Advanced outputs include:

```text
Monte Carlo:
  passed_probability
  failed_probability
  gate_failure_probability
  metric_quantiles
  sensitivity

Game theory:
  profiles
  best_responses
  pure_strategy_nash_equilibria
  conflict_index
  coordination_failures

Reduced-order model:
  trajectory
  final_state
  diagnostics

Stakeholder surface:
  board_view
  investor_view
  policy_view
  research_view

Validation lab:
  structure checks
  range flags
  validation scorecard
  validation level
  calibration gaps
```

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

Advanced reports are generated through Python objects rather than the `terafab` CLI. Relevant files:

```text
strategic_simulation/stakeholder_surface.py
validation_lab/validation_report.py
docs/ADVANCED_SIMULATION.md
docs/VALIDATION_LAB.md
docs/STAKEHOLDER_DECISION_SURFACES.md
```

Example:

```python
from strategic_simulation import build_stakeholder_decision_surface
from validation_lab import build_validation_report

validation = build_validation_report(result, ranges)
surface = build_stakeholder_decision_surface(
    monte_carlo=mc,
    game=game,
    rom=rom,
    validation=validation,
)
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
docs/ADVANCED_SIMULATION.md
docs/VALIDATION_LAB.md
docs/STAKEHOLDER_DECISION_SURFACES.md
```

Colab notebooks:

```text
notebooks/terafab_colab_dashboard.ipynb
notebooks/terafab_comparative_simulation_reporting_colab.ipynb
notebooks/terafab_advanced_simulation_lab.ipynb
```

The advanced simulation notebook is designed to demonstrate:

```text
deterministic baseline run
Monte Carlo uncertainty propagation
game-theory actor-strategy analysis
reduced-order trajectory simulation
validation-lab screening
stakeholder decision-surface synthesis
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

## Build advanced simulations and validation studies

Advanced studies should begin with a validated deterministic scenario and then add one or more external advanced configurations.

### 1. Select a deterministic kernel scenario

```text
scenarios/baseline_2026.json
scenarios/terawatt_stress_2026.json
scenarios/multi_year_2026_2030.json
scenarios/worst_case_2026_2030.json
scenarios/best_case_2026_2030.json
```

### 2. Choose an advanced study type

```text
Monte Carlo uncertainty study:
  strategic_simulation/examples/uncertainty_baseline_2026.json

Stakeholder strategy study:
  strategic_simulation/examples/strategic_game_2026.json

Reduced-order trajectory study:
  strategic_simulation/examples/rom_transition_2026_2030.json

Integrated advanced study:
  strategic_simulation/examples/integrated_advanced_2026_2030.json

Validation-readiness study:
  validation_lab/examples/public_reference_validation_case.json
```

### 3. Keep advanced assumptions explicit

For Monte Carlo, document:

```text
parameter path
distribution
low / mode / high or equivalent parameters
unit
status
source_ref
confidence
```

For game theory, document:

```text
actors
strategies
payoff assumptions
payoff evidence status
caution / boundary note
```

For reduced-order models, document:

```text
state variables
control variables
x0
A
B
c
shock
bounds
interpretation
```

For validation-lab studies, document:

```text
reference ranges
range status
range notes
validation level target
calibration gaps
```

### 4. Run the advanced study in Python

```python
import json
from pathlib import Path

from terafab_decision_twin.schema import load_scenario
from terafab_decision_twin.engine import run_scenario
from strategic_simulation import (
    run_monte_carlo,
    analyze_normal_form_game,
    simulate_reduced_order_model,
    build_stakeholder_decision_surface,
)
from validation_lab import build_validation_report

scenario = load_scenario("scenarios/baseline_2026.json")
base_result = run_scenario(scenario)

mc_config = json.loads(Path("strategic_simulation/examples/uncertainty_baseline_2026.json").read_text())
game_config = json.loads(Path("strategic_simulation/examples/strategic_game_2026.json").read_text())
rom_config = json.loads(Path("strategic_simulation/examples/rom_transition_2026_2030.json").read_text())
ranges = json.loads(Path("validation_lab/reference_ranges.json").read_text())

mc = run_monte_carlo("scenarios/baseline_2026.json", mc_config)
game = analyze_normal_form_game(game_config)
rom = simulate_reduced_order_model(rom_config)
validation = build_validation_report(base_result, ranges)

surface = build_stakeholder_decision_surface(
    monte_carlo=mc,
    game=game,
    rom=rom,
    validation=validation,
)

print(surface)
```

### 5. Interpret as screening, not certification

The advanced layer supports:

```text
public due diligence
stakeholder workshops
board-level scenario comparison
investor screening
policy stress testing
research extension
validation-readiness assessment
```

It does not support, by itself:

```text
official Terafab validation
bank-grade technical due diligence
permitting approval
utility interconnection approval
water-authority approval
investment recommendation
private fab process validation
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

strategic_simulation/
  Advanced simulation overlay: Monte Carlo uncertainty propagation, finite game analysis,
  reduced-order model simulation, and stakeholder decision surfaces.

strategic_simulation/examples/
  Advanced example configurations for uncertainty, game theory, reduced-order dynamics,
  and integrated advanced-study orchestration.

validation_lab/
  Validation-readiness overlay: structure checks, reference-range screening, scorecards,
  validation reports, and calibration-gap reporting.

validation_lab/examples/
  Example validation-lab configuration for public-reference screening.

schema/
  Public scenario schema.

scenarios/
  Included runnable deterministic scenarios.

notebooks/
  Colab dashboard, comparative scenario reporting notebook, and advanced simulation lab notebook.

docs/
  GitHub Pages-ready public site and technical documentation, including advanced simulation
  and validation-lab documentation.

sources/
  Public source-governance files: admitted facts, claim register, source manifest, unresolved variables,
  and restricted-source exclusion.

assets/
  One-page public infographic assets.

tests/
  Unit tests for schema, engine, equations, evidence, CLI behavior, release guards,
  strategic simulation, and validation lab.

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
strategic simulation
validation lab
```

Advanced-layer tests cover:

```text
Monte Carlo reproducibility with a fixed seed
Monte Carlo run-count behavior
distribution sampling
game-theory equilibrium detection
reduced-order trajectory behavior
stakeholder decision-surface construction
validation-lab structure checks
reference-range flags and validation reporting
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
official stakeholder preference model
official game-theory payoff model
official utility-capacity commitment
official water-authority conclusion
official public-policy legitimacy finding
Level 4 expert/calibrated validation without external data
```

The package is a public, executable, evidence-gated scenario simulator. Its conclusions are conditional on the scenario inputs, evidence labels, advanced assumptions, reference ranges, and validation limits supplied to it.

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
