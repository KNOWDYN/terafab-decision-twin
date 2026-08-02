# Step 3 Stress Test and Gate Decision

**Study ID:** `ecm_terafab_us_energy_security`
**Kernel:** `terafab_energy_security` 0.1.0
**Decision:** **MOVE TO STEP 4**

## Scope tested

The stress test evaluates the Step 3 deterministic calculation kernel, its
frozen-evidence interface, command-line parity, package inclusion, decision
logic, and forecast-notebook compatibility. It does not treat the synthetic
verification fixture as a scientific scenario or infer whether Terafab is
realistic.

## Results

| Test | Result | Finding |
|---|---|---|
| Five-stage execution | Pass | Target, manufacturing, facility, supply, and ERCOT/national stages execute through one typed API. |
| Target identity | Pass | Reconstructed rated output closes within `1e-8`; the 1 TW/year target is never assigned directly as facility MW. |
| Wafer geometry | Pass | The dies-per-wafer equation remains positive across the frozen die-area envelope and includes circular edge loss. |
| Electricity balance | Pass | Total-facility intensity is split into core and cooling components without double counting; residual is at or below `1e-8`. |
| First-law heat balance | Pass | Process and cooling contributions reconstruct coincident heat rejection within `1e-8`. |
| Water balance | Pass | Withdrawal equals consumption plus wastewater within `1e-8` when required inputs exist. External-withdrawal data do not receive a second recycling credit. |
| Impossible water combination | Pass | Cases with UPW intensity greater than total-water intensity fail the physical water gate. |
| Missing evidence behavior | Pass | Missing manufacturing capacity, heat-rejection capacity, water basis, interconnection, or PUCT metrics produces `indeterminate`, not zero or a favorable default. |
| Known capacity failure | Pass | A known wafer-capacity shortfall produces `not_demonstrated`. |
| Schedule precedence | Pass | A known interconnection date after facility operation fails both schedule and supply-deliverability gates. |
| PUCT boundary operators | Pass | LOLE equality passes; duration and magnitude equality fail because their operators are strict. |
| Reserve-margin misuse guard | Pass | Reserve margin is marked screening-only and cannot independently pass regional adequacy. |
| National context guard | Pass | National energy and peak shares are reported as context and never promoted to adequacy conclusions. |
| Determinism | Pass | Repeated API calls produce bitwise-identical canonical JSON and identical SHA-256 reproduction hashes. |
| CLI/API parity | Pass | The CLI and Python API return identical dictionaries for the frozen synthetic verification fixture. |
| Frozen evidence | Pass | The Step 2 validator passes 154 checks; the overlay independently verifies all five snapshot hashes. |
| Extreme-bound grid | Pass | All 512 combinations of frozen manufacturing/facility endpoints remained finite and conserved; 128 physically impossible UPW/total-water combinations were rejected. |
| Notebook repair | Pass | All five forecast-notebook requirements pass, all 17 code cells compile, and the forecast layer calls `run_scenario` rather than embedding governing equations. |
| Test discovery | Pass | The five function-style notebook checks are now included in the repository's `unittest` workflow. |
| Wheel build | Pass | The wheel contains all eight overlay modules, the `terafab-energy-security` entry point, and both Academic and Commercial licenses. |
| Repository regression | Pass | The full discovered suite passes 71 tests. |
| Repository hygiene | Pass | `git diff --check` and the restricted-source filename guard pass. |

## Defects found and corrected

1. A late but fully known interconnection initially returned `indeterminate`
   because the missing current-year margin was evaluated before the known
   schedule failure. Gate precedence now records a definite failure.
2. Total facility electricity could have been misread as non-cooling load and
   then had cooling added again. The kernel now uses the fixed-point component
   split while preserving total admitted electricity.
3. A water-recycling fraction could have been subtracted from a benchmark that
   already represented external withdrawal. Water-intensity basis is now
   mandatory, preventing a second reuse credit.
4. The three PUCT margins have different units and were initially candidates
   for an invalid scalar minimum. They are now stored separately in gate
   details; the gate is a conjunction, not a weighted or aggregated index.
5. Five forecast-notebook checks existed outside the repository's active
   `unittest` discovery path. They are now discovered and pass.

## Residual limits carried into Step 4

- The kernel is deterministic and milestone-year based; pathway generation,
  correlated sampling, Shapley effects, convergence, and annual 2026–2050
  orchestration belong to Step 4.
- No public Terafab wafer capacity, electrical load, water capacity, or final
  interconnection has appeared merely because the kernel can accept those
  fields.
- The current root ECM notebook is a compatibility artifact for the existing
  generic package. The paper-specific Step 4 notebook must call
  `terafab_energy_security` and must exclude economics, policy, governance, and
  investment analysis from the principal study.
- Probabilistic ERCOT adequacy remains indeterminate unless defensible
  frequency, duration, and magnitude values are supplied for the same case and
  year.

## Decision

**MOVE TO STEP 4.**

The Step 3 kernel is dimensionally closed, evidence-gated, installable,
deterministic, and resistant to the main favorable-default and double-counting
failure modes. Its remaining limitations are the intended subjects of Step 4,
not defects requiring Step 3 redesign.

No commit, push, or pull request was performed.
