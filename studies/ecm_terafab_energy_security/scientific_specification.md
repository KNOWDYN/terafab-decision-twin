# Scientific Specification: Terafab and United States Energy Security

**Study ID:** `ecm_terafab_us_energy_security`
**Contract version:** `0.1.0`
**Step:** 1 of 7 — scientific contract
**Status:** Complete for owner review; no empirical parameter values are locked in Step 1
**Intended journal:** *Energy Conversion and Management*
**Software status:** Independent, source-available KNOWDYN research package

## 1. Working title

**Can Terafab be powered? A prospective assessment of terawatt-scale semiconductor manufacturing and United States electricity security**

The title may be refined after the scientific results are known. The manuscript must not imply access to private Terafab data, official participation, endorsement, certification, or validation.

## 2. Primary scientific question

> Under transparent interpretations of the publicly announced Terafab production target, what semiconductor throughput and facility electricity, heat-rejection, water, and firm-supply requirements are implied, and under which 2026–2050 deployment and energy-supply pathways can those requirements be accommodated without violating defined ERCOT and United States electricity-security constraints?

This question replaces an unqualified yes/no question about whether Terafab is “realistic.” Realism is decomposed into interpretable and falsifiable conditions: target semantics, manufacturing feasibility, facility-resource feasibility, temporal deliverability, and electricity-security consequences.

## 3. Public-claim boundary and semantic discipline

The official public website states “Terafab output 1 TW/Year,” describes production at terawatt scale, and separately refers to “1 TW+” of solar power needed. Those statements do not define whether the output quantity is chip rated electrical power, deployed computing-system demand, computing performance converted to a power equivalent, or another measure. The public page also compares the target with “Current annual U.S. consumption .5 TW,” which mixes annual language with the dimension of power. These statements establish a public research question but do not provide a complete engineering specification.

The study therefore enforces the following rules:

1. `1 TW/year` is never assigned as the fab site electrical load.
2. The primary interpretation is **one terawatt of aggregate rated electrical power embodied in good compute devices manufactured per calendar year**.
3. At least one alternative defensible interpretation must be evaluated if Step 2 finds sufficient evidence to define it without inventing private specifications.
4. The facility load is derived from wafer throughput, process and facility energy intensities, utilization, yield, packaging, cooling, and water-treatment requirements.
5. Public claims are model inputs or scenario boundaries, not verified operating facts.
6. If Step 2 cannot establish a defensible target interpretation, the target-semantic gate fails and the scientific conclusion becomes `indeterminate`, not `infeasible`.

Primary public context:

- Terafab public site: <https://terafab.ai/>
- Reuters public project summary, updated 6 May 2026: <https://www.reuters.com/business/autos-transportation/elon-musk-lays-out-terafab-ai-chip-project-plan-2026-05-06/>

## 4. Research questions

### RQ1 — Target translation

What good-die output, wafer starts, packaging throughput, and yield trajectory are required to meet each defensible interpretation of the announced target?

### RQ2 — Facility-resource requirements

What annual electricity, coincident peak power, cooling power, heat rejection, ultrapure-water demand, total withdrawal, consumptive use, and wastewater discharge follow from the required throughput?

### RQ3 — Temporal realization

What is the earliest feasible realization year under accelerated, reference, delayed, and non-realization pathways when manufacturing capacity and supporting infrastructure must be commissioned before the corresponding production load?

### RQ4 — ERCOT electricity security

How does each pathway alter ERCOT annual consumption, coincident peak demand, accredited capacity requirement, reserve position, loss-of-load expectation, expected unserved energy, and dependence on grid or onsite firm supply?

### RQ5 — United States electricity security

What share of projected US electricity generation, peak capacity additions, firm generation, storage, natural-gas demand, and emissions would be attributable to each pathway relative to an official no-Terafab counterfactual?

### RQ6 — Dominant constraints and uncertainty

Which uncertain parameters and interactions most strongly control target realization year, facility load, security margins, and the probability of satisfying all feasibility gates?

