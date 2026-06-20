from __future__ import annotations

import hashlib
import json
from math import isfinite
from typing import Any, Dict, List

from .evidence import (
    audit_evidence, summarize_statuses, status_of, unit_of, collect_assumptions,
    collect_verified_facts, normalize_status, is_evidence_object, source_of
)
from .schema import assert_valid_scenario
from .time_axis import build_time_axis
from .models.first_law import heat_rejection_required_MW
from .models.entropy import heat_transfer_entropy_generation_MW_per_K
from .models.exergy import heat_exergy_MW, exergy_destroyed_MW, exergy_efficiency
from .models.power import energy_consumption_MWh, firm_capacity_margin_MW, emissions_tCO2, electricity_cost_USD
from .models.cooling import cooling_auxiliary_power_MW, heat_rejection_margin_with_reserve_MW
from .models.water import withdrawal_m3, consumptive_use_m3, wastewater_m3, permit_margin_with_reserve_m3_per_day, upw_demand_m3
from .models.manufacturing import learned_yield, effective_yield, good_die_output, compute_output_proxy
from .models.readiness import readiness_index, readiness_bottleneck
from .models.economics import annualized_capex_USD, water_cost_USD, emissions_cost_USD, cost_per_good_die_USD, cost_per_compute_watt_USD
from .models.governance import governance_risk_index, governance_readiness
from .models.policy import public_benefit_index, public_burden_index, legitimacy_margin
from .models.real_options import phase_gate_value, recommend_phase_action
from .models.gates import evaluate_gates, overall_passed
from .outputs import build_output_records, SCALAR_OUTPUTS, VECTOR_OUTPUTS, MATRIX_OUTPUTS
from .units import DAYS_PER_YEAR, safe_div
from .cleanroom import CleanroomState, cleanroom_readiness, particle_control_index
from .contamination import ContaminationState, contamination_loss_fraction, contamination_readiness as contamination_readiness_fn
from .packaging import PackagingState, packaging_readiness as packaging_readiness_fn, packaging_capacity_good_die_limit
from .qualification import QualificationState, qualification_readiness as qualification_readiness_fn
from .evidence_bayes import bayes_update, posterior_to_status

MODEL_VERSION = "0.3.0"


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class InputReader:
    def __init__(self, scenario: Dict[str, Any], allow_unknown_substitution: bool = False):
        self.scenario = scenario
        self.allow_unknown_substitution = allow_unknown_substitution
        self.unresolved: List[Dict[str, Any]] = []
        self.substitutions: List[Dict[str, Any]] = []
        self.assumption_paths: List[str] = []

    def _raw(self, section: Dict[str, Any], key: str, default: Any = None, *, section_name: str = "") -> tuple[Any, str, str]:
        path = f"{section_name}.{key}" if section_name else key
        if key not in section:
            return default, "scenario_assumption", path
        value = section.get(key)
        if is_evidence_object(value):
            status = status_of(value)
            if status in {"scenario_assumption", "stress_test_assumption", "user_provided"}:
                self.assumption_paths.append(path)
            return value.get("value", default), status, path
        self.assumption_paths.append(path)
        return value, "scenario_assumption", path

    def number(self, section: Dict[str, Any], key: str, default: float = 0.0, *, required: bool = False, section_name: str = "", unit: str = "") -> float:
        raw, status, path = self._raw(section, key, default, section_name=section_name)
        is_unknown = status == "unknown" or raw in (None, "", "unknown")
        if is_unknown:
            rec = {"path": path, "status": status, "unit": unit, "reason": "Material input is unknown or missing."}
            self.unresolved.append(rec)
            if required and not self.allow_unknown_substitution:
                self.substitutions.append({**rec, "substituted_value": None, "mode": "underdetermined"})
                return float(default)
            self.substitutions.append({**rec, "substituted_value": float(default), "mode": "explicit_nonconclusive_substitution"})
            return float(default)
        try:
            return float(raw)
        except Exception as exc:
            rec = {"path": path, "status": status, "unit": unit, "reason": f"Could not parse numeric value: {exc}"}
            self.unresolved.append(rec)
            self.substitutions.append({**rec, "substituted_value": float(default), "mode": "explicit_nonconclusive_substitution"})
            return float(default)

    def integer(self, section: Dict[str, Any], key: str, default: int = 0, *, required: bool = False, section_name: str = "", unit: str = "") -> int:
        return int(round(self.number(section, key, default, required=required, section_name=section_name, unit=unit)))

    def text(self, section: Dict[str, Any], key: str, default: str = "unknown", *, section_name: str = "") -> str:
        raw, status, path = self._raw(section, key, default, section_name=section_name)
        if status == "unknown" or raw in (None, "", "unknown"):
            self.unresolved.append({"path": path, "status": status, "unit": "category", "reason": "Categorical input is unknown."})
            return default
        return str(raw)


