# Step 1 Stress Test and Gate Decision

**Study ID:** `ecm_terafab_us_energy_security`
**Contract version tested:** `0.1.0`
**Decision:** **MOVE TO STEP 2**
**Decision type:** Proceed with mandatory evidence priorities; no further Step 1 revision is required before evidence acquisition.

## 1. Test purpose

This stress test evaluates whether the Step 1 scientific contract is sufficiently coherent, falsifiable, bounded, computable, evidence-aware, reproducible, and aligned with *Energy Conversion and Management* to justify beginning the evidence and parameter foundation in Step 2.

The test does not assess whether Terafab is feasible. It assesses whether the proposed study can produce a defensible answer without converting public claims or assumptions into facts.

## 2. Stress-test results

| Criterion | Result | Evidence from the contract | Residual risk |
|---|---|---|---|
| Dimensional validity | Pass | Product output `W_rated/year`, facility power MW, and electricity MWh/TWh are explicitly separated; assigning 1 TW/year as site load is prohibited | The public target remains semantically ambiguous and must be bounded in Step 2 |
| Scientific falsifiability | Pass after revision | Four hypotheses have null, support, falsification, and indeterminate rules | H3 depends on the availability of an authoritative hourly adequacy representation |
| Scope control | Pass with conditions | National analysis is contextual; ERCOT is the principal security system; hourly analysis is restricted to selected years | Attempting a full national dispatch or power-flow model would break the scope |
| Manufacturing identifiability | Conditional pass | The target-to-throughput equation exposes die power, die per wafer, yield, and throughput explicitly | Multiplicative parameter degeneracy requires evidence-supported ranges rather than a single inferred answer |
| Facility thermodynamics | Pass | Electricity, cooling, first-law heat, and water balances are coupled and auxiliaries feed back into total electricity | Public component-level fab data may be heterogeneous or dated |
| Supply-pathway realism | Pass after revision | The new `supply_deliverability` gate prohibits unlimited or instantaneous onsite supply | Construction-rate, fuel, accredited-capacity, interconnection, and water evidence must be obtained |
| ERCOT security relevance | Pass | Incremental coincident peak, reserve position, accredited capacity, LOLE, and EUE are specified | Probabilistic metrics may require a reduced-order adequacy representation if full official data are unavailable |
| National energy-security relevance | Pass | National annual electricity, peak, firm capacity, fuel, and emissions are contextualized without an arbitrary index | National annual-energy shares must not be interpreted as regional reliability |
| Validation feasibility | Conditional pass | Independent electricity, cooling, water, throughput, ERCOT, and EIA benchmarks are required | Water, yield, and advanced-node fab validation data are likely to be the weakest evidence classes |
| Uncertainty integrity | Pass | Correlated sampling, convergence, sensitivity intervals, and a predeclared 20/80 concentration test are required | Dependence structures may remain weakly identified |
| Computational feasibility | Pass | Annual 2026–2050 calculations and selected-year hourly cases are practical in Python and Colab; the scenario matrix is finite | Full chronological capacity-expansion optimization is intentionally excluded |
| ECM fit | Pass | The contribution centers on production-to-energy conversion, facility thermodynamics, resource requirements, and adequacy under uncertainty | Policy, game theory, and investment content must remain excluded from the principal paper |
| Evidence and legal boundary | Pass | Non-affiliation, source-available status, no-private-data, no-official-feasibility, and no-advice boundaries are explicit | Public claims must be preserved verbatim with status and date in Step 2 |
| Reproducibility | Pass | Frozen sources, hashes, machine-readable contracts, CLI-notebook parity, and prespecified outputs are required | Live web retrieval must not enter the final execution path |

## 3. Defects found and corrected during the stress test

### 3.1 Unconstrained supply escape route

Initial defect: a `firm_onsite` or hybrid portfolio could have been assigned enough capacity to make any pathway appear feasible.

Correction:

- Added the required `supply_deliverability` gate.
- Required construction lead time, commissioned capacity, accredited availability, outage behavior, interconnection timing, fuel or energy availability, and material water constraints.
- Prohibited unlimited or instantaneous supply.

### 3.2 Weak regional-versus-national hypothesis

Initial defect: the statement that ERCOT would be “more restrictive” than a national annual-energy balance lacked a clean falsification condition.

Correction:

- Replaced it with a test of whether a pathway can remain inside the admitted national annual-electricity projection spread while violating an official ERCOT adequacy gate in the same year.

### 3.3 Post hoc sensitivity threshold

Initial defect: H4 deferred its definition of “dominant subset” to Step 2, leaving room for result-dependent threshold selection.

Correction:

- Locked a 20/80 concentration rule before model results: the leading 20% of admitted uncertain inputs must account for at least 80% of normalized total-order sensitivity mass, subject to a pre-results bootstrap stability rule established in Step 2.

## 4. Critical evidence risks for Step 2

The following are not Step 1 design failures. They are empirical kill tests that Step 2 must resolve before code architecture is finalized:

1. **Target semantics:** Determine whether the 1 TW/year claim can be bounded as rated device/package power manufactured annually or whether multiple interpretations must remain co-primary.
2. **Throughput translation:** Obtain defensible ranges for device or package power, gross die per wafer, yield, wafer starts, and packaging throughput without using proprietary data.
3. **Facility intensities:** Establish admissible electricity, cooling, cleanroom, ultrapure-water, and wastewater intensities with applicability and uncertainty notes.
4. **Geographic attribution:** Verify which publicly described facility phases are reasonably modeled inside ERCOT and keep non-ERCOT cases separate.
5. **Adequacy standard:** Identify the official ERCOT/PUCT/NERC reliability definitions, accredited-capacity treatment, and available hourly inputs.
6. **Supply deliverability:** Bound generation, storage, fuel, interconnection, and construction schedules so onsite supply cannot be used as an unconstrained assumption.

If target semantics or indispensable facility-intensity evidence cannot be bounded, Step 2 must return `revise scope` or `indeterminate study`, not proceed to numerical model construction.

## 5. Verification performed

- Both JSON contracts parse successfully with Python’s standard JSON parser.
- Study ID and contract version agree across files.
- All four hypothesis identifiers appear in the narrative specification.
- The temporal boundary is consistently 2026–2050.
- All ten feasibility gates are present, including `supply_deliverability`.
- Classification rules distinguish `conditionally_feasible`, `not_demonstrated`, and `indeterminate`.
- The 20/80 sensitivity rule is machine-readable.
- `git diff --check` reports no whitespace errors.
- The existing 47-test `unittest` suite passes without regression.
- No named restricted-source file is referenced in the Step 1 artifacts.

## 6. Decision rationale

**Decision: MOVE TO STEP 2.**

The remaining uncertainties concern evidence availability, parameter admissibility, and target interpretation—the exact subjects of Step 2. The scientific contract now prevents those uncertainties from being hidden, silently defaulted, or converted into official claims. Revising Step 1 again before testing the evidence would add speculative detail without improving validity.

Progression is conditional on Step 2 treating the six critical evidence risks above as explicit pass/fail gates. No scientific kernel upgrade should begin until those evidence gates are reported to the owner.