## 5. Hypotheses and falsification logic

The machine-readable hypotheses are defined in `hypotheses.json`. The study tests four propositions:

- **H1 — Conditional physical realization:** At least one evidence-supported pathway can satisfy the announced target interpretation and all manufacturing, facility, temporal, and electricity-security gates by 2050.
- **H2 — Regional constraint visibility:** At least one pathway that remains inside the spread of admitted national annual-electricity projections nevertheless violates an ERCOT adequacy constraint.
- **H3 — Supply-portfolio effect:** A pre-committed firm or hybrid supply portfolio reduces incremental ERCOT adequacy risk relative to a grid-dominant connection at the same manufacturing trajectory.
- **H4 — Scale uncertainty concentration:** The leading 20% of admitted uncertain inputs account for at least 80% of normalized total-order sensitivity mass for feasibility outcome or realization year, with stable bootstrap ranks.

No hypothesis may be rewritten after results are inspected. A hypothesis may be retired only if Step 2 demonstrates that the required public evidence does not exist; the retirement and reason must remain in the repository.

## 6. Definitions

| Term | Definition in this study |
|---|---|
| Announced target | A public target or claim, preserved with its original wording and evidence status |
| Rated compute power produced | Sum of rated electrical power of good compute devices manufactured during one calendar year, reported as `W_rated/year` |
| Facility electrical load | Electrical power drawn by process tools, facility systems, cooling, water treatment, packaging, and auxiliaries, reported in MW |
| Facility electricity | Time-integrated facility load, reported in MWh or TWh |
| Realization year | First calendar year in which the target and every applicable gate are simultaneously satisfied |
| Manufacturing feasibility | Required throughput, yield, equipment, and packaging remain inside evidence-supported ranges |
| Infrastructure feasibility | Required power, cooling, water, wastewater, and supply capacity are available before load is commissioned |
| Electricity security | A vector of adequacy, reliability, firm-supply, fuel-exposure, and incremental-system-burden metrics; not an arbitrary composite index |
| Counterfactual | Official ERCOT or EIA baseline without the incremental Terafab pathway |
| Conditional feasibility | Feasibility under explicitly stated assumptions; not a prediction or official project assessment |

## 7. System boundaries

### 7.1 Temporal boundary

- Baseline year: 2026.
- End year: 2050, aligned with the EIA Annual Energy Outlook horizon.
- Primary resolution: annual for all pathways.
- Secondary resolution: hourly for selected milestone and stress years, contingent on authoritative hourly data.
- The model may use monthly or quarterly construction milestones, but manuscript conclusions are reported by year unless a shorter interval is scientifically necessary.

### 7.2 Geographic boundary

- Facility boundary: publicly reported Texas research and large-scale facilities, without assuming a private site layout.
- Regional boundary: ERCOT, conditional on an ERCOT-connected facility.
- National boundary: United States electricity system as represented by EIA and NERC public projections.
- If a material facility is found to be outside ERCOT, Step 2 must introduce a separate interconnection-region case rather than misattribute its load to ERCOT.

### 7.3 Physical and industrial boundary

Included:

- Logic, memory, advanced-packaging, testing, and facility services when supported by the target interpretation.
- Process-tool electricity.
- Cleanroom circulation and make-up air.
- Chilled water, process cooling water, heat rejection, and cooling auxiliaries.
- Ultrapure-water production, withdrawal, consumption, and wastewater.
- Onsite electricity generation and storage when defined by a supply portfolio.
- Operational fuel use and direct/indirect operational emissions.

Excluded from the principal model:

- Electricity consumed by the manufactured chips after sale or deployment.
- Orbital data-center operation and launch-energy requirements.
- Embodied energy of construction materials and equipment unless a separate sensitivity case is justified.
- Proprietary process recipes, equipment specifications, yields, schedules, or contracts.
- Full macroeconomic equilibrium, wholesale-price forecasting, investment valuation, and project-finance conclusions.
- Semiconductor supply-chain security benefits; these may be discussed qualitatively but are not used to offset electricity-security impacts.

