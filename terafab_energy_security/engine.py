"""Five-stage deterministic production-to-energy constraint kernel."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict
from typing import Any, Mapping

from .equations import (
    facility_resources,
    gross_dies_per_wafer,
    require_finite,
    require_fraction,
    reserve_margin,
    translate_target,
)
from .gates import GateResult, GateStatus, binding_constraint, classify
from .models import EnergySecurityCase


MODEL_VERSION = "0.1.0"
RESIDUAL_LIMIT = 1e-8


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _validate_case(case: EnergySecurityCase) -> None:
    if not case.case_id.strip():
        raise ValueError("case_id must not be empty")
    if case.year != case.ercot.year:
        raise ValueError("case year must equal ERCOT baseline year")
    if case.year < case.facility_operation_year:
        raise ValueError("case year cannot precede the modeled facility operation year")

    require_finite("rated_output_W_per_year", case.target.rated_output_W_per_year, nonnegative=True)
    require_fraction("target_fraction", case.target.target_fraction)
    require_finite("module_rated_power_W", case.manufacturing.module_rated_power_W, positive=True)
    require_finite("die_area_mm2", case.manufacturing.die_area_mm2, positive=True)
    require_finite("wafer_diameter_mm", case.manufacturing.wafer_diameter_mm, positive=True)
    require_fraction("effective_yield", case.manufacturing.effective_yield)
    if case.manufacturing.effective_yield == 0:
        raise ValueError("effective_yield must be greater than zero")
    require_finite("logic_dies_per_module", case.manufacturing.logic_dies_per_module, positive=True)
    if case.manufacturing.capacity_wafers_per_month is not None:
        require_finite("capacity_wafers_per_month", case.manufacturing.capacity_wafers_per_month, nonnegative=True)

    require_finite("electricity_kWh_per_wafer", case.facility.electricity_kWh_per_wafer, nonnegative=True)
    require_fraction("load_factor", case.facility.load_factor)
    if case.facility.load_factor == 0:
        raise ValueError("load_factor must be greater than zero")
    require_finite("coincident_peak_multiplier", case.facility.coincident_peak_multiplier, positive=True)
    require_finite("cooling_cop", case.facility.cooling_cop, positive=True)
    require_finite("total_water_m3_per_wafer", case.facility.total_water_m3_per_wafer, nonnegative=True)
    if case.facility.total_water_intensity_basis not in {
        "gross_process_demand_before_reuse",
        "external_withdrawal_after_reuse",
    }:
        raise ValueError("invalid total_water_intensity_basis")
    require_finite("upw_m3_per_wafer", case.facility.upw_m3_per_wafer, nonnegative=True)
    require_fraction("water_recycling_fraction", case.facility.water_recycling_fraction)
    for name in (
        "recycling_displacement_fraction",
        "consumptive_fraction",
    ):
        value = getattr(case.facility, name)
        if value is not None:
            require_fraction(name, value)
    for name in (
        "heat_rejection_capacity_MW",
        "withdrawal_capacity_m3_per_day",
        "wastewater_capacity_m3_per_day",
    ):
        value = getattr(case.facility, name)
        if value is not None:
            require_finite(name, value, nonnegative=True)

    supply = case.supply
    for name in (
        "grid_accredited_addition_MW",
        "firm_onsite_nameplate_MW",
        "renewable_nameplate_MW",
        "storage_nameplate_MW",
        "onsite_annual_energy_MWh",
    ):
        require_finite(name, getattr(supply, name), nonnegative=True)
    if supply.grid_interconnection_capacity_MW is not None:
        require_finite("grid_interconnection_capacity_MW", supply.grid_interconnection_capacity_MW, nonnegative=True)
    for name in (
        "firm_onsite_availability_fraction",
        "firm_fuel_availability_fraction",
        "renewable_elcc_fraction",
        "storage_elcc_fraction",
    ):
        require_fraction(name, getattr(supply, name))

    ercot = case.ercot
    if ercot.baseline_peak_load_MW is not None:
        require_finite("baseline_peak_load_MW", ercot.baseline_peak_load_MW, positive=True)
    if ercot.baseline_reserve_margin_fraction is not None:
        require_finite("baseline_reserve_margin_fraction", ercot.baseline_reserve_margin_fraction)
    if (ercot.baseline_peak_load_MW is None) != (ercot.baseline_reserve_margin_fraction is None):
        raise ValueError("ERCOT baseline peak and reserve margin must either both be supplied or both be unknown")
    require_finite("annual_electricity_TWh", case.national.annual_electricity_TWh, positive=True)
    if case.national.peak_load_MW is not None:
        require_finite("national_peak_load_MW", case.national.peak_load_MW, positive=True)


def _commissioned(nameplate: float, commissioning_year: int | None, year: int) -> bool | None:
    if nameplate <= 0:
        return True
    if commissioning_year is None:
        return None
    return commissioning_year <= year


def _supply_stage(case: EnergySecurityCase, facility: Mapping[str, Any]) -> dict[str, Any]:
    supply = case.supply
    year = case.year
    operation_year = case.facility_operation_year

    firm_ready = _commissioned(supply.firm_onsite_nameplate_MW, supply.firm_onsite_commissioning_year, year)
    renewable_ready = _commissioned(supply.renewable_nameplate_MW, supply.renewable_commissioning_year, year)
    storage_ready = _commissioned(supply.storage_nameplate_MW, supply.storage_commissioning_year, year)
    interconnection_ready = None if supply.grid_interconnection_year is None else supply.grid_interconnection_year <= year

    firm_accredited = 0.0 if firm_ready is not True else (
        supply.firm_onsite_nameplate_MW
        * supply.firm_onsite_availability_fraction
        * supply.firm_fuel_availability_fraction
    )
    renewable_accredited = 0.0 if renewable_ready is not True else (
        supply.renewable_nameplate_MW * supply.renewable_elcc_fraction
    )
    storage_accredited = 0.0 if storage_ready is not True else (
        supply.storage_nameplate_MW * supply.storage_elcc_fraction
    )
    onsite_accredited = firm_accredited + renewable_accredited + storage_accredited
    net_grid_peak = max(0.0, facility["coincident_peak_load_MW"] - onsite_accredited)
    if supply.onsite_annual_energy_MWh > facility["annual_electricity_MWh"] + 1e-9:
        raise ValueError("onsite_annual_energy_MWh cannot exceed facility annual electricity")
    grid_energy = max(0.0, facility["annual_electricity_MWh"] - supply.onsite_annual_energy_MWh)

    interconnection_margin: float | None = None
    if supply.grid_interconnection_capacity_MW is not None and interconnection_ready is True:
        interconnection_margin = supply.grid_interconnection_capacity_MW - net_grid_peak

    schedule_requirements: list[tuple[str, int | None]] = [("grid_interconnection", supply.grid_interconnection_year)]
    if supply.firm_onsite_nameplate_MW > 0:
        schedule_requirements.append(("firm_onsite", supply.firm_onsite_commissioning_year))
    if supply.renewable_nameplate_MW > 0:
        schedule_requirements.append(("renewable", supply.renewable_commissioning_year))
    if supply.storage_nameplate_MW > 0:
        schedule_requirements.append(("storage", supply.storage_commissioning_year))
    missing_schedule = [name for name, commissioned_year in schedule_requirements if commissioned_year is None]
    late_assets = [
        name
        for name, commissioned_year in schedule_requirements
        if commissioned_year is not None and commissioned_year > operation_year
    ]

    return {
        "firm_onsite_accredited_MW": firm_accredited,
        "renewable_accredited_MW": renewable_accredited,
        "storage_accredited_MW": storage_accredited,
        "onsite_accredited_capacity_MW": onsite_accredited,
        "net_grid_coincident_peak_MW": net_grid_peak,
        "grid_annual_energy_MWh": grid_energy,
        "grid_interconnection_margin_MW": interconnection_margin,
        "missing_schedule_evidence": missing_schedule,
        "late_supporting_assets": late_assets,
        "all_support_commissioned_by_operation": False if late_assets else (None if missing_schedule else True),
        "commissioning_state": {
            "grid_interconnection": interconnection_ready,
            "firm_onsite": firm_ready,
            "renewable": renewable_ready,
            "storage": storage_ready,
        },
    }


def _ercot_stage(case: EnergySecurityCase, supply: Mapping[str, Any]) -> dict[str, Any]:
    inputs = case.ercot
    project_peak = supply["net_grid_coincident_peak_MW"]
    baseline_available = inputs.baseline_peak_load_MW is not None
    if baseline_available:
        counterfactual_peak = float(inputs.baseline_peak_load_MW)
        counterfactual_prm = float(inputs.baseline_reserve_margin_fraction)
        baseline_accredited = counterfactual_peak * (1.0 + counterfactual_prm)
        with_project_peak = counterfactual_peak + project_peak
        with_project_accredited = baseline_accredited + case.supply.grid_accredited_addition_MW
        with_project_prm = reserve_margin(with_project_accredited, with_project_peak)
        delta_prm = with_project_prm - counterfactual_prm
    else:
        counterfactual_peak = None
        counterfactual_prm = None
        baseline_accredited = None
        with_project_peak = None
        with_project_accredited = None
        with_project_prm = None
        delta_prm = None
    return {
        "counterfactual_peak_load_MW": counterfactual_peak,
        "counterfactual_accredited_capacity_MW": baseline_accredited,
        "counterfactual_reserve_margin_fraction": counterfactual_prm,
        "incremental_grid_coincident_peak_MW": project_peak,
        "with_project_peak_load_MW": with_project_peak,
        "with_project_accredited_capacity_MW": with_project_accredited,
        "with_project_reserve_margin_fraction": with_project_prm,
        "delta_reserve_margin_fraction": delta_prm,
        "official_baseline_available": baseline_available,
        "probabilistic_metrics": {
            "lole_events_per_year": inputs.lole_events_per_year,
            "maximum_event_duration_hours": inputs.maximum_event_duration_hours,
            "highest_hourly_average_load_shed_MW": inputs.highest_hourly_average_load_shed_MW,
        },
        "screening_only": True,
        "reserve_margin_is_regulatory_pass": False,
    }


def _gate_results(
    case: EnergySecurityCase,
    manufacturing: Mapping[str, Any],
    facility: Mapping[str, Any],
    supply: Mapping[str, Any],
) -> list[GateResult]:
    gates: list[GateResult] = []
    gates.append(GateResult(
        "target_semantics",
        GateStatus.PASS if case.target.interpretation_admitted else GateStatus.INDETERMINATE,
        True,
        None,
        "The modeled interpretation is traceable and admitted for conditional analysis."
        if case.target.interpretation_admitted
        else "The target interpretation is not admitted; the affected conclusion is indeterminate.",
    ))

    capacity = case.manufacturing.capacity_wafers_per_month
    required = manufacturing["wafer_starts_per_month"]
    if capacity is None:
        throughput_gate = GateResult("manufacturing_throughput", GateStatus.INDETERMINATE, True, None, "Public or scenario manufacturing capacity is not specified.")
    else:
        margin = capacity - required
        throughput_gate = GateResult("manufacturing_throughput", GateStatus.PASS if margin >= 0 else GateStatus.FAIL, True, margin, "Available wafer capacity must cover required starts.")
    gates.append(throughput_gate)

    physical_residual = max(
        manufacturing["rated_output_identity_residual"],
        facility["energy_balance_relative_residual"],
    )
    gates.append(GateResult(
        "facility_energy",
        GateStatus.PASS if physical_residual <= RESIDUAL_LIMIT else GateStatus.FAIL,
        True,
        RESIDUAL_LIMIT - physical_residual,
        "Target and facility electricity identities must close within the frozen residual tolerance.",
    ))

    heat_capacity = case.facility.heat_rejection_capacity_MW
    heat_required = facility["heat_rejection_peak_MW"]
    if heat_capacity is None:
        thermal_gate = GateResult("thermal_capacity", GateStatus.INDETERMINATE, True, None, "Heat-rejection capacity is not specified.")
    else:
        margin = heat_capacity - heat_required
        thermal_gate = GateResult("thermal_capacity", GateStatus.PASS if margin >= 0 else GateStatus.FAIL, True, margin, "Heat-rejection capacity must cover coincident first-law heat load.")
    gates.append(thermal_gate)

    withdrawal = facility["external_water_withdrawal_m3_per_day"]
    wastewater = facility["wastewater_m3_per_day"]
    if not facility["upw_not_greater_than_gross_water"]:
        water_gate = GateResult("water_capacity", GateStatus.FAIL, True, case.facility.total_water_m3_per_wafer - case.facility.upw_m3_per_wafer, "UPW demand cannot exceed total gross water demand.")
    elif withdrawal is None or wastewater is None:
        water_gate = GateResult("water_capacity", GateStatus.INDETERMINATE, True, None, "Recycling displacement or consumptive-water evidence is missing.")
    elif case.facility.withdrawal_capacity_m3_per_day is None or case.facility.wastewater_capacity_m3_per_day is None:
        water_gate = GateResult("water_capacity", GateStatus.INDETERMINATE, True, None, "Water withdrawal or wastewater capacity is not specified.")
    else:
        withdrawal_margin = case.facility.withdrawal_capacity_m3_per_day - withdrawal
        discharge_margin = case.facility.wastewater_capacity_m3_per_day - wastewater
        margin = min(withdrawal_margin, discharge_margin)
        water_gate = GateResult("water_capacity", GateStatus.PASS if margin >= 0 else GateStatus.FAIL, True, margin, "Withdrawal and discharge capacities must cover steady annual demand.")
    gates.append(water_gate)

    schedule_state = supply["all_support_commissioned_by_operation"]
    schedule_status = GateStatus.INDETERMINATE if schedule_state is None else (GateStatus.PASS if schedule_state else GateStatus.FAIL)
    gates.append(GateResult(
        "schedule_precedence",
        schedule_status,
        True,
        None,
        "Every required supporting asset must be commissioned no later than facility operation.",
    ))

    interconnection_margin = supply["grid_interconnection_margin_MW"]
    if schedule_state is False:
        supply_gate = GateResult("supply_deliverability", GateStatus.FAIL, True, None, "At least one required supporting asset is commissioned after facility operation.", {"late_assets": supply["late_supporting_assets"]})
    elif interconnection_margin is None or schedule_state is None:
        supply_gate = GateResult("supply_deliverability", GateStatus.INDETERMINATE, True, None, "Interconnection capacity, commissioning, or deliverability evidence is missing.")
    else:
        supply_margin = interconnection_margin
        supply_gate = GateResult("supply_deliverability", GateStatus.PASS if supply_margin >= 0 else GateStatus.FAIL, True, supply_margin, "Accredited onsite supply and the grid interconnection must cover coincident demand on schedule.")
    gates.append(supply_gate)

    ercot = case.ercot
    probabilistic_values = (
        ercot.lole_events_per_year,
        ercot.maximum_event_duration_hours,
        ercot.highest_hourly_average_load_shed_MW,
        ercot.magnitude_limit_MW,
    )
    if any(value is None for value in probabilistic_values):
        regional_gate = GateResult("regional_adequacy", GateStatus.INDETERMINATE, True, None, "Reserve margin is screening only; complete PUCT probabilistic metrics are unavailable.")
    else:
        lole_margin = ercot.lole_limit_events_per_year - float(ercot.lole_events_per_year)
        duration_margin = ercot.duration_limit_hours - float(ercot.maximum_event_duration_hours)
        magnitude_margin = float(ercot.magnitude_limit_MW) - float(ercot.highest_hourly_average_load_shed_MW)
        passed = lole_margin >= 0 and duration_margin > 0 and magnitude_margin > 0
        regional_gate = GateResult(
            "regional_adequacy",
            GateStatus.PASS if passed else GateStatus.FAIL,
            True,
            None,
            "All PUCT frequency, duration, and magnitude conditions must pass; reserve margin alone is insufficient.",
            {
                "lole_margin_events_per_year": lole_margin,
                "duration_margin_hours": duration_margin,
                "magnitude_margin_MW": magnitude_margin,
            },
        )
    gates.append(regional_gate)

    gates.append(GateResult(
        "national_context",
        GateStatus.PASS,
        False,
        None,
        "National annual energy and peak shares are contextual, not an adequacy verdict.",
    ))

    upstream_indeterminate = any(gate.required and gate.status is GateStatus.INDETERMINATE for gate in gates)
    if case.evidence_sufficient_for_case is True:
        evidence_status = GateStatus.PASS
        evidence_reason = "Case evidence was explicitly declared sufficient and all claim boundaries remain conditional."
    elif case.evidence_sufficient_for_case is False:
        evidence_status = GateStatus.FAIL
        evidence_reason = "Case evidence was explicitly declared insufficient."
    elif upstream_indeterminate:
        evidence_status = GateStatus.INDETERMINATE
        evidence_reason = "At least one indispensable gate lacks bounded evidence."
    else:
        evidence_status = GateStatus.PASS
        evidence_reason = "No indispensable gate input remains unbounded in this case."
    gates.append(GateResult("evidence_sufficiency", evidence_status, True, None, evidence_reason))
    return gates


def run_case(case: EnergySecurityCase | Mapping[str, Any]) -> dict[str, Any]:
    """Run one deterministic milestone-year case through all five stages."""
    if not isinstance(case, EnergySecurityCase):
        case = EnergySecurityCase.from_dict(case)
    _validate_case(case)

    dies_per_wafer = gross_dies_per_wafer(
        case.manufacturing.wafer_diameter_mm,
        case.manufacturing.die_area_mm2,
    )
    manufacturing = translate_target(
        case.target.rated_output_W_per_year,
        case.target.target_fraction,
        case.manufacturing.module_rated_power_W,
        case.manufacturing.logic_dies_per_module,
        dies_per_wafer,
        case.manufacturing.effective_yield,
    )
    manufacturing["capacity_wafers_per_month"] = case.manufacturing.capacity_wafers_per_month

    facility = facility_resources(
        manufacturing["wafer_starts_per_year"],
        case.facility.electricity_kWh_per_wafer,
        case.facility.load_factor,
        case.facility.coincident_peak_multiplier,
        case.facility.cooling_cop,
        case.facility.total_water_m3_per_wafer,
        case.facility.total_water_intensity_basis,
        case.facility.upw_m3_per_wafer,
        case.facility.water_recycling_fraction,
        case.facility.recycling_displacement_fraction,
        case.facility.consumptive_fraction,
        case.facility.operating_days_per_year,
    )
    supply = _supply_stage(case, facility)
    ercot = _ercot_stage(case, supply)
    national = {
        "share_of_US_annual_electricity": facility["annual_electricity_MWh"] / (case.national.annual_electricity_TWh * 1_000_000.0),
        "share_of_US_peak_load": None if case.national.peak_load_MW is None else facility["coincident_peak_load_MW"] / case.national.peak_load_MW,
        "annual_electricity_counterfactual_TWh": case.national.annual_electricity_TWh,
        "peak_load_counterfactual_MW": case.national.peak_load_MW,
        "context_only": True,
    }

    gates = _gate_results(case, manufacturing, facility, supply)
    result: dict[str, Any] = {
        "model": "terafab_energy_security",
        "model_version": MODEL_VERSION,
        "case_id": case.case_id,
        "year": case.year,
        "claim_level": "prospective_conditional_constraint_analysis",
        "target_interpreter": {
            "public_target_input_W_per_year": case.target.rated_output_W_per_year,
            "target_fraction": case.target.target_fraction,
            "interpretation": case.target.interpretation,
            "interpretation_admitted": case.target.interpretation_admitted,
            "facility_load_equivalence_prohibited": True,
        },
        "manufacturing": manufacturing,
        "facility": facility,
        "deployment_and_supply": supply,
        "ercot": ercot,
        "national": national,
        "gates": [gate.to_dict() for gate in gates],
        "decision": {
            "classification": classify(gates),
            "binding_constraint": binding_constraint(gates),
            "official_project_feasibility_claim": False,
        },
        "nonclaims": [
            "No verified Terafab operating data",
            "No official feasibility determination or prediction",
            "No affiliation or endorsement",
            "No engineering, investment, permitting, procurement, or regulatory advice",
        ],
        "input": asdict(case),
    }
    result["reproducibility_hash"] = _stable_hash(result)
    if not math.isfinite(facility["annual_electricity_MWh"]):
        raise ArithmeticError("non-finite facility result")
    return result
