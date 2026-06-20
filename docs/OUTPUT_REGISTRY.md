# Output Registry

## Scalars

The v1 engine returns scalar summaries including:

- `energy_MWh`
- `average_site_load_MW`
- `peak_site_load_MW`
- `minimum_firm_capacity_margin_MW`
- `heat_rejection_required_MW`
- `minimum_heat_rejection_margin_MW`
- `cooling_auxiliary_energy_MWh`
- `entropy_generation_MW_per_K`
- `exergy_destroyed_MW`
- `average_exergy_efficiency`
- `water_withdrawal_m3`
- `water_consumptive_use_m3`
- `wastewater_m3`
- `minimum_water_withdrawal_margin_m3_per_day`
- `minimum_wastewater_discharge_margin_m3_per_day`
- `good_die`
- `compute_output_proxy_W`
- `average_effective_yield`
- `average_readiness_index`
- `annualized_capex_USD`
- `total_opex_USD`
- `total_cost_USD`
- `cost_per_good_die_USD`
- `cost_per_compute_watt_USD`
- `emissions_tCO2`
- `public_benefit_index`
- `public_burden_index`
- `legitimacy_margin`
- `maximum_governance_risk_index`
- `recommended_phase_action`

## Vectors

Each run returns a `time_series` list with one row per model period.

## Gate matrix

Each run returns a gate table with gate name, pass/fail state, severity, margin, and message.