### 7.4 Functional units

Primary functional unit:

\[
1\ \mathrm{W_{rated}}\ \text{of good compute-device capacity manufactured per calendar year}.
\]

Required normalized outputs include:

- kWh per wafer start.
- kWh per good die.
- kWh per `W_rated/year` manufactured.
- m³ water per wafer start and per good die.
- MW facility load per 100,000 monthly wafer starts.
- MW and TWh of incremental system burden per target fraction.

## 8. Model architecture required by the contract

The scientific calculation must be implemented in five coupled stages:

1. **Target interpreter:** converts each admitted public target meaning into a numerical production requirement.
2. **Manufacturing translator:** converts target output into good die, gross die, wafer starts, packaging throughput, and capacity ramp.
3. **Facility-resource model:** derives electricity, peak load, heat rejection, cooling, water, wastewater, fuel, and emissions.
4. **Deployment and supply model:** schedules manufacturing and supporting infrastructure under each pathway and supply portfolio.
5. **Electricity-security assessment:** compares the incremental load with ERCOT and US counterfactuals and calculates security metrics and gates.

The existing `terafab_decision_twin` remains the generic evidence-gated physical kernel. A new `terafab_energy_security` overlay will implement target translation, deployment, supply, grid, and paper-specific analysis. The notebook may call these APIs but may not contain unique governing calculations.

## 9. Governing calculation contract

### 9.1 Rated output and throughput

For calendar year \(t\):

\[
C_{\mathrm{rated},t}
=12\,W_t\,D_t\,Y_t\,P_{\mathrm{die},t},
\]

where:

- \(C_{\mathrm{rated},t}\): rated compute-device power manufactured in year \(t\), `W_rated/year`.
- \(W_t\): wafer starts per month.
- \(D_t\): gross die per wafer.
- \(Y_t\): effective good-die yield, including qualification, contamination, and packaging effects.
- \(P_{\mathrm{die},t}\): rated electrical power per good compute device.

The inverse requirement is:

\[
W_t=\frac{C_{\mathrm{rated},t}}
{12D_tY_tP_{\mathrm{die},t}}.
\]

The exact accounting unit may be device, die, module, or packaged compute assembly. Step 2 must select the primary unit from public evidence and preserve conversion factors.

### 9.2 Operational electricity

\[
E_{\mathrm{fab},t}=E_{\mathrm{tools},t}+E_{\mathrm{cleanroom},t}
+E_{\mathrm{cooling},t}+E_{\mathrm{UPW},t}+E_{\mathrm{pack},t}
+E_{\mathrm{other},t}.
\]

Each term must be either throughput-derived, load-derived, or explicitly evidence-coded. Cooling and water-treatment auxiliaries must feed back into total facility electricity; they cannot be reported outside the electricity balance.

### 9.3 Peak facility load

\[
P_{\mathrm{fab,peak},t}=\max_h
\left(P_{\mathrm{tools},t,h}+P_{\mathrm{facility},t,h}
+P_{\mathrm{cooling},t,h}+P_{\mathrm{water},t,h}
+P_{\mathrm{pack},t,h}\right).
\]

When hourly profiles are unavailable, annual peak load must be represented by an evidence-supported load factor or coincidence model with uncertainty.

### 9.4 First-law heat balance

\[
Q_{\mathrm{reject},t,h}=
P_{\mathrm{electric},t,h}+Q_{\mathrm{process},t,h}
-W_{\mathrm{useful},t,h}-\frac{dU}{dt}.
\]

At annual steady operation, stored energy is not assumed significant without evidence. Recovered heat must be tracked separately and must not be counted simultaneously as rejected and useful heat.

### 9.5 Water balance

\[
V_{\mathrm{withdraw},t}=
V_{\mathrm{UPW},t}+V_{\mathrm{cooling},t}+V_{\mathrm{process},t}
+V_{\mathrm{domestic},t}-V_{\mathrm{reuse},t},
\]

