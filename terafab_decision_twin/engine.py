from __future__ import annotations

import hashlib
import json
from math import isfinite
from typing import Any, Dict, List

from .evidence import audit_evidence, summarize_statuses, v
from .schema import assert_valid_scenario
from .time_axis import build_time_axis
from .models.first_law import heat_rejection_required_MW
from .models.entropy import heat_transfer_entropy_generation_MW_per_K
from .models.exergy import heat_exergy_MW, exergy_destroyed_MW, exergy_efficiency
from .models.power import energy_consumption_MWh, firm_capacity_margin_MW, emissions_tCO2, electricity_cost_USD
from .models.cooling import cooling_auxiliary_power_MW, heat_rejection_margin_MW, cooling_tower_evaporation_m3_per_h
from .models.water import withdrawal_m3, consumptive_use_m3, wastewater_m3, permit_margin_m3_per_day, upw_demand_m3
from .models.manufacturing import learned_yield, effective_yield, good_die_output, compute_output_proxy
from .models.readiness import readiness_index, readiness_bottleneck
from .models.economics import annualized_capex_USD, water_cost_USD, emissions_cost_USD, cost_per_good_die_USD, cost_per_compute_watt_USD
from .models.governance import governance_risk_index, governance_readiness
from .models.policy import public_benefit_index, public_burden_index, legitimacy_margin
from .models.real_options import phase_gate_value, recommend_phase_action
from .models.gates import evaluate_gates, overall_passed
from .units import DAYS_PER_YEAR, safe_div


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _float(section: Dict[str, Any], key: str, default: float = 0.0) -> float:
    value = v(section, key, default)
    if value in (None, "unknown", ""):
        return float(default)
    return float(value)


