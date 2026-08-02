# Step 2 Stress Test and Gate Decision

**Study ID:** `ecm_terafab_us_energy_security`
**Evidence contract version:** `0.2.0`
**Evidence freeze:** 2026-08-01
**Decision:** **MOVE TO STEP 3**
**Permitted claim:** Prospective, conditional constraint analysis

## 1. Test purpose

This stress test asks whether Step 2 provides a traceable and sufficiently
bounded evidence foundation for model implementation. It does not determine
whether Terafab is feasible, and it does not validate a digital twin of the
project.

## 2. Evidence stress-test results

| Test | Result | Finding |
|---|---|---|
| Public-claim isolation | Pass | The 1 TW/year target remains `W_rated/year`; an explicit guard prohibits treating it as facility load. Project facility load remains `null`. |
| Project-fact discipline | Pass | Wafer capacity, electrical load, water withdrawal, final interconnection, product mix, yield, and process recipe remain unknown rather than inferred facts. |
| Target semantics | Conditional pass | The primary interpretation is computable, but the public phrase remains ambiguous. Alternative interpretations and `indeterminate` behavior are mandatory. |
| Throughput boundedness | Pass for scenario analysis | Pre-results power, geometry, yield, and packaging ranges produce a positive, finite, ordered extreme envelope of approximately 1.49 million to 925 million 300 mm wafers/year. This is a numerical guard, not a result or forecast. |
| Facility evidence sufficiency | Conditional pass | The registry contains multiple electricity, facility-component, cleanroom, and water comparators, with incompatible boundaries documented and broad uncertainty retained. |
| Schedule precedence | Pass | Every provisional phase schedule places construction completion before the first operations/incentive year. The Phase 4 source conflict is preserved. |
| Geographic attribution | Conditional pass | Grimes County is supported by public filings, but the ERCOT point and deliverability are not. The ERCOT branch is conditional and may fail or become indeterminate. |
| Adequacy threshold completeness | Pass | Frequency, duration, and magnitude components are retained; the magnitude is annual; both protocol-prescribed and SB6 CDR cases are mandatory. |
| Supply realism | Pass with required gates | Generic lead times cannot bypass site, permitting, interconnection, transmission, fuel, water, commissioning, ELCC, or outage constraints. |
| Calibration/validation leakage | Pass | The component calibration source is disjoint from listed external validation sources. The holdout-count rule blocks a validated-twin claim. |
| Uncertainty pre-registration | Pass | Distributions, seed, sample counts, convergence, rank correlations, independence sensitivity, and H4's bootstrap thresholds are frozen before model results. |
| Dependence validity | Pass | Both the target Spearman matrix and its transformed Gaussian-copula latent matrix pass positive-semidefinite guards; a deliberately invalid 1.10-correlation matrix is rejected. |
| Snapshot reproducibility | Pass | Five frozen snapshots match their SHA-256 manifest. |
| Machine-readable integrity | Pass | The offline validator completed 154 checks across 26 sources, 22 parameters, and five snapshots. All 13 study JSON files parse. |
| Repository regression | Pass | The existing `unittest` suite completed 47 tests with no failure. |
| Whitespace/restricted-source guard | Pass | `git diff --check` is clean and no restricted-source filename is present. |

## 3. Adversarial questions

### Can a favorable interpretation silently turn 1 TW into free evidence?

No. It is admitted only as an ambiguous manufacturing-output target. The model
must show the full target-to-module-to-die-to-wafer chain and may return
`indeterminate`.

### Can onsite generation make every pathway feasible?

No. Commissioning must precede load, accredited capacity is portfolio- and
season-dependent, and site/interconnection/fuel/water adders are required.
Absent evidence fails the relevant gate; it does not receive a favorable
default.

### Can a national annual-energy share prove ERCOT security?

No. The national EIA case envelope is context only. ERCOT is evaluated with
regional coincident demand, accredited supply, and the PUCT reliability rule.

### Can comparator agreement be called project validation?

No. The frozen contract requires at least five independent numerical holdouts
and specified error/coverage thresholds. Current evidence is insufficient, so
only diagnostic benchmarking and prospective constraint language are allowed.

## 4. Defect found and corrected

The first validator execution exposed a field-name mismatch between the
validation contract (`external_validation_sources`) and validator
(`validation_sources`). The validator was corrected and re-run from a clean
process.

An adversarial methods review also found that ordinary parameter-attributed
Sobol indices would be invalid under the declared correlated input model. The
contract now applies H4's predeclared total-order test to an explicitly
independent-marginal Sobol design and requires dependence-aware Shapley effects
for the correlated joint distribution. It also specifies the Spearman-to-
Gaussian latent-correlation transform and validates both matrices. No evidence
value or acceptance threshold was changed in response to model results.

## 5. Existing engineering gap assigned to Step 3

The repository's official `unittest` command does not discover five
function-style tests in `tests/test_ecm_colab_notebook.py`. Direct execution
showed two pass and three fail: the current root notebook lacks the expected
forecast-first sections, kernel-use markers, and forecast-grade
figures/exports. This predates Step 2 and does not invalidate its evidence
foundation. It is a mandatory Step 3 implementation and test-discovery item;
it must be resolved before the upgraded study can pass a later release gate.

## 6. Residual scientific risks

- The project itself has not publicly resolved the target's dimension.
- Filed schedules are conditional and Phase 4 contains an internal conflict.
- No verified project operating, capacity, utility, water, or interconnection
  data were identified.
- Advanced-node comparator data remain heterogeneous and partly historical.
- Reserve-margin screening cannot substitute for probabilistic reliability.
- Site-specific supply, transmission, fuel, and water deliverability may remain
  binding unknowns even after model implementation.

These risks are not hidden. They are encoded as uncertainty, required gates,
or an `indeterminate` classification.

## 7. Decision rationale

**Decision: MOVE TO STEP 3.**

All Step 2 kill tests either pass or have a defensible conditional model
boundary with explicit failure/indeterminate behavior. Revising Step 2 would
not create the missing project data. The scientifically appropriate next move
is to implement the calculation kernel against the frozen evidence contracts,
while preserving the prospective-constraint claim and treating the three
notebook test failures as mandatory Step 3 work.

No commit, push, branch publication, or pull request was performed.