\[
V_{\mathrm{withdraw},t}=V_{\mathrm{consumed},t}
+V_{\mathrm{discharged},t}+\Delta V_{\mathrm{stored},t}.
\]

### 9.6 ERCOT incremental load

\[
L^{\ast}_{t,h}=L^{0}_{t,h}+P_{\mathrm{grid},t,h},
\]

where \(L^0\) is the no-Terafab counterfactual and \(P_{\mathrm{grid}}\) is the facility load remaining after eligible onsite supply, storage discharge, and interruptible-load actions. Onsite generation must not be subtracted unless its availability and fuel constraints are modeled.

### 9.7 Capacity and adequacy metrics

At minimum:

\[
\Delta P_{\mathrm{peak},t}=\max_h L^{\ast}_{t,h}-\max_h L^{0}_{t,h},
\]

\[
RM_t=\frac{C_{\mathrm{accredited},t}-P_{\mathrm{peak},t}}
{P_{\mathrm{peak},t}},
\]

with loss-of-load expectation and expected unserved energy calculated for selected years when the required hourly generation, outage, weather, and load data are available. Official ERCOT/NERC definitions and standards identified in Step 2 control thresholds.

### 9.8 National incremental burden

The model must report, without conflating power and energy:

\[
s^E_t=\frac{E_{\mathrm{fab},t}}{E^{US,0}_t},
\qquad
s^P_t=\frac{P_{\mathrm{fab,peak},t}}{P^{US,0}_{\mathrm{peak},t}}.
\]

These shares do not themselves establish insecurity; they contextualize scale.

## 10. Scenario contract

The scenario matrix is defined before results are observed.

### 10.1 Target scale

- `no_build`: no incremental Terafab load; mandatory counterfactual.
- `research_fab`: publicly supported research-fab scale.
- `initial_large_scale`: first industrial large-scale phase supported by public evidence.
- `full_announced_target`: complete admitted interpretation of the public target.

Step 2 assigns evidence-supported numerical scales. No numerical value is inferred from scenario labels alone.

### 10.2 Realization pathway

- `accelerated`: earliest evidence-supported commissioning trajectory.
- `reference`: central evidence-supported trajectory.
- `delayed`: slower commissioning trajectory.
- `not_realized_by_2050`: announced target not reached within the study horizon.

Because no definitive public completion date is available, no pathway is labeled “official.”

### 10.3 Electricity-supply portfolio

- `grid_dominant`: grid supplies the facility subject to interconnection and adequacy constraints.
- `firm_onsite`: material firm onsite supply, with fuel, availability, emissions, and outage constraints.
- `renewable_storage_grid`: variable renewable generation plus storage and grid support.
- `firm_low_carbon_hybrid`: evidence-supported firm low-carbon supply combined with grid and storage.

Supply technologies are included only when their construction and operation can be parameterized from public evidence. Names do not presume that Terafab will adopt them.

No supply portfolio may be treated as unlimited or instantaneously available. Every portfolio must include evidence-supported capacity, construction lead time, accredited availability, outage behavior, interconnection timing, fuel or energy availability, and any material water constraint. A portfolio that cannot satisfy those requirements fails `supply_deliverability` rather than rescuing an otherwise infeasible pathway.

### 10.4 Stress conditions

Selected milestone years must test:

- Normal weather and availability.
- Summer peak stress.
- Winter extreme stress.
- Delayed generation or transmission commissioning.
- Yield underperformance.
- Cooling or water constraint.
- Fuel-supply or onsite-generation outage where applicable.

## 11. Required outputs

### 11.1 Manufacturing and facility

- Required monthly and annual wafer starts.
- Gross and good die or package output.
- Yield and readiness trajectory.
- Annual facility electricity and coincident peak power.
- Load factor and component energy breakdown.
- Cooling auxiliary power and heat-rejection requirement.
- Recoverable and rejected heat, with temperature/exergy context where data permit.
- Water withdrawal, consumption, reuse, and wastewater.
- Direct and electricity-related operational emissions.

