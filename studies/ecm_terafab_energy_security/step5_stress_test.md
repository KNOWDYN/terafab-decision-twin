# Step 5 stress-test report

Date: 2026-08-01
Scope: prespecified figures and tables, result integrity, visual QA, validation boundaries, reproducibility, and readiness for manuscript construction.

## Stress-test results

| Test | Result | Evidence |
|---|---:|---|
| Prespecified output coverage | Pass | All 10 figures and 6 tables are generated. |
| Plot-data traceability | Pass | Every figure has a dedicated machine-readable CSV; artifact hashes are recorded in `publication_manifest.json`. |
| Figure rendering | Pass after revision | PNG and PDF versions render successfully. Visual QA corrected crowded gate and sensitivity labels. |
| Figure 2 feasibility guard | Pass | The output is labelled a requirement surface because no public project wafer capacity exists for a pass/fail boundary. |
| Independent-validation guard | Pass | Figure 3 is explicitly a limited benchmark diagnostic; bias, NRMSE, MAPE, and coverage are not fabricated. |
| ERCOT horizon guard | Pass | Figure 6 stops at 2030, the last frozen official counterfactual year. |
| Probabilistic-adequacy guard | Pass | Figure 7 stores LOLE and expected unserved energy as null and labels its replacement as screening-only. |
| National-scope guard | Pass | Figure 8 stores peak share, fuel, and emissions as null and reports annual EIA electricity context only. |
| Classification integrity | Pass | 1 counterfactual and 336 indeterminate trajectories; no failed case is relabelled as indeterminate or vice versa at gate level. |
| Hypothesis integrity | Pass | H1–H4 remain indeterminate in the final manifest. |
| Full uncertainty convergence | Pass | Worst 16,384→32,768 relative change is 0.2900%, below 1%, across all dependence stresses. |
| Sensitivity uncertainty | Pass | 1,000 bootstrap replicates; Sobol and Shapley intervals and rankings are exported. |
| 20/80 diagnostic | Below threshold | Top two independent total-order inputs account for 78.0212%, below 80%; no favorable rounding is applied. |
| Notebook execution | Pass | Six code cells execute end-to-end and call the same publication-bundle API as the CLI. |
| CLI final-mode execution | Pass | The final bundle contains 44 artifacts and a complete checksum manifest. |
| Repository regression suite | Pass | 107 tests pass, including restricted-source, licensing, release-metadata, scientific-boundary, and publication-artifact guards. |
| Git publication boundary | Pass | No commit, push, branch publication, or pull request was created; those remain Step 7 actions. |

## Adversarial interpretation tests

### Can the results be presented as proof that Terafab is impossible?

No. The classification is indeterminate because indispensable public evidence is missing. Explicit stress failures show where declared cases break, but unknown ordinary-case capacities prevent an impossibility proof.

### Can a positive reserve-margin change be presented as an ERCOT benefit?

No. The sign changes with the official counterfactual and the assumed accredited grid addition. No probabilistic reliability metric is available, and the reserve-margin calculation is labelled screening-only.

### Can the model be called validated because public comparators are shown?

No. The central electricity and water values are informed by the same comparators displayed in Figure 3, and the frozen minimum of five independent numeric holdouts is not met. The model is verified algebraically and compared diagnostically, not empirically validated for Terafab.

### Can the 91.54 GW p95 be stated as the expected Terafab load?

No. It is a marginal tail quantile under broad epistemic scenario distributions. The central conditional estimate is 16.58 GW at full realization, while no verified project load exists.

## Decision

**MOVE TO STEP 6.**

The Step 5 results layer is complete, traceable, visually reviewed, and resistant to the principal overclaiming failure modes. Revising Step 5 cannot supply the missing project measurements or probabilistic ERCOT data. Step 6 should draft the paper around the defensible result: the announcement is not presently demonstrable as realistic from public evidence, while its primary admitted interpretation implies resource requirements material to US and ERCOT energy-security planning.

Step 6 must retain the prospective-constraint framing, the indeterminate hypothesis outcomes, the three limited figure replacements, and the distinction between resource requirement, accredited-capacity screening, and probabilistic adequacy.
