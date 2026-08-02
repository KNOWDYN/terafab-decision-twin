# Step 4 stress-test report

Date: 2026-08-01
Scope: annual pathway orchestration, uncertainty/convergence, sensitivity diagnostics, shared CLI/notebook workflow, and scientific claim guards.

## Results

| Test | Result | Evidence |
|---|---:|---|
| Locked matrix completeness | Pass | 337 trajectories generated: 1 no-build, 224 unknown target-scale branches, and 112 computable conditional full-target branches. |
| Annual and gate coverage | Pass | Full run exported 2,825 annual rows and 20,720 required/optional gate rows. |
| Unknown-scale discipline | Pass | Research-fab and initial-large-scale branches produce no invented numerical resource results and classify as indeterminate. |
| Target-semantic guard | Pass | The primary `W_rated/year` branch and unresolved alternative branch are explicit; no path assigns 1 TW as facility load. |
| Post-2030 ERCOT boundary | Pass | Protocol/SB6 values are used only where the frozen 2026–2030 series exists; later baselines remain `null`. |
| Yield failure injection | Pass | A 0.75 yield multiplier increases wafer starts by exactly `1 / 0.75` at unchanged target. |
| Cooling/water failure injection | Pass | The 80%-capacity stress fails both thermal-capacity and water-capacity gates. |
| Schedule failure injection | Pass | The three-year infrastructure delay fails schedule precedence for the accelerated 2029 start. |
| Firm-outage injection | Pass | The outage case reduces firm accredited capacity to zero and increases net grid peak relative to the matched normal case. |
| Vectorized/kernel parity | Pass | Sampled wafer, electricity, peak, and water equations match the deterministic Step 3 kernel. |
| Full Sobol convergence | Pass | Every estimable output changed by less than 1% from 16,384 to 32,768 samples in all four dependence cases. Worst change: 0.2900%. |
| Correlation stress distinction | Pass after repair | A test exposed an incorrect sign application that made ±0.20 identical. The shift rule was corrected and a regression test now requires distinct designs. |
| Independent sensitivity stability | Pass as a diagnostic | Top-set inclusion minimum 1.00; median and fifth-percentile Spearman rank correlation are effectively 1.00 with 1,000 bootstraps. |
| Predeclared 20/80 diagnostic | Below threshold | The top two inputs carry 78.0212% of normalized total-order mass, below 80%. This is not an H4 result because facility peak is not H4's locked outcome. |
| Dependence-aware diagnostic | Pass | Shapley effects sum to 1.0; linear-surrogate `R² = 0.9405`. Top inputs are dies per module, fab electricity intensity, and die area. |
| Feasibility-probability guard | Pass | The result is `null`/indeterminate, not a fabricated zero or probability, whenever required evidence is absent. |
| Notebook execution | Pass | All six code cells execute in quick mode and export the same matrix/report structures used by the CLI. |
| Repository regression suite | Pass | 98 tests pass, including direct CLI/API trajectory parity. |

## Full-run observations

- Every one of the 336 nonzero trajectories remains `indeterminate`; this is caused by the known evidence boundaries, not numerical instability.
- The full-target central conditional case reaches approximately 68.29 million 300-mm wafer starts/year, 135.17 TWh/year facility electricity, 16.58 GW coincident load, and 568.72 million m³/year external water withdrawal at full realization. These are model outputs under the admitted interpretation and assumptions, not reported Terafab design values.
- The official probabilistic ERCOT metrics required for H2/H3 were not admitted in Step 2. Reserve-margin calculations remain screening quantities and cannot establish regulatory adequacy.
- The strongest independent resource-peak sensitivity contributors are logic dies per module, fab electricity intensity, and die area. The correlated Shapley ranking has the same top three, but agreement is not used as post-hoc support for H4.

## Hypothesis disposition after Step 4

| Hypothesis | Disposition | Reason |
|---|---|---|
| H1 | Indeterminate | No numerical branch can pass all required gates because public manufacturing, thermal, water, and evidence-sufficiency capacities are unresolved. |
| H2 | Indeterminate | Comparable official probabilistic regional margins are unavailable; a screening reserve margin cannot substitute. |
| H3 | Indeterminate | Hourly adequacy/accredited-capacity evidence is unavailable. |
| H4 | Indeterminate | Its locked joint-feasibility/realization outcome is unidentifiable; resource-peak sensitivity is diagnostic only. |

## Decision

**MOVE TO STEP 5.**

Step 4 is internally complete and stress-resistant within the frozen public evidence. Repeating or broadening simulations cannot resolve the missing project capacities or official adequacy series. Step 5 should therefore analyze conditional resource envelopes, scenario contrasts, and binding evidence gaps; it must not recast the all-indeterminate feasibility classification as a yes/no realism verdict.