### 11.2 ERCOT security

- Incremental annual TWh.
- Incremental coincident peak MW.
- Change in accredited-capacity requirement and reserve position.
- Required grid, onsite firm, renewable, and storage capacity.
- Supply construction lead time, accredited availability, and commissioned capacity by year.
- LOLE and EUE change for selected years when data support probabilistic assessment.
- Hours and magnitude of curtailment or unserved facility load.
- Natural-gas fuel requirement for gas-backed portfolios.
- Transmission/interconnection requirement represented as a constraint, not a power-flow claim unless a validated network model is available.

### 11.3 National context

- Share of US projected annual electricity.
- Share of US projected peak load.
- Incremental generation and firm-capacity requirement.
- Incremental fuel demand and operational emissions.
- Comparison with EIA reference and high-electricity-demand cases.

### 11.4 Decision outputs

- First year each individual gate is satisfied.
- First year all applicable gates are jointly satisfied.
- Feasibility probability and confidence interval under each scenario.
- Binding constraint by year and scenario.
- Global sensitivity ranking with uncertainty intervals.
- Classification: `conditionally_feasible`, `not_demonstrated`, or `indeterminate`.

## 12. Decision and gate logic

No single weighted “energy-security index” will be constructed. Such an index would embed arbitrary weights and could conceal opposing effects.

The project target is classified as `conditionally_feasible` only if at least one evidence-supported pathway simultaneously passes:

1. `target_semantics` — the modeled target interpretation is traceable and dimensionally valid.
2. `manufacturing_throughput` — throughput and yield remain within evidence-supported envelopes.
3. `facility_energy` — electricity and peak-load requirements close physically and have identified supply.
4. `thermal_capacity` — cooling and heat rejection satisfy peak and reserve requirements.
5. `water_capacity` — withdrawal, consumption, reuse, and discharge constraints pass.
6. `schedule_precedence` — supporting infrastructure precedes or coincides with manufacturing load.
7. `supply_deliverability` — generation, storage, interconnection, fuel, and supporting resources are buildable and available on the modeled schedule.
8. `regional_adequacy` — ERCOT security metrics satisfy the applicable official standard relative to the counterfactual.
9. `national_context` — national consequences are quantified; this is primarily contextual and not automatically a pass/fail gate unless Step 2 identifies an official constraint.
10. `evidence_sufficiency` — no material conclusion depends on an unbounded or undisclosed unknown.

`not_demonstrated` means no admitted pathway passes all required gates. It does not prove that the project is impossible. `indeterminate` means target semantics or indispensable evidence are insufficient for a defensible assessment.

## 13. Evidence contract for Step 2

Every material parameter must include:

- Stable parameter ID.
- Value and unit.
- Time and geographic basis.
- Evidence status from the repository’s canonical status system.
- Direct source reference and access date.
- Extraction note or transformation equation.
- Confidence and applicability note.
- Lower and upper bounds or distribution, when uncertain.
- Correlation group, when independence would be physically implausible.
- Whether it is used for calibration, validation, scenario definition, or context only.

Priority sources are official project publications and filings, EIA, NERC, ERCOT/PUCT, US government datasets, peer-reviewed semiconductor-fab measurements, and manufacturer public sustainability disclosures. News reporting may establish public context but may not be used as a substitute for primary engineering data when primary evidence exists.

No live web retrieval is permitted in the final paper reproduction path. Admitted source snapshots or extracted public datasets must be frozen and hashed.

## 14. Verification and validation contract

### 14.1 Software and equation verification

- Unit and dimensional tests for every governing equation.
- Relative residual below `1e-8` for algebraic energy and water balances, excluding explicitly documented numerical integration error.
- Deterministic reproduction under fixed inputs and random seeds.
- Backward-compatibility tests for retained core APIs.
- CLI and notebook outputs must agree bitwise for deterministic tables or within documented floating-point tolerances.