def _int(section: Dict[str, Any], key: str, default: int = 0) -> int:
    return int(round(_float(section, key, default)))


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

    strict = bool(scenario.get("control", {}).get("strict_evidence", False))
    evidence_issues = audit_evidence(scenario, strict=strict)
    evidence_errors = [f"{i.path}: {i.message}" for i in evidence_issues if i.severity == "error"]
    evidence_warnings = [f"{i.path}: {i.message}" for i in evidence_issues if i.severity == "warning"]

    load_MW = _float(energy, "site_electric_load_MW")
    load_factor = _float(energy, "load_factor", 1.0)
    firm_capacity_MW = _float(energy, "firm_capacity_MW")
    reserve_margin_fraction = _float(energy, "reserve_margin_fraction", 0.15)
    carbon_intensity = _float(energy, "grid_carbon_intensity_kg_per_MWh", 0.0)

    heat_fraction = _float(cooling, "heat_rejection_fraction", 0.98)
    waste_heat_MW = _float(cooling, "waste_heat_MW", 0.0)
    heat_capacity_MW = _float(cooling, "heat_rejection_capacity_MW")
    cop = _float(cooling, "cop", 5.0)
    hot_K = _float(cooling, "hot_reservoir_K", 315.0)
    cold_K = _float(cooling, "cold_reservoir_K", 298.15)
    ambient_K = _float(cooling, "ambient_temperature_K", 298.15)

    withdrawal_intensity = _float(water, "withdrawal_m3_per_MWh", 0.0)
    consumptive_fraction = _float(water, "consumptive_fraction", 0.0)
    wastewater_fraction = _float(water, "wastewater_fraction", max(0.0, 1.0 - consumptive_fraction))
    permit_withdrawal = _float(water, "permit_withdrawal_m3_per_day", 0.0)
    permit_discharge = _float(water, "permit_discharge_m3_per_day", permit_withdrawal)
    upw_per_wafer = _float(water, "upw_m3_per_wafer", 0.0)

    wafer_starts_per_month = _float(mfg, "wafer_starts_per_month", 0.0)
    die_per_wafer = _float(mfg, "die_per_wafer", 0.0)
    base_yield = _float(mfg, "baseline_yield", 0.0)
    learning_rate = _float(mfg, "learning_rate_per_year", 0.0)
    contamination_loss = _float(mfg, "contamination_loss_fraction", 0.0)
    qualification_readiness = _float(mfg, "qualification_readiness", 1.0)
    contamination_readiness = _float(mfg, "contamination_readiness", 1.0)
    packaging_readiness = _float(mfg, "packaging_readiness", 1.0)
    compute_watts_per_good_die = _float(mfg, "compute_watts_per_good_die", 0.0)

    electricity_price = _float(econ, "electricity_price_USD_per_MWh", 0.0)
    water_price = _float(econ, "water_price_USD_per_m3", 0.0)
    capex = _float(econ, "capex_USD", 0.0)
    fixed_opex = _float(econ, "annual_fixed_opex_USD", 0.0)
    discount_rate = _float(econ, "discount_rate", 0.08)
    asset_life = _int(econ, "asset_life_years", 20)
    incentive = _float(econ, "incentive_public_USD", 0.0)

    jobs = _float(pol, "jobs_created", 0.0)
    domestic_supply = _float(pol, "domestic_supply_security_index", 0.0)
    water_stress = _float(pol, "local_water_stress_index", 0.0)
    public_legitimacy = _float(pol, "public_legitimacy_index", 0.0)
    regulatory_readiness = _float(pol, "regulatory_readiness_index", 0.0)
    emissions_price = _float(pol, "emissions_price_USD_per_tCO2", 0.0)

    partner_count = _int(gov, "partner_count", 1)
    gov_complexity = _float(gov, "governance_complexity_index", 0.0)
    decision_latency = _float(gov, "decision_latency_months", 0.0)

    annual_capex = annualized_capex_USD(capex, discount_rate, asset_life)

    ts: List[Dict[str, Any]] = []
    for step in axis:
        years_since_start = step.year - int(scenario["time"].get("start_year", 2026)) + (step.period - 1) * step.fraction_of_year
        energy_MWh = energy_consumption_MWh(load_MW, step.hours, load_factor)
        heat_required_MW = heat_rejection_required_MW(load_MW, heat_fraction, waste_heat_MW)
        heat_margin_MW = heat_rejection_margin_MW(heat_capacity_MW, heat_required_MW)
        cooling_power_MW = cooling_auxiliary_power_MW(heat_required_MW, cop)
        cooling_energy_MWh = cooling_power_MW * step.hours * load_factor
        entropy_gen = heat_transfer_entropy_generation_MW_per_K(heat_required_MW, hot_K, cold_K)
        destroyed_MW = exergy_destroyed_MW(ambient_K, entropy_gen)
        heat_exergy = heat_exergy_MW(heat_required_MW, hot_K, ambient_K)
        ex_eff = exergy_efficiency(max(0.0, heat_exergy - destroyed_MW), max(heat_exergy, 1e-12))
        emissions = emissions_tCO2(energy_MWh, carbon_intensity)

        withdraw = withdrawal_m3(energy_MWh, withdrawal_intensity)
        upw = upw_demand_m3(wafer_starts_per_month * 12.0 * step.fraction_of_year, upw_per_wafer)
        total_withdraw = withdraw + upw
        consume = consumptive_use_m3(total_withdraw, consumptive_fraction)
        waste = wastewater_m3(total_withdraw, wastewater_fraction)
        days = DAYS_PER_YEAR * step.fraction_of_year
        withdrawal_margin = permit_margin_m3_per_day(total_withdraw, permit_withdrawal, days)
        discharge_margin = permit_margin_m3_per_day(waste, permit_discharge, days)

        wafer_starts = wafer_starts_per_month * 12.0 * step.fraction_of_year
        learned = learned_yield(base_yield, learning_rate, years_since_start)
        readiness = readiness_index(qualification_readiness, contamination_readiness, packaging_readiness, regulatory_readiness)
        eff_yield = effective_yield(learned, contamination_loss, qualification_readiness * contamination_readiness, packaging_readiness)
        good_die = good_die_output(wafer_starts, die_per_wafer, eff_yield)
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

        ts.append({
            "label": step.label,
            "year": step.year,
            "hours": step.hours,
            "phase": phase.get("phase", "unknown"),
            "site_electric_load_MW": load_MW,
            "energy_MWh": energy_MWh,
            "firm_capacity_margin_MW": firm_capacity_margin_MW(firm_capacity_MW, load_MW, reserve_margin_fraction),
            "heat_rejection_required_MW": heat_required_MW,
            "heat_rejection_capacity_MW": heat_capacity_MW,
            "heat_rejection_margin_MW": heat_margin_MW,
            "cooling_auxiliary_power_MW": cooling_power_MW,
            "cooling_auxiliary_energy_MWh": cooling_energy_MWh,
            "entropy_generation_MW_per_K": entropy_gen,
            "exergy_destroyed_MW": destroyed_MW,
            "heat_exergy_MW": heat_exergy,
            "exergy_efficiency": ex_eff,
            "water_withdrawal_m3": total_withdraw,
            "water_consumptive_use_m3": consume,
            "wastewater_m3": waste,
            "water_withdrawal_margin_m3_per_day": withdrawal_margin,
            "wastewater_discharge_margin_m3_per_day": discharge_margin,
            "effective_yield": eff_yield,
            "readiness_index": readiness,
            "readiness_bottleneck": readiness_bottleneck({"qualification": qualification_readiness, "contamination": contamination_readiness, "packaging": packaging_readiness, "regulatory": regulatory_readiness}),
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
        })

    def total(key: str) -> float:
        return sum(float(row.get(key, 0.0)) for row in ts)
    def avg(key: str) -> float:
        return safe_div(total(key), len(ts), 0.0)
    def minv(key: str) -> float:
        return min(float(row.get(key, 0.0)) for row in ts) if ts else 0.0
    def maxv(key: str) -> float:
        return max(float(row.get(key, 0.0)) for row in ts) if ts else 0.0

    total_year_fraction = sum(step.fraction_of_year for step in axis)
    total_cost = annual_capex * total_year_fraction + total("opex_USD")
    good_die_total = total("good_die")
    compute_total = total("compute_output_proxy_W")
    cpg = cost_per_good_die_USD(total_cost, good_die_total)
    cpw = cost_per_compute_watt_USD(total_cost, compute_total)

    summary = {
        "scenario_id": scenario["metadata"].get("scenario_id"),
        "time_steps": len(ts),
        "energy_MWh": total("energy_MWh"),
        "average_site_load_MW": load_MW,
        "peak_site_load_MW": load_MW,
        "minimum_firm_capacity_margin_MW": minv("firm_capacity_margin_MW"),
        "heat_rejection_required_MW": maxv("heat_rejection_required_MW"),
        "minimum_heat_rejection_margin_MW": minv("heat_rejection_margin_MW"),
        "cooling_auxiliary_energy_MWh": total("cooling_auxiliary_energy_MWh"),
        "entropy_generation_MW_per_K": avg("entropy_generation_MW_per_K"),
        "exergy_destroyed_MW": avg("exergy_destroyed_MW"),
        "average_exergy_efficiency": avg("exergy_efficiency"),
        "water_withdrawal_m3": total("water_withdrawal_m3"),
        "water_consumptive_use_m3": total("water_consumptive_use_m3"),
        "wastewater_m3": total("wastewater_m3"),
        "minimum_water_withdrawal_margin_m3_per_day": minv("water_withdrawal_margin_m3_per_day"),
        "minimum_wastewater_discharge_margin_m3_per_day": minv("wastewater_discharge_margin_m3_per_day"),
        "good_die": good_die_total,
        "compute_output_proxy_W": compute_total,
        "average_effective_yield": avg("effective_yield"),
        "average_readiness_index": avg("readiness_index"),
        "annualized_capex_USD": annual_capex,
        "total_opex_USD": total("opex_USD"),
        "total_cost_USD": total_cost,
        "cost_per_good_die_USD": cpg,
        "cost_per_compute_watt_USD": cpw,
        "emissions_tCO2": total("emissions_tCO2"),
        "public_benefit_index": avg("public_benefit_index"),
        "public_burden_index": avg("public_burden_index"),
        "legitimacy_margin": avg("legitimacy_margin"),
        "maximum_governance_risk_index": maxv("governance_risk_index"),
        "recommended_phase_action": ts[-1]["phase_action"] if ts else "none",
    }

    gates = evaluate_gates(summary, evidence_errors=evidence_errors)
    result = {
        "metadata": {
            "package": "terafab-decision-twin",
            "version": "0.1.0",
            "scenario_id": scenario["metadata"].get("scenario_id"),
            "title": scenario["metadata"].get("title"),
        },
        "summary": summary,
        "time_series": ts,
        "gates": [g.to_dict() for g in gates],
        "passed": overall_passed(gates),
        "evidence": {
            "status_counts": summarize_statuses(scenario),
            "warnings": evidence_warnings,
            "errors": evidence_errors,
            "policy": "No assumption is promoted to verified fact. Restricted sources are not redistributed.",
        },
        "hashes": {
            "scenario_sha256": stable_hash(scenario),
        },
    }
    # Encode infinities safely for JSON consumers.
    for key, val in list(summary.items()):
        if isinstance(val, float) and not isfinite(val):
            summary[key] = None
    result["hashes"]["result_sha256"] = stable_hash(result)
    return result
