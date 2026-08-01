# Step 3 Computational Kernel

**Study ID:** `ecm_terafab_us_energy_security`
**Overlay package:** `terafab_energy_security`
**Kernel version:** `0.1.0`
**Claim level:** Prospective conditional constraint analysis

## Purpose

The Step 3 overlay converts an admitted annual rated-device output target into
semiconductor throughput, facility electricity, heat rejection, water demand,
supply requirements, ERCOT screening metrics, national scale, and tri-state
decision gates. It does not introduce project specifications where Step 2
found none.

The existing `terafab_decision_twin` package remains unchanged as the generic
evidence-gated model. The new top-level `terafab_energy_security` package is a
paper-specific overlay with no third-party runtime dependency.

## Five calculation stages

| Stage | Implementation | Principal outputs |
|---|---|---|
| Target interpreter | `engine.run_case` and `equations.translate_target` | Admitted `W_rated/year`, modules/year, explicit prohibition on target-to-facility-load equivalence |
| Manufacturing translator | `equations.gross_dies_per_wafer` and `translate_target` | Gross dies/wafer, good dies/year, wafer starts/month and year, packaging throughput, identity residual |
| Facility resource model | `equations.facility_resources` | Total/component electricity, average and coincident peak load, cooling power, first-law heat rejection, UPW, gross water, withdrawal, reuse, consumption, wastewater, balance residuals |
| Deployment and supply model | `engine._supply_stage` | Commissioned and accredited onsite capacity, grid peak and energy, interconnection margin, missing and late infrastructure |
| Electricity-security assessment | `engine._ercot_stage` and tri-state gates | Counterfactual/accredited capacity, incremental peak, reserve-margin change, PUCT frequency-duration-magnitude gate, national energy and peak shares |

## Locked governing details

### Wafer geometry

The continuous dies-per-wafer approximation includes circular edge loss:

\[
D=\frac{\pi d^2}{4A}-\frac{\pi d}{\sqrt{2A}}.
\]

Scribe-lane and defect effects are not hidden in this equation. They remain in
die-area and effective-yield scenarios.

### Target identity

\[
C_{\mathrm{rated}}
=W_{\mathrm{year}}DYP_{\mathrm{module}}/N_{\mathrm{die/module}}.
\]

The inverse is used to calculate required wafer starts. The reconstructed
target must have a relative residual no greater than `1e-8`.

### Cooling and total electricity

Step 2 admits a total-facility electricity intensity. Cooling therefore cannot
be added again. For total electricity `E`, non-cooling facility electricity
`B`, and cooling COP:

\[
E=B+\frac{B}{COP},\qquad
B=E\frac{COP}{COP+1}.
\]

This produces an internally consistent component split while preserving the
admitted total. The full coincident electrical load is treated as heat rejected
under the annual steady, negligible-product-energy assumption.

### Water accounting

Every case must declare whether its water intensity is:

- `gross_process_demand_before_reuse`; or
- `external_withdrawal_after_reuse`.

Recycling displacement is subtracted only in the first case. This prevents an
external-withdrawal benchmark from receiving a second recycling credit.
Consumption and wastewater remain unknown unless a consumptive fraction is
provided. The steady water balance must close within `1e-8`.

### ERCOT adequacy

Reserve margin is calculated and reported only as a screen. It cannot pass the
regional adequacy gate. A determinate gate requires all three PUCT quantities:

- LOLE no greater than the applicable limit;
- maximum expected event duration strictly below its limit; and
- expected highest hourly average load shed strictly below the annual
  magnitude limit.

Missing probabilistic values produce `indeterminate`, never an inferred pass.

## Gate and classification logic

Every required gate has one of three states: `pass`, `fail`, or
`indeterminate`.

- `conditionally_feasible`: every required gate passes for the modeled case.
- `not_demonstrated`: at least one required gate fails and no indispensable
  gate is indeterminate.
- `indeterminate`: at least one indispensable gate lacks bounded evidence.

This precedence prevents a favorable known margin from concealing absent
project capacity, interconnection, water, or probabilistic adequacy evidence.

## Interfaces

Python:

```python
from terafab_energy_security import EnergySecurityCase, run_case

result = run_case(EnergySecurityCase.from_dict(case_payload))
```

Command line:

```bash
terafab-energy-security validate-evidence studies/ecm_terafab_energy_security
terafab-energy-security run case.json --output result.json
```

`python -m terafab_energy_security` provides the same interface. The CLI and
Python API return identical machine-readable results.

## Step boundary

Step 3 supplies a deterministic milestone-year kernel. Step 4 may now build the
predeclared 2026–2050 realization pathways, supply portfolios, annual tables,
and correlated uncertainty workflow by calling this package. Governing
equations must not be duplicated in the Step 4 notebook.

The included `synthetic_complete_case.json` is solely a software-verification
fixture. It is not an admitted Terafab scenario, forecast, project
specification, validation observation, or paper result.
