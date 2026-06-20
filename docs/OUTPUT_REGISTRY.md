# Output Registry

Every run emits scalar, vector, and matrix outputs.

## Scalar records

`output_records` contain:

```text
name
kind
value
unit
scenario_id
source_status
equation_ref
assumptions_used
warning_flags
reproducibility_hash
```

## Registered scalar outputs

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

`time_series` contains one row per model period. Rows include time labels and system state outputs.

## Matrices

- `gate_matrix`: gate by period with severity, status, margin, and message.
- `module_output_matrix`: formal module outputs.
- `partner_allocation_matrix`: governance allocation structure.
- `subsystem_state_matrix`: power, cooling, water, and readiness state by period.