def _safe_total(ts: List[Dict[str, Any]], key: str) -> float:
    return sum(float(row.get(key, 0.0) or 0.0) for row in ts)


def _safe_avg(ts: List[Dict[str, Any]], key: str) -> float:
    return safe_div(_safe_total(ts, key), len(ts), 0.0)


def _safe_min(ts: List[Dict[str, Any]], key: str) -> float:
    return min(float(row.get(key, 0.0) or 0.0) for row in ts) if ts else 0.0


def _safe_max(ts: List[Dict[str, Any]], key: str) -> float:
    return max(float(row.get(key, 0.0) or 0.0) for row in ts) if ts else 0.0


def run_scenario(scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Run the evidence-gated time-step solver for a scenario dictionary."""
    assert_valid_scenario(scenario)

    axis = build_time_axis(scenario["time"])
    energy = scenario["energy"]
    cooling = scenario["cooling"]
    water = scenario["water"]
    mfg = scenario["manufacturing"]
    econ = scenario["economics"]
    gov = scenario["governance"]
    pol = scenario["policy"]
    phase = scenario["terafab_phase"]
    control = scenario.get("control", {})

    strict = bool(control.get("strict_evidence", False))
    allow_unknown_substitution = bool(control.get("allow_unknown_substitution", False))
    reader = InputReader(scenario, allow_unknown_substitution=allow_unknown_substitution)

    evidence_issues = audit_evidence(scenario, strict=strict)
    evidence_errors = [f"{i.path}: {i.message}" for i in evidence_issues if i.severity == "error"]
    evidence_warnings = [f"{i.path}: {i.message}" for i in evidence_issues if i.severity == "warning"]

    load_MW = reader.number(energy, "site_electric_load_MW", required=True, section_name="energy", unit="MW")
    load_factor = reader.number(energy, "load_factor", 1.0, required=True, section_name="energy", unit="fraction")
    firm_capacity_MW = reader.number(energy, "firm_capacity_MW", required=True, section_name="energy", unit="MW")
    reserve_margin_fraction = reader.number(energy, "reserve_margin_fraction", 0.15, section_name="energy", unit="fraction")
    carbon_intensity = reader.number(energy, "grid_carbon_intensity_kg_per_MWh", 0.0, section_name="energy", unit="kg/MWh")

    heat_fraction = reader.number(cooling, "heat_rejection_fraction", 0.98, required=True, section_name="cooling", unit="fraction")
    waste_heat_MW = reader.number(cooling, "waste_heat_MW", 0.0, section_name="cooling", unit="MW")
    heat_capacity_MW = reader.number(cooling, "heat_rejection_capacity_MW", required=True, section_name="cooling", unit="MW")
    cooling_reserve_margin_fraction = reader.number(cooling, "cooling_reserve_margin_fraction", 0.0, section_name="cooling", unit="fraction")
    cop = reader.number(cooling, "cop", 5.0, required=True, section_name="cooling", unit="ratio")
    hot_K = reader.number(cooling, "hot_reservoir_K", 315.0, section_name="cooling", unit="K")
    cold_K = reader.number(cooling, "cold_reservoir_K", 298.15, section_name="cooling", unit="K")
    ambient_K = reader.number(cooling, "ambient_temperature_K", 298.15, section_name="cooling", unit="K")

    withdrawal_intensity = reader.number(water, "withdrawal_m3_per_MWh", 0.0, required=True, section_name="water", unit="m3/MWh")
    consumptive_fraction = reader.number(water, "consumptive_fraction", 0.0, section_name="water", unit="fraction")
    wastewater_fraction = reader.number(water, "wastewater_fraction", max(0.0, 1.0 - consumptive_fraction), section_name="water", unit="fraction")
    permit_withdrawal = reader.number(water, "permit_withdrawal_m3_per_day", 0.0, required=True, section_name="water", unit="m3/day")
    permit_discharge = reader.number(water, "permit_discharge_m3_per_day", permit_withdrawal, section_name="water", unit="m3/day")
    water_reserve_margin_fraction = reader.number(water, "water_reserve_margin_fraction", 0.0, section_name="water", unit="fraction")
    wastewater_reserve_margin_fraction = reader.number(water, "wastewater_reserve_margin_fraction", water_reserve_margin_fraction, section_name="water", unit="fraction")
    upw_per_wafer = reader.number(water, "upw_m3_per_wafer", 0.0, section_name="water", unit="m3/wafer")

    wafer_starts_per_month = reader.number(mfg, "wafer_starts_per_month", 0.0, required=True, section_name="manufacturing", unit="wafers/month")
    die_per_wafer = reader.number(mfg, "die_per_wafer", 0.0, required=True, section_name="manufacturing", unit="die/wafer")
    base_yield = reader.number(mfg, "baseline_yield", 0.0, required=True, section_name="manufacturing", unit="fraction")
    learning_rate = reader.number(mfg, "learning_rate_per_year", 0.0, section_name="manufacturing", unit="fraction/year")
    contamination_loss_declared = reader.number(mfg, "contamination_loss_fraction", 0.0, section_name="manufacturing", unit="fraction")
    qualification_readiness_declared = reader.number(mfg, "qualification_readiness", 1.0, section_name="manufacturing", unit="fraction")
    contamination_readiness_declared = reader.number(mfg, "contamination_readiness", 1.0, section_name="manufacturing", unit="fraction")
    packaging_readiness_declared = reader.number(mfg, "packaging_readiness", 1.0, section_name="manufacturing", unit="fraction")
    compute_watts_per_good_die = reader.number(mfg, "compute_watts_per_good_die", 0.0, section_name="manufacturing", unit="W/die")
    chemical_control_index = reader.number(mfg, "chemical_control_index", 1.0, section_name="manufacturing", unit="fraction")
    excursion_rate_per_year = reader.number(mfg, "excursion_rate_per_year", 0.0, section_name="manufacturing", unit="1/year")
    filtration_efficiency = reader.number(mfg, "filtration_efficiency", 0.99, section_name="manufacturing", unit="fraction")
    airflow_turnovers_per_hour = reader.number(mfg, "airflow_turnovers_per_hour", 80.0, section_name="manufacturing", unit="1/hour")
    particle_load_index = reader.number(mfg, "particle_load_index", 0.1, section_name="manufacturing", unit="index")
    thermal_stability_index = reader.number(mfg, "thermal_stability_index", 1.0, section_name="manufacturing", unit="fraction")
    substrate_availability_index = reader.number(mfg, "substrate_availability_index", packaging_readiness_declared, section_name="manufacturing", unit="fraction")
    advanced_packaging_capacity_index = reader.number(mfg, "advanced_packaging_capacity_index", packaging_readiness_declared, section_name="manufacturing", unit="fraction")
    interconnect_yield_index = reader.number(mfg, "interconnect_yield_index", packaging_readiness_declared, section_name="manufacturing", unit="fraction")
    tool_qualification_index = reader.number(mfg, "tool_qualification_index", qualification_readiness_declared, section_name="manufacturing", unit="fraction")
    process_window_index = reader.number(mfg, "process_window_index", qualification_readiness_declared, section_name="manufacturing", unit="fraction")
    customer_acceptance_index = reader.number(mfg, "customer_acceptance_index", qualification_readiness_declared, section_name="manufacturing", unit="fraction")

    electricity_price = reader.number(econ, "electricity_price_USD_per_MWh", 0.0, required=True, section_name="economics", unit="USD/MWh")
    water_price = reader.number(econ, "water_price_USD_per_m3", 0.0, required=True, section_name="economics", unit="USD/m3")
    capex = reader.number(econ, "capex_USD", 0.0, required=True, section_name="economics", unit="USD")
    fixed_opex = reader.number(econ, "annual_fixed_opex_USD", 0.0, section_name="economics", unit="USD/year")
    discount_rate = reader.number(econ, "discount_rate", 0.08, section_name="economics", unit="fraction")
    asset_life = reader.integer(econ, "asset_life_years", 20, section_name="economics", unit="years")
    incentive = reader.number(econ, "incentive_public_USD", 0.0, section_name="economics", unit="USD")

    jobs = reader.number(pol, "jobs_created", 0.0, required=True, section_name="policy", unit="jobs")
    domestic_supply = reader.number(pol, "domestic_supply_security_index", 0.0, required=True, section_name="policy", unit="index")
    water_stress = reader.number(pol, "local_water_stress_index", 0.0, section_name="policy", unit="index")
    public_legitimacy = reader.number(pol, "public_legitimacy_index", 0.0, required=True, section_name="policy", unit="index")
    regulatory_readiness = reader.number(pol, "regulatory_readiness_index", 0.0, section_name="policy", unit="index")
    emissions_price = reader.number(pol, "emissions_price_USD_per_tCO2", 0.0, section_name="policy", unit="USD/tCO2")

    partner_count = reader.integer(gov, "partner_count", 1, required=True, section_name="governance", unit="count")
    gov_complexity = reader.number(gov, "governance_complexity_index", 0.0, required=True, section_name="governance", unit="index")
    decision_latency = reader.number(gov, "decision_latency_months", 0.0, section_name="governance", unit="months")

    phase_name = reader.text(phase, "phase", "unknown", section_name="terafab_phase")
    one_tw_status = status_of(phase.get("one_terawatt_treatment", {}), "scenario_assumption")

    annual_capex = annualized_capex_USD(capex, discount_rate, asset_life)
    clean_state = CleanroomState(airflow_turnovers_per_hour, filtration_efficiency, particle_load_index, thermal_stability_index)
    particle_index = particle_control_index(airflow_turnovers_per_hour, filtration_efficiency, particle_load_index)
    cleanroom_index = cleanroom_readiness(clean_state)
    contamination_state = ContaminationState(particle_index, chemical_control_index, excursion_rate_per_year)
    contamination_loss_modeled = contamination_loss_fraction(particle_index, chemical_control_index, excursion_rate_per_year)
    contamination_readiness_modeled = contamination_readiness_fn(contamination_state)
    packaging_state = PackagingState(substrate_availability_index, advanced_packaging_capacity_index, interconnect_yield_index)
    packaging_readiness_modeled = packaging_readiness_fn(packaging_state)
    qualification_state = QualificationState(tool_qualification_index, process_window_index, customer_acceptance_index, regulatory_readiness)
    qualification_readiness_modeled = qualification_readiness_fn(qualification_state)
    effective_contamination_loss = max(contamination_loss_declared, contamination_loss_modeled)
    effective_qualification_readiness = min(qualification_readiness_declared, qualification_readiness_modeled)
    effective_contamination_readiness = min(contamination_readiness_declared, contamination_readiness_modeled, cleanroom_index)
    effective_packaging_readiness = min(packaging_readiness_declared, packaging_readiness_modeled)

    ts: List[Dict[str, Any]] = []
    for step in axis:
        years_since_start = step.year - int(scenario["time"].get("start_year", 2026)) + (step.period - 1) * step.fraction_of_year
        energy_MWh = energy_consumption_MWh(load_MW, step.hours, load_factor)
        heat_required_MW = heat_rejection_required_MW(load_MW, heat_fraction, waste_heat_MW)
        heat_margin_MW = heat_rejection_margin_with_reserve_MW(heat_capacity_MW, heat_required_MW, cooling_reserve_margin_fraction)
        cooling_power_MW = cooling_auxiliary_power_MW(heat_required_MW, cop)
        cooling_energy_MWh = cooling_power_MW * step.hours * load_factor
        entropy_gen = heat_transfer_entropy_generation_MW_per_K(heat_required_MW, hot_K, cold_K)
        destroyed_MW = exergy_destroyed_MW(ambient_K, entropy_gen)
        heat_exergy = heat_exergy_MW(heat_required_MW, hot_K, ambient_K)
        ex_eff = exergy_efficiency(max(0.0, heat_exergy - destroyed_MW), max(heat_exergy, 1e-12))
        emissions = emissions_tCO2(energy_MWh, carbon_intensity)

        withdraw = withdrawal_m3(energy_MWh, withdrawal_intensity)
        wafer_starts = wafer_starts_per_month * 12.0 * step.fraction_of_year
        upw = upw_demand_m3(wafer_starts, upw_per_wafer)
        total_withdraw = withdraw + upw
        consume = consumptive_use_m3(total_withdraw, consumptive_fraction)
        waste = wastewater_m3(total_withdraw, wastewater_fraction)
        days = DAYS_PER_YEAR * step.fraction_of_year
        withdrawal_margin = permit_margin_with_reserve_m3_per_day(total_withdraw, permit_withdrawal, water_reserve_margin_fraction, days)
        discharge_margin = permit_margin_with_reserve_m3_per_day(waste, permit_discharge, wastewater_reserve_margin_fraction, days)

        learned = learned_yield(base_yield, learning_rate, years_since_start)
        readiness = readiness_index(effective_qualification_readiness, effective_contamination_readiness, effective_packaging_readiness, regulatory_readiness)
        eff_yield = effective_yield(learned, effective_contamination_loss, effective_qualification_readiness * effective_contamination_readiness, effective_packaging_readiness)
        good_die = good_die_output(wafer_starts, die_per_wafer, eff_yield)
        # If packaging capacity is modeled as an index, treat it as a readiness factor rather than a hard cap in v0.2.
        good_die = packaging_capacity_good_die_limit(good_die, good_die if effective_packaging_readiness > 0 else 0.0)
        compute_watts = compute_output_proxy(good_die, compute_watts_per_good_die)

        electricity_cost = electricity_cost_USD(energy_MWh, electricity_price)
        water_cost = water_cost_USD(total_withdraw, water_price)
        emissions_cost = emissions_cost_USD(emissions, emissions_price)
        fixed_opex_step = fixed_opex * step.fraction_of_year
        opex = electricity_cost + water_cost + emissions_cost + fixed_opex_step

        pbi = public_benefit_index(domestic_supply, jobs, public_legitimacy, water_stress, emissions, energy_MWh)
        burden = public_burden_index(incentive, water_stress, emissions, energy_MWh)
        lm = legitimacy_margin(pbi, burden)
        gr = governance_risk_index(partner_count, gov_complexity, decision_latency, public_legitimacy)
        gready = governance_readiness(public_legitimacy, regulatory_readiness, gov_complexity)
        option_value = phase_gate_value(expected_value_USD=max(0.0, compute_watts), option_cost_USD=annual_capex * step.fraction_of_year, readiness=readiness, risk_index=gr)

        row = {
            "label": step.label,
            "year": step.year,
            "period": step.period,
            "hours": step.hours,
            "phase": phase_name,
            "site_electric_load_MW": load_MW,
            "energy_MWh": energy_MWh,
            "firm_capacity_margin_MW": firm_capacity_margin_MW(firm_capacity_MW, load_MW, reserve_margin_fraction),
            "heat_rejection_required_MW": heat_required_MW,
            "heat_rejection_capacity_MW": heat_capacity_MW,
            "heat_rejection_margin_MW": heat_margin_MW,
            "cooling_reserve_margin_fraction": cooling_reserve_margin_fraction,
            "cooling_auxiliary_power_MW": cooling_power_MW,
            "cooling_auxiliary_energy_MWh": cooling_energy_MWh,
            "entropy_generation_MW_per_K": entropy_gen,
            "exergy_destroyed_MW": destroyed_MW,
            "heat_exergy_MW": heat_exergy,
            "exergy_efficiency": ex_eff,
            "water_withdrawal_m3": total_withdraw,
            "water_consumptive_use_m3": consume,
            "wastewater_m3": waste,
            "water_reserve_margin_fraction": water_reserve_margin_fraction,
            "wastewater_reserve_margin_fraction": wastewater_reserve_margin_fraction,
            "water_withdrawal_margin_m3_per_day": withdrawal_margin,
            "wastewater_discharge_margin_m3_per_day": discharge_margin,
            "cleanroom_readiness_index": cleanroom_index,
            "particle_control_index": particle_index,
            "contamination_loss_fraction": effective_contamination_loss,
            "contamination_readiness_index": effective_contamination_readiness,
            "qualification_readiness_index": effective_qualification_readiness,
            "packaging_readiness_index": effective_packaging_readiness,
            "effective_yield": eff_yield,
            "readiness_index": readiness,
            "readiness_bottleneck": readiness_bottleneck({"qualification": effective_qualification_readiness, "contamination": effective_contamination_readiness, "packaging": effective_packaging_readiness, "regulatory": regulatory_readiness}),
            "good_die": good_die,
            "compute_output_proxy_W": compute_watts,
            "electricity_cost_USD": electricity_cost,
            "water_cost_USD": water_cost,
            "emissions_tCO2": emissions,
            "emissions_cost_USD": emissions_cost,
            "opex_USD": opex,
            "public_benefit_index": pbi,
            "public_burden_index": burden,
            "legitimacy_margin": lm,
            "governance_risk_index": gr,
            "governance_readiness_index": gready,
            "phase_gate_value_USD": option_value,
            "phase_action": recommend_phase_action(option_value, readiness, gr),
        }
        ts.append(row)

    total_year_fraction = sum(step.fraction_of_year for step in axis)
    total_cost = annual_capex * total_year_fraction + _safe_total(ts, "opex_USD")
    good_die_total = _safe_total(ts, "good_die")
    compute_total = _safe_total(ts, "compute_output_proxy_W")
    cpg = cost_per_good_die_USD(total_cost, good_die_total)
    cpw = cost_per_compute_watt_USD(total_cost, compute_total)

    summary = {
        "scenario_id": scenario["metadata"].get("scenario_id"),
        "time_steps": len(ts),
        "energy_MWh": _safe_total(ts, "energy_MWh"),
        "average_site_load_MW": load_MW,
        "peak_site_load_MW": load_MW,
        "minimum_firm_capacity_margin_MW": _safe_min(ts, "firm_capacity_margin_MW"),
        "heat_rejection_required_MW": _safe_max(ts, "heat_rejection_required_MW"),
        "minimum_heat_rejection_margin_MW": _safe_min(ts, "heat_rejection_margin_MW"),
        "cooling_auxiliary_energy_MWh": _safe_total(ts, "cooling_auxiliary_energy_MWh"),
        "entropy_generation_MW_per_K": _safe_avg(ts, "entropy_generation_MW_per_K"),
        "exergy_destroyed_MW": _safe_avg(ts, "exergy_destroyed_MW"),
        "average_exergy_efficiency": _safe_avg(ts, "exergy_efficiency"),
        "water_withdrawal_m3": _safe_total(ts, "water_withdrawal_m3"),
        "water_consumptive_use_m3": _safe_total(ts, "water_consumptive_use_m3"),
        "wastewater_m3": _safe_total(ts, "wastewater_m3"),
        "minimum_water_withdrawal_margin_m3_per_day": _safe_min(ts, "water_withdrawal_margin_m3_per_day"),
        "minimum_wastewater_discharge_margin_m3_per_day": _safe_min(ts, "wastewater_discharge_margin_m3_per_day"),
        "good_die": good_die_total,
        "compute_output_proxy_W": compute_total,
        "average_effective_yield": _safe_avg(ts, "effective_yield"),
        "average_readiness_index": _safe_avg(ts, "readiness_index"),
        "average_cleanroom_readiness_index": _safe_avg(ts, "cleanroom_readiness_index"),
        "average_contamination_readiness_index": _safe_avg(ts, "contamination_readiness_index"),
        "average_packaging_readiness_index": _safe_avg(ts, "packaging_readiness_index"),
        "average_qualification_readiness_index": _safe_avg(ts, "qualification_readiness_index"),
        "annualized_capex_USD": annual_capex,
        "total_opex_USD": _safe_total(ts, "opex_USD"),
        "total_cost_USD": total_cost,
        "cost_per_good_die_USD": cpg,
        "cost_per_compute_watt_USD": cpw,
        "emissions_tCO2": _safe_total(ts, "emissions_tCO2"),
        "public_benefit_index": _safe_avg(ts, "public_benefit_index"),
        "public_burden_index": _safe_avg(ts, "public_burden_index"),
        "legitimacy_margin": _safe_avg(ts, "legitimacy_margin"),
        "maximum_governance_risk_index": _safe_max(ts, "governance_risk_index"),
        "recommended_phase_action": ts[-1]["phase_action"] if ts else "none",
        "one_terawatt_status": one_tw_status,
    }

    if reader.unresolved:
        for key in ["cost_per_good_die_USD", "cost_per_compute_watt_USD"]:
            summary[key] = None

    gates = evaluate_gates(summary, evidence_errors=evidence_errors, unresolved_variables=reader.unresolved)
    gate_matrix = [
        {"time_index": row["label"], "gate": g.name, "passed": g.passed, "severity": g.severity, "margin": g.margin}
        for row in ts for g in gates
    ]
    module_output_matrix = [
        {"module": "power", "time_index": row["label"], "energy_MWh": row["energy_MWh"], "firm_capacity_margin_MW": row["firm_capacity_margin_MW"]} for row in ts
    ] + [
        {"module": "water", "time_index": row["label"], "water_withdrawal_m3": row["water_withdrawal_m3"], "withdrawal_margin_m3_per_day": row["water_withdrawal_margin_m3_per_day"]} for row in ts
    ] + [
        {"module": "manufacturing", "time_index": row["label"], "good_die": row["good_die"], "effective_yield": row["effective_yield"]} for row in ts
    ]
    partner_allocation_matrix = [{"partner": f"partner_{i+1}", "allocation_fraction": safe_div(1.0, max(partner_count, 1), 0.0)} for i in range(max(partner_count, 1))]
    subsystem_state_matrix = [{
        "time_index": row["label"],
        "power_margin_MW": row["firm_capacity_margin_MW"],
        "cooling_margin_MW": row["heat_rejection_margin_MW"],
        "water_margin_m3_per_day": row["water_withdrawal_margin_m3_per_day"],
        "readiness_index": row["readiness_index"],
    } for row in ts]

    assumptions = collect_assumptions(scenario)
    verified_facts = collect_verified_facts(scenario)
    assumption_paths = sorted(set([row["path"] for row in assumptions] + reader.assumption_paths))
    warning_flags = ["evidence_warnings"] if evidence_warnings else []
    if reader.unresolved:
        warning_flags.append("underdetermined_outputs")
    if one_tw_status == "stress_test_assumption":
        warning_flags.append("one_terawatt_is_stress_test_only")

    for key, val in list(summary.items()):
        if isinstance(val, float) and not isfinite(val):
            summary[key] = None

    result = {
        "metadata": {
            "package": "terafab-decision-twin",
            "version": MODEL_VERSION,
            "scenario_id": scenario["metadata"].get("scenario_id"),
            "title": scenario["metadata"].get("title"),
            "model_version": scenario["metadata"].get("model_version", MODEL_VERSION),
            "schema_version": scenario["metadata"].get("schema_version", "0.2.0"),
            "source_bundle_version": scenario["metadata"].get("source_bundle_version", "public-source-manifest-v0.2"),
            "scenario_type": scenario["metadata"].get("scenario_type", "baseline"),
            "scenario_purpose": scenario["metadata"].get("scenario_purpose", "Demonstration scenario."),
        },
        "summary": summary,
        "time_series": ts,
        "gates": [g.to_dict() for g in gates],
        "passed": overall_passed(gates),
        "evidence": {
            "status_counts": summarize_statuses(scenario),
            "warnings": evidence_warnings,
            "errors": evidence_errors,
            "verified_or_reported_inputs": verified_facts,
            "assumptions_used": assumptions,
            "policy": "No assumption is promoted to verified fact. Restricted sources are not redistributed.",
        },
        "unknowns": {
            "unresolved_variables": reader.unresolved,
            "substitutions": reader.substitutions,
            "underdetermined": bool(reader.unresolved),
            "policy": "Material unknown values create failed unknown_input_discipline gates and underdetermined outputs; they are not silently treated as verified defaults.",
        },
        "registries": {
            "scalar_outputs": SCALAR_OUTPUTS,
            "vector_outputs": VECTOR_OUTPUTS,
            "matrix_outputs": MATRIX_OUTPUTS,
        },
        "matrices": {
            "gate_matrix": gate_matrix,
            "module_output_matrix": module_output_matrix,
            "partner_allocation_matrix": partner_allocation_matrix,
            "subsystem_state_matrix": subsystem_state_matrix,
        },
        "formal_modules": {
            "cleanroom": clean_state.to_dict(),
            "contamination": contamination_state.to_dict(),
            "packaging": packaging_state.to_dict(),
            "qualification": qualification_state.to_dict(),
            "bayesian_evidence_example": bayes_update(0.5, 0.7, 0.3).to_dict(),
            "bayesian_status_rule": posterior_to_status(0.999),
        },
        "interpretation": {
            "can_conclude": [
                "The scenario computes consequences conditional on its evidence-coded inputs.",
                "Gate failures identify modeled constraints or unresolved variables requiring decision attention.",
                "Stress-test assumptions remain stress tests, not verified Terafab facts."
            ],
            "cannot_conclude": [
                "The model does not verify proprietary Terafab operating data.",
                "The model does not claim Terafab endorsement, financing, permitting, construction, or adoption.",
                "The model does not convert assumptions, Bayesian confidence, or stress tests into verified facts."
            ],
            "highest_value_next_data": [
                "site-specific power capacity and tariff structure",
                "permitted water withdrawal and discharge capacity",
                "validated process/yield and packaging readiness data",
                "governance and contracting obligations"
            ],
        },
        "hashes": {
            "scenario_sha256": stable_hash(scenario),
        },
    }
    result_hash = stable_hash({k: v for k, v in result.items() if k != "hashes"})
    result["output_records"] = build_output_records(summary, scenario_id=result["metadata"]["scenario_id"], assumptions_used=assumption_paths, warning_flags=warning_flags, result_hash=result_hash)
    result["hashes"]["result_sha256"] = stable_hash(result)
    return result
