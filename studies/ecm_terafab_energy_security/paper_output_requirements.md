# Preliminary Paper Output Requirements

**Study ID:** `ecm_terafab_us_energy_security`
**Contract version:** `0.1.0`

These outputs are specified before simulations are executed. Their purpose is to prevent result-driven selection of figures, tables, and comparisons. Final captions and presentation may change, but omission or replacement of a prespecified output must be justified in the result manifest.

## Figures

### Figure 1 — Claim-to-consequence architecture

A system diagram separating:

1. Public target wording.
2. Target interpretation.
3. Device and wafer throughput.
4. Facility electricity, heat, and water.
5. Deployment and supply portfolio.
6. ERCOT and United States consequences.

The diagram must visually distinguish product output from factory electrical load.

### Figure 2 — Target-translation feasibility surface

Required monthly wafer starts as a function of effective yield and rated device or package power for the full target. Evidence-supported parameter regions must be shown separately from extrapolated regions.

### Figure 3 — Independent benchmark validation

Measured versus modeled electricity, cooling, or water metrics, including uncertainty intervals, identity line, error metrics, and separation between calibration and validation observations.

### Figure 4 — Terafab realization pathways, 2026–2050

Annual target fraction, wafer throughput, facility peak load, and facility electricity for accelerated, reference, delayed, and non-realization pathways.

### Figure 5 — Facility thermodynamic and water decomposition

Component electricity, cooling power, heat rejection, recoverable heat where supportable, water withdrawal, consumption, reuse, and discharge at principal milestones.

### Figure 6 — ERCOT incremental burden

Incremental coincident peak load, annual electricity, accredited capacity requirement, and reserve-position change relative to the no-build counterfactual. Official counterfactual uncertainty must be visible.

### Figure 7 — Adequacy consequences by supply portfolio

LOLE, expected unserved energy, or the strongest authoritative adequacy metrics available for grid-dominant, firm-onsite, renewable-storage-grid, and firm-low-carbon-hybrid portfolios in selected milestone and stress years.

If probabilistic adequacy data cannot be constructed, this figure must be replaced by an explicitly limited accredited-capacity and reserve-margin analysis, not by invented reliability probabilities.

### Figure 8 — National scale and fuel exposure

Share of projected US annual electricity and peak load, required firm additions, fuel demand, and operational emissions across EIA reference and high-demand counterfactuals.

### Figure 9 — Feasibility map

Gate status and first joint-pass year across target-scale, deployment, supply, and stress cases. `Indeterminate` cases must be visually different from failed cases.

### Figure 10 — Global sensitivity and convergence

First- and total-order sensitivity indices with uncertainty intervals, plus convergence of key medians and tail quantiles as sample size increases.

## Tables

### Table 1 — Public claims and admitted interpretations

Original public wording, source, date, evidence status, admitted engineering interpretation, excluded interpretations, and uncertainty note.

### Table 2 — Model variables and equations

Symbol, definition, unit, temporal basis, equation, evidence class, and model module.

### Table 3 — Evidence and validation dataset

Source type, facility/process context, measured metrics, use as calibration or validation, applicability, limitations, and checksum reference.

### Table 4 — Scenario matrix

Target scale, realization pathway, supply portfolio, stress condition, target semantics, and counterfactual baseline.

### Table 5 — Principal results by pathway

Realization year, throughput, peak load, annual electricity, heat rejection, water, firm capacity, adequacy metrics, binding constraint, and feasibility classification.

### Table 6 — Verification and validation

Conservation residuals, software tests, empirical error metrics, interval coverage, uncertainty convergence, and reproduction status.

## Supplementary material

- Complete evidence and parameter registers.
- Scenario JSON files.
- Full yearly output tables for 2026–2050.
- Hourly milestone-year outputs where admitted.
- Complete gate matrix.
- Sensitivity samples or deterministic regeneration instructions.
- Figure and table manifest with source hashes.
- Notebook and command-line reproduction instructions.

## Output integrity rules

1. Every plotted value must exist in a machine-readable output table.
2. The notebook and CLI must call the same Python functions.
3. Figure labels must preserve power-versus-energy dimensions.
4. Public claims, evidence-supported parameters, assumptions, and derived outputs must be visually and textually distinguishable.
5. No result may be promoted from assumption to verified fact.
6. Failed, passed, and indeterminate gates must remain distinct.
