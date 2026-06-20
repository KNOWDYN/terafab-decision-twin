from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List

SCALAR_OUTPUTS = [
    "energy_MWh", "average_site_load_MW", "peak_site_load_MW", "minimum_firm_capacity_margin_MW",
    "heat_rejection_required_MW", "minimum_heat_rejection_margin_MW", "cooling_auxiliary_energy_MWh",
    "entropy_generation_MW_per_K", "exergy_destroyed_MW", "average_exergy_efficiency",
    "water_withdrawal_m3", "water_consumptive_use_m3", "wastewater_m3",
    "minimum_water_withdrawal_margin_m3_per_day", "minimum_wastewater_discharge_margin_m3_per_day",
    "good_die", "compute_output_proxy_W", "average_effective_yield", "average_readiness_index",
    "annualized_capex_USD", "total_opex_USD", "total_cost_USD", "cost_per_good_die_USD",
    "cost_per_compute_watt_USD", "emissions_tCO2", "public_benefit_index", "public_burden_index",
    "legitimacy_margin", "maximum_governance_risk_index"
]

VECTOR_OUTPUTS = [
    "time_series.energy_MWh", "time_series.heat_rejection_required_MW", "time_series.water_withdrawal_m3",
    "time_series.good_die", "time_series.effective_yield", "time_series.public_benefit_index",
    "time_series.exergy_destroyed_MW"
]

MATRIX_OUTPUTS = [
    "gate_matrix", "module_output_matrix", "partner_allocation_matrix", "subsystem_state_matrix"
]

OUTPUT_UNITS = {
    "energy_MWh": "MWh", "average_site_load_MW": "MW", "peak_site_load_MW": "MW",
    "minimum_firm_capacity_margin_MW": "MW", "heat_rejection_required_MW": "MW",
    "minimum_heat_rejection_margin_MW": "MW", "cooling_auxiliary_energy_MWh": "MWh",
    "entropy_generation_MW_per_K": "MW/K", "exergy_destroyed_MW": "MW", "average_exergy_efficiency": "fraction",
    "water_withdrawal_m3": "m3", "water_consumptive_use_m3": "m3", "wastewater_m3": "m3",
    "minimum_water_withdrawal_margin_m3_per_day": "m3/day", "minimum_wastewater_discharge_margin_m3_per_day": "m3/day",
    "good_die": "die", "compute_output_proxy_W": "W", "average_effective_yield": "fraction", "average_readiness_index": "fraction",
    "annualized_capex_USD": "USD/year", "total_opex_USD": "USD", "total_cost_USD": "USD", "cost_per_good_die_USD": "USD/die",
    "cost_per_compute_watt_USD": "USD/W", "emissions_tCO2": "tCO2", "public_benefit_index": "index",
    "public_burden_index": "index", "legitimacy_margin": "index", "maximum_governance_risk_index": "index",
}

OUTPUT_EQUATIONS = {
    "energy_MWh": "P_load * hours * load_factor",
    "minimum_firm_capacity_margin_MW": "firm_capacity - peak_load*(1+reserve_margin)",
    "heat_rejection_required_MW": "P_IT*heat_fraction + process_heat + aux_heat - useful_work",
    "minimum_heat_rejection_margin_MW": "cooling_capacity*(1-reserve_margin)-heat_required",
    "water_withdrawal_m3": "energy_MWh*withdrawal_intensity + wafer_starts*UPW_per_wafer",
    "minimum_water_withdrawal_margin_m3_per_day": "permit*(1-reserve_margin)-daily_withdrawal",
    "minimum_wastewater_discharge_margin_m3_per_day": "permit*(1-reserve_margin)-daily_wastewater",
    "exergy_destroyed_MW": "T0 * entropy_generation",
    "good_die": "wafer_starts * die_per_wafer * effective_yield",
    "cost_per_good_die_USD": "total_cost/good_die",
    "legitimacy_margin": "public_benefit_index - public_burden_index",
}

@dataclass(frozen=True)
class OutputRecord:
    name: str
    value: Any
    unit: str
    kind: str
    time_index: str | None
    scenario_id: str
    source_status: str
    equation_ref: str
    assumptions_used: List[str]
    warning_flags: List[str]
    reproducibility_hash: str
    confidence_note: str = "Derived from scenario inputs; not a verified operating fact."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def output_metadata(name: str) -> Dict[str, str]:
    return {
        "unit": OUTPUT_UNITS.get(name, ""),
        "status": "derived_output",
        "equation_ref": OUTPUT_EQUATIONS.get(name, "registered_model_equation"),
    }


def build_output_records(summary: Dict[str, Any], *, scenario_id: str, assumptions_used: List[str], warning_flags: List[str], result_hash: str) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for name in SCALAR_OUTPUTS:
        meta = output_metadata(name)
        records.append(OutputRecord(
            name=name,
            value=summary.get(name),
            unit=meta["unit"],
            kind="scalar",
            time_index=None,
            scenario_id=scenario_id,
            source_status="derived_output",
            equation_ref=meta["equation_ref"],
            assumptions_used=assumptions_used,
            warning_flags=warning_flags,
            reproducibility_hash=result_hash,
        ).to_dict())
    return records
