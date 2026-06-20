SCALAR_OUTPUTS = [
    "energy_MWh",
    "average_site_load_MW",
    "peak_site_load_MW",
    "heat_rejection_required_MW",
    "minimum_heat_rejection_margin_MW",
    "cooling_auxiliary_energy_MWh",
    "water_withdrawal_m3",
    "water_consumptive_use_m3",
    "wastewater_m3",
    "minimum_water_withdrawal_margin_m3_per_day",
    "minimum_wastewater_discharge_margin_m3_per_day",
    "good_die",
    "compute_output_proxy_W",
    "average_effective_yield",
    "annualized_capex_USD",
    "total_opex_USD",
    "cost_per_good_die_USD",
    "cost_per_compute_watt_USD",
    "public_benefit_index",
    "public_burden_index",
    "legitimacy_margin",
    "maximum_governance_risk_index",
]

VECTOR_OUTPUTS = [
    "time_series.energy_MWh",
    "time_series.heat_rejection_required_MW",
    "time_series.water_withdrawal_m3",
    "time_series.good_die",
    "time_series.effective_yield",
    "time_series.public_benefit_index",
]

MATRIX_OUTPUTS = [
    "gate_results_by_time_and_gate",
    "module_output_matrix",
]

OUTPUT_METADATA = {
    "energy_MWh": {"unit": "MWh", "status": "derived_output"},
    "heat_rejection_required_MW": {"unit": "MW", "status": "derived_output"},
    "water_withdrawal_m3": {"unit": "m3", "status": "derived_output"},
    "good_die": {"unit": "die", "status": "derived_output"},
    "cost_per_good_die_USD": {"unit": "USD/good_die", "status": "derived_output"},
    "legitimacy_margin": {"unit": "index", "status": "derived_output"},
}