### 14.2 Empirical validation

Step 2 must seek at least:

- Two independent peer-reviewed or authoritative sources containing measured fab electricity or component loads.
- One independent source for cleanroom or cooling-system performance.
- One independent source for water or ultrapure-water intensity.
- One source for yield/throughput or a defensible public industrial envelope.
- Official ERCOT and EIA baseline projections.

Calibration and validation sources must be separated where the data allow. Required reported diagnostics are bias, MAE, RMSE or normalized RMSE, interval coverage, and residual patterns. Hard empirical error thresholds will be locked at the end of Step 2 after benchmark heterogeneity and reported measurement uncertainty are quantified; they may not be chosen after model results are known.

If independent validation data are inadequate, the paper must be framed as a prospective constraint analysis rather than a validated digital twin.

### 14.3 Uncertainty verification

- Correlated inputs must preserve declared dependence.
- Monte Carlo or quasi-random sampling must report seed and sample count.
- Key medians and tail quantiles must change by less than 1% when the final sample count is doubled, or non-convergence must be disclosed.
- Global sensitivity estimates must include uncertainty or bootstrap intervals.

## 15. Publication claims permitted by the contract

The study may conclude:

- What resource ranges are implied under stated target interpretations.
- Which constraints bind under specified pathways.
- Whether evidence-supported pathways demonstrate conditional feasibility by 2050.
- How modeled pathways alter ERCOT and national electricity-security metrics relative to public counterfactuals.
- Which additional data would most change the conclusion.

The study may not claim:

- Verified Terafab operating demand, schedule, design, costs, or performance.
- Official Terafab feasibility or infeasibility.
- A prediction that the project will or will not be built.
- Terafab, Tesla, SpaceX, xAI, Intel, ERCOT, EIA, NERC, or government endorsement.
- Investment, permitting, procurement, infrastructure-planning, or regulatory advice.
- A validated digital twin without independent physical calibration data.

## 16. Journal-fit boundary

The manuscript’s principal contribution is the coupled conversion from an unprecedented semiconductor-production target to manufacturing, facility thermodynamics, and electricity-security consequences. Policy, governance, game theory, public-benefit indices, and investment valuation are excluded from the principal analysis because they would dilute the energy-conversion contribution and introduce weakly identified weights.

The intended contribution to *Energy Conversion and Management* is:

1. A dimensionally consistent production-to-energy scaling framework.
2. Coupled electricity, heat-rejection, water, and supply-pathway calculations.
3. Prospective adequacy analysis under uncertainty.
4. Reproducible, evidence-gated scenario computation.

## 17. Step 1 completion criteria

Step 1 is complete only when:

- The primary question is falsifiable and calculation-ready.
- Target semantics are explicit and the `1 TW/year` claim is not equated to site load.
- Geographic, temporal, physical, and evidentiary boundaries are fixed.
- Scenario axes are fixed before simulation results exist.
- Required equations, outputs, gates, validation requirements, and nonclaims are defined.
- `hypotheses.json` and `model_contract.json` validate as JSON and agree with this specification.
- A stress test recommends either progression to Step 2 or revision of this contract.

## 18. Current public planning context

The following sources motivate but do not determine the results:

- EIA Annual Energy Outlook 2026: <https://www.eia.gov/outlooks/aeo/>
- NERC 2025 Long-Term Reliability Assessment, published January 2026: <https://www.nerc.com/globalassets/our-work/assessments/nerc_ltra_2025.pdf>
- ERCOT preliminary 2026–2032 long-term load forecast: <https://www.ercot.com/news/release/04152026-ercot-releases-preliminary>
- NERC characteristics and risks of emerging large loads: <https://www.nerc.com/globalassets/who-we-are/standing-committees/rstc/whitepaper-characteristics-and-risks-of-emerging-large-loads.pdf>

These current sources will be frozen, versioned, and assessed for admissibility in Step 2.
