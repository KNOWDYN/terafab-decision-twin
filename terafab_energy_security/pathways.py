"""Predeclared 2026-2050 pathway and portfolio orchestration."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any, Iterable, Mapping

from .engine import run_case
from .evidence import FrozenEvidence
from .models import (
    EnergySecurityCase,
    ErcotInputs,
    FacilityInputs,
    ManufacturingInputs,
    NationalInputs,
    SupplyInputs,
    TargetInputs,
)


TARGET_SCALES = ("no_build", "research_fab", "initial_large_scale", "full_announced_target")
REALIZATION_PATHWAYS = ("accelerated", "reference", "delayed", "not_realized_by_2050")
SUPPLY_PORTFOLIOS = ("grid_dominant", "firm_onsite", "renewable_storage_grid", "firm_low_carbon_hybrid")
STRESS_CONDITIONS = (
    "normal",
    "summer_peak",
    "winter_extreme",
    "infrastructure_delay",
    "yield_underperformance",
    "cooling_or_water_constraint",
    "firm_supply_outage",
)


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_scenario_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        config = json.load(stream)
    validate_scenario_config(config)
    return config


def validate_scenario_config(config: Mapping[str, Any]) -> None:
    if tuple(config["target_scales"]) != TARGET_SCALES:
        raise ValueError("target-scale axis or order changed")
    if tuple(config["realization_pathways"]) != REALIZATION_PATHWAYS:
        raise ValueError("realization-pathway axis or order changed")
    if tuple(config["supply_portfolios"]) != SUPPLY_PORTFOLIOS:
        raise ValueError("supply-portfolio axis or order changed")
    if tuple(config["stress_conditions"]) != STRESS_CONDITIONS:
        raise ValueError("stress-condition axis or order changed")
    if config["start_year"] != 2026 or config["end_year"] != 2050:
        raise ValueError("study horizon must remain 2026-2050")
    semantic_branches = config["target_semantic_branches"]
    if semantic_branches["rated_device_output"]["numerical_status"] != "conditional_model_interpretation":
        raise ValueError("primary target-semantic branch changed")
    if semantic_branches["other_publicly_undefined_meaning"]["numerical_status"] != "indeterminate":
        raise ValueError("the mandatory alternative target-semantic branch must remain indeterminate")
    if config["target_scales"]["research_fab"]["fraction_of_public_target"] is not None:
        raise ValueError("research-fab scale must remain unknown")
    if config["target_scales"]["initial_large_scale"]["fraction_of_public_target"] is not None:
        raise ValueError("initial-large-scale output must remain unknown")
    for name, pathway in config["realization_pathways"].items():
        milestones = pathway["milestones"]
        years = [item[0] for item in milestones]
        fractions = [item[1] for item in milestones]
        if years != sorted(years) or len(years) != len(set(years)):
            raise ValueError(f"{name}: milestone years must be unique and ordered")
        if fractions != sorted(fractions) or not all(0 < value <= 1 for value in fractions):
            raise ValueError(f"{name}: milestone fractions must be monotonic in (0, 1]")
    renewable = config["supply_portfolios"]["renewable_storage_grid"]
    if renewable["solar_elcc_fraction_winter"] > 0.02:
        raise ValueError("winter solar ELCC exceeds frozen extracted bound")
    if renewable["storage_elcc_fraction"] > 0.74:
        raise ValueError("five-hour storage ELCC exceeds frozen extracted bound")
    if not config["rules"]["unknown_target_scales_receive_numeric_defaults"] is False:
        raise ValueError("unknown target scales may not receive numeric defaults")
    if config["rules"]["probabilistic_ercot_metrics_available"]:
        raise ValueError("Step 2 did not admit probabilistic ERCOT result series")


def build_scenario_matrix(config: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.append({
        "scenario_id": "no_build__counterfactual",
        "target_scale": "no_build",
        "realization_pathway": "not_realized_by_2050",
        "supply_portfolio": "grid_dominant",
        "stress_condition": "normal",
        "target_semantics": "not_applicable_zero_increment",
        "numerical_status": "counterfactual",
    })
    for target_scale in TARGET_SCALES[1:]:
        target_value = config["target_scales"][target_scale]["fraction_of_public_target"]
        for pathway, portfolio, stress in itertools.product(
            REALIZATION_PATHWAYS,
            SUPPLY_PORTFOLIOS,
            STRESS_CONDITIONS,
        ):
            rows.append({
                "scenario_id": f"{target_scale}__{pathway}__{portfolio}__{stress}",
                "target_scale": target_scale,
                "realization_pathway": pathway,
                "supply_portfolio": portfolio,
                "stress_condition": stress,
                "target_semantics": "rated_device_output",
                "numerical_status": "indeterminate_target_scale" if target_value is None else "computable_conditional_case",
            })
    return rows


def _pathway_fraction(config: Mapping[str, Any], pathway: str, year: int) -> float:
    fraction = 0.0
    for milestone_year, milestone_fraction in config["realization_pathways"][pathway]["milestones"]:
        if year >= milestone_year:
            fraction = float(milestone_fraction)
    return fraction


def _first_active_year(config: Mapping[str, Any], pathway: str) -> int:
    return int(config["realization_pathways"][pathway]["milestones"][0][0])


def _national_cases(evidence: FrozenEvidence, year: int) -> tuple[float, float]:
    snapshot = evidence.snapshot("aeo2026_national_electricity.json")
    cases = snapshot["cases"]
    baseline = {row[0]: row[1] for row in cases["counterfactual_baseline"]["series"]}
    high = {row[0]: row[1] for row in cases["high_electricity_demand"]["series"]}
    return float(baseline[year]), float(high[year])


def _ercot_cases(evidence: FrozenEvidence, year: int) -> tuple[ErcotInputs, ErcotInputs]:
    snapshot = evidence.snapshot("ercot_adequacy.json")
    cdr = snapshot["cdr_december_2025"]
    protocol = {row["year"]: row for row in cdr["protocol_prescribed"]}
    sb6 = {row["year"]: row["value"] for row in cdr["sb6_base_case_peak_load_hour_PRM_fraction"]}
    if year not in protocol:
        return ErcotInputs(year, None, None), ErcotInputs(year, None, None)
    peak = float(protocol[year]["peak_load_MW"])
    protocol_inputs = ErcotInputs(year, peak, float(protocol[year]["peak_load_hour_PRM_fraction"]))
    sb6_inputs = ErcotInputs(year, peak, float(sb6[year]))
    return protocol_inputs, sb6_inputs


def _central_inputs(
    config: Mapping[str, Any],
    stress_name: str,
) -> tuple[ManufacturingInputs, FacilityInputs]:
    manufacturing = config["central_manufacturing"]
    facility = config["central_facility"]
    stress = config["stress_conditions"][stress_name]
    mfg = ManufacturingInputs(
        module_rated_power_W=float(manufacturing["module_rated_power_W"]),
        die_area_mm2=float(manufacturing["die_area_mm2"]),
        wafer_diameter_mm=float(manufacturing["wafer_diameter_mm"]),
        effective_yield=float(manufacturing["effective_yield"]) * float(stress["yield_multiplier"]),
        logic_dies_per_module=float(manufacturing["logic_dies_per_module"]),
        capacity_wafers_per_month=manufacturing["capacity_wafers_per_month"],
    )
    fac = FacilityInputs(
        electricity_kWh_per_wafer=float(facility["electricity_kWh_per_wafer"]),
        load_factor=float(facility["load_factor"]),
        cooling_cop=float(facility["cooling_cop"]),
        total_water_m3_per_wafer=float(facility["total_water_m3_per_wafer"]),
        total_water_intensity_basis=str(facility["total_water_intensity_basis"]),
        upw_m3_per_wafer=float(facility["upw_m3_per_wafer"]),
        water_recycling_fraction=float(facility["water_recycling_fraction"]),
        coincident_peak_multiplier=float(stress["peak_multiplier"]),
        recycling_displacement_fraction=facility["recycling_displacement_fraction"],
        consumptive_fraction=facility["consumptive_fraction"],
        heat_rejection_capacity_MW=facility["heat_rejection_capacity_MW"],
        withdrawal_capacity_m3_per_day=facility["withdrawal_capacity_m3_per_day"],
        wastewater_capacity_m3_per_day=facility["wastewater_capacity_m3_per_day"],
    )
    return mfg, fac


def _probe_case(
    scenario_id: str,
    year: int,
    operation_year: int,
    target_fraction: float,
    config: Mapping[str, Any],
    manufacturing: ManufacturingInputs,
    facility: FacilityInputs,
    ercot: ErcotInputs,
    national_TWh: float,
    supply: SupplyInputs | None = None,
) -> EnergySecurityCase:
    return EnergySecurityCase(
        case_id=f"{scenario_id}__{year}",
        year=year,
        facility_operation_year=operation_year,
        target=TargetInputs(
            rated_output_W_per_year=float(config["public_target_W_rated_per_year"]),
            target_fraction=target_fraction,
            interpretation=str(config["target_interpretation"]),
            interpretation_admitted=True,
        ),
        manufacturing=manufacturing,
        facility=facility,
        supply=supply or SupplyInputs(1e12, operation_year),
        ercot=ercot,
        national=NationalInputs(national_TWh),
    )


def _portfolio_supply(
    config: Mapping[str, Any],
    portfolio_name: str,
    stress_name: str,
    first_active_year: int,
    facility_peak_MW: float,
    facility_energy_MWh: float,
    operation_year: int,
) -> SupplyInputs:
    portfolio = config["supply_portfolios"][portfolio_name]
    stress = config["stress_conditions"][stress_name]
    availability_multiplier = float(stress["supply_availability_multiplier"])
    delay = int(stress["infrastructure_delay_years"])
    grid_year = 2026 + 3 + delay
    asset_year = max(2026, int(portfolio["first_available_year"])) + int(portfolio["generic_lead_time_years"]) + int(portfolio["mandatory_adder_years"]) + delay
    huge_grid = 1e12

    if portfolio_name == "grid_dominant":
        return SupplyInputs(huge_grid, grid_year)

    if portfolio_name in {"firm_onsite", "firm_low_carbon_hybrid"}:
        nominal_availability = float(portfolio["availability_fraction"])
        nominal_fuel = float(portfolio["fuel_availability_fraction"])
        peak_share = float(portfolio["onsite_peak_share"])
        nameplate = facility_peak_MW * peak_share / (nominal_availability * nominal_fuel)
        return SupplyInputs(
            huge_grid,
            grid_year,
            firm_onsite_nameplate_MW=nameplate,
            firm_onsite_availability_fraction=nominal_availability * availability_multiplier,
            firm_fuel_availability_fraction=nominal_fuel,
            firm_onsite_commissioning_year=asset_year,
            onsite_annual_energy_MWh=facility_energy_MWh * float(portfolio["onsite_energy_share"]) * availability_multiplier,
        )

    solar_elcc = float(portfolio["solar_elcc_fraction_winter"] if stress_name == "winter_extreme" else portfolio["solar_elcc_fraction_normal"])
    if stress_name == "firm_supply_outage":
        storage_elcc = 0.0
    else:
        storage_elcc = float(portfolio["storage_elcc_fraction"])
    return SupplyInputs(
        huge_grid,
        grid_year,
        renewable_nameplate_MW=facility_peak_MW * float(portfolio["solar_nameplate_to_facility_peak_ratio"]),
        renewable_elcc_fraction=solar_elcc,
        renewable_commissioning_year=asset_year,
        storage_nameplate_MW=facility_peak_MW * float(portfolio["storage_nameplate_to_facility_peak_ratio"]),
        storage_elcc_fraction=storage_elcc,
        storage_commissioning_year=asset_year,
        onsite_annual_energy_MWh=facility_energy_MWh * float(portfolio["onsite_energy_share"]),
    )


def _zero_row(
    scenario: Mapping[str, Any],
    year: int,
    protocol: ErcotInputs,
    sb6: ErcotInputs,
    national_baseline_TWh: float,
    national_high_TWh: float,
    row_type: str,
) -> dict[str, Any]:
    return {
        **scenario,
        "year": year,
        "row_type": row_type,
        "target_fraction_of_public_claim": 0.0,
        "rated_output_W_per_year": 0.0,
        "wafer_starts_per_year": 0.0,
        "wafer_starts_per_month": 0.0,
        "annual_electricity_MWh": 0.0,
        "coincident_peak_load_MW": 0.0,
        "heat_rejection_peak_MW": 0.0,
        "external_water_withdrawal_m3": 0.0,
        "net_grid_coincident_peak_MW": 0.0,
        "required_gigafab_100k_equivalents": 0.0,
        "protocol_counterfactual_peak_MW": protocol.baseline_peak_load_MW,
        "protocol_counterfactual_PRM_fraction": protocol.baseline_reserve_margin_fraction,
        "protocol_with_project_PRM_fraction": protocol.baseline_reserve_margin_fraction,
        "sb6_counterfactual_PRM_fraction": sb6.baseline_reserve_margin_fraction,
        "sb6_with_project_PRM_fraction": sb6.baseline_reserve_margin_fraction,
        "national_baseline_TWh": national_baseline_TWh,
        "national_high_demand_TWh": national_high_TWh,
        "national_baseline_energy_share": 0.0,
        "national_high_demand_energy_share": 0.0,
        "classification": "not_applicable_counterfactual" if row_type == "counterfactual" else "not_applicable_preoperation",
        "binding_constraint": None,
        "regional_adequacy_status": "not_applicable_zero_increment",
        "reproducibility_hash": _stable_hash([scenario["scenario_id"], year, row_type, 0.0]),
    }


def _flatten_result(
    scenario: Mapping[str, Any],
    year: int,
    target_fraction: float,
    primary: Mapping[str, Any],
    secondary: Mapping[str, Any],
    national_baseline_TWh: float,
    national_high_TWh: float,
) -> dict[str, Any]:
    manufacturing = primary["manufacturing"]
    facility = primary["facility"]
    supply = primary["deployment_and_supply"]
    primary_ercot = primary["ercot"]
    secondary_ercot = secondary["ercot"]
    gate_statuses = {gate["gate_id"]: gate["status"] for gate in primary["gates"]}
    return {
        **scenario,
        "year": year,
        "row_type": "active_conditional_case",
        "target_fraction_of_public_claim": target_fraction,
        "rated_output_W_per_year": manufacturing["rated_output_W_per_year"],
        "wafer_starts_per_year": manufacturing["wafer_starts_per_year"],
        "wafer_starts_per_month": manufacturing["wafer_starts_per_month"],
        "required_gigafab_100k_equivalents": manufacturing["wafer_starts_per_month"] / 100000.0,
        "annual_electricity_MWh": facility["annual_electricity_MWh"],
        "coincident_peak_load_MW": facility["coincident_peak_load_MW"],
        "cooling_auxiliary_peak_MW": facility["cooling_auxiliary_peak_MW"],
        "heat_rejection_peak_MW": facility["heat_rejection_peak_MW"],
        "external_water_withdrawal_m3": facility["external_water_withdrawal_m3"],
        "water_consumption_m3": facility["water_consumption_m3"],
        "wastewater_m3": facility["wastewater_m3"],
        "onsite_accredited_capacity_MW": supply["onsite_accredited_capacity_MW"],
        "net_grid_coincident_peak_MW": supply["net_grid_coincident_peak_MW"],
        "grid_interconnection_margin_MW": supply["grid_interconnection_margin_MW"],
        "late_supporting_assets": supply["late_supporting_assets"],
        "protocol_counterfactual_peak_MW": primary_ercot["counterfactual_peak_load_MW"],
        "protocol_counterfactual_PRM_fraction": primary_ercot["counterfactual_reserve_margin_fraction"],
        "protocol_with_project_PRM_fraction": primary_ercot["with_project_reserve_margin_fraction"],
        "protocol_delta_PRM_fraction": primary_ercot["delta_reserve_margin_fraction"],
        "sb6_counterfactual_PRM_fraction": secondary_ercot["counterfactual_reserve_margin_fraction"],
        "sb6_with_project_PRM_fraction": secondary_ercot["with_project_reserve_margin_fraction"],
        "sb6_delta_PRM_fraction": secondary_ercot["delta_reserve_margin_fraction"],
        "national_baseline_TWh": national_baseline_TWh,
        "national_high_demand_TWh": national_high_TWh,
        "national_baseline_energy_share": primary["national"]["share_of_US_annual_electricity"],
        "national_high_demand_energy_share": secondary["national"]["share_of_US_annual_electricity"],
        "classification": primary["decision"]["classification"],
        "binding_constraint": primary["decision"]["binding_constraint"],
        "regional_adequacy_status": gate_statuses["regional_adequacy"],
        "gate_statuses": gate_statuses,
        "reproducibility_hash": primary["reproducibility_hash"],
    }


def run_scenario_matrix(
    config: Mapping[str, Any],
    evidence: FrozenEvidence,
    scenario_ids: Iterable[str] | None = None,
) -> dict[str, Any]:
    validate_scenario_config(config)
    matrix = build_scenario_matrix(config)
    selected = None if scenario_ids is None else set(scenario_ids)
    annual_rows: list[dict[str, Any]] = []
    gate_rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    unknown_scale_rows: list[dict[str, Any]] = []

    for scenario in matrix:
        if selected is not None and scenario["scenario_id"] not in selected:
            continue
        target_scale = scenario["target_scale"]
        base_target = config["target_scales"][target_scale]["fraction_of_public_target"]
        if base_target is None:
            row = {
                **scenario,
                "classification": "indeterminate",
                "reason": "Target scale has no defensible public numerical value.",
            }
            unknown_scale_rows.append(row)
            summaries.append(row)
            continue

        if target_scale == "no_build":
            for year in range(config["start_year"], config["end_year"] + 1):
                protocol, sb6 = _ercot_cases(evidence, year)
                national_baseline, national_high = _national_cases(evidence, year)
                annual_rows.append(_zero_row(scenario, year, protocol, sb6, national_baseline, national_high, "counterfactual"))
            summaries.append({**scenario, "classification": "counterfactual", "first_active_year": None, "first_joint_pass_year": None})
            continue

        pathway = scenario["realization_pathway"]
        first_active = _first_active_year(config, pathway)
        active_classifications: list[str] = []
        active_rows: list[dict[str, Any]] = []
        for year in range(config["start_year"], config["end_year"] + 1):
            protocol, sb6 = _ercot_cases(evidence, year)
            national_baseline, national_high = _national_cases(evidence, year)
            target_fraction = float(base_target) * _pathway_fraction(config, pathway, year)
            if target_fraction == 0.0:
                annual_rows.append(_zero_row(scenario, year, protocol, sb6, national_baseline, national_high, "preoperation"))
                continue

            manufacturing, facility = _central_inputs(config, scenario["stress_condition"])
            probe_case = _probe_case(
                scenario["scenario_id"], year, first_active, target_fraction, config,
                manufacturing, facility, protocol, national_baseline,
            )
            probe = run_case(probe_case)
            if scenario["stress_condition"] == "cooling_or_water_constraint":
                constraint_fraction = float(config["stress_conditions"]["cooling_or_water_constraint"]["capacity_fraction_of_requirement"])
                facility = replace(
                    facility,
                    heat_rejection_capacity_MW=probe["facility"]["heat_rejection_peak_MW"] * constraint_fraction,
                    withdrawal_capacity_m3_per_day=probe["facility"]["external_water_withdrawal_m3_per_day"] * constraint_fraction,
                    wastewater_capacity_m3_per_day=probe["facility"]["wastewater_m3_per_day"] * constraint_fraction,
                )
                probe_case = replace(probe_case, facility=facility)
                probe = run_case(probe_case)

            provisional_supply = _portfolio_supply(
                config,
                scenario["supply_portfolio"],
                scenario["stress_condition"],
                first_active,
                probe["facility"]["coincident_peak_load_MW"],
                probe["facility"]["annual_electricity_MWh"],
                first_active,
            )
            supply_probe_case = replace(probe_case, supply=provisional_supply)
            supply_probe = run_case(supply_probe_case)
            net_grid_peak = supply_probe["deployment_and_supply"]["net_grid_coincident_peak_MW"]
            portfolio = config["supply_portfolios"][scenario["supply_portfolio"]]
            final_supply = replace(
                provisional_supply,
                grid_interconnection_capacity_MW=net_grid_peak * (1.0 + float(portfolio["interconnection_headroom_fraction"])),
                grid_accredited_addition_MW=net_grid_peak * (1.0 + float(portfolio["grid_resource_reserve_fraction"])),
            )
            primary_case = replace(probe_case, supply=final_supply)
            primary = run_case(primary_case)
            secondary_case = replace(
                primary_case,
                ercot=sb6,
                national=NationalInputs(national_high),
            )
            secondary = run_case(secondary_case)
            row = _flatten_result(
                scenario, year, target_fraction, primary, secondary,
                national_baseline, national_high,
            )
            annual_rows.append(row)
            active_rows.append(row)
            active_classifications.append(row["classification"])
            for gate in primary["gates"]:
                gate_rows.append({
                    "scenario_id": scenario["scenario_id"],
                    "year": year,
                    "gate_id": gate["gate_id"],
                    "status": gate["status"],
                    "required": gate["required"],
                    "margin": gate["margin"],
                    "reason": gate["reason"],
                })

        if not active_rows:
            overall = "indeterminate"
        elif "indeterminate" in active_classifications:
            overall = "indeterminate"
        elif "conditionally_feasible" in active_classifications:
            overall = "conditionally_feasible"
        else:
            overall = "not_demonstrated"
        first_joint_pass = next((row["year"] for row in active_rows if row["classification"] == "conditionally_feasible"), None)
        summaries.append({
            **scenario,
            "classification": overall,
            "first_active_year": first_active,
            "first_joint_pass_year": first_joint_pass,
            "active_years": len(active_rows),
            "2050_wafer_starts_per_year": active_rows[-1]["wafer_starts_per_year"] if active_rows else None,
            "2050_annual_electricity_MWh": active_rows[-1]["annual_electricity_MWh"] if active_rows else None,
            "2050_peak_load_MW": active_rows[-1]["coincident_peak_load_MW"] if active_rows else None,
            "2050_water_withdrawal_m3": active_rows[-1]["external_water_withdrawal_m3"] if active_rows else None,
        })

    manifest = {
        "study_id": config["study_id"],
        "scenario_definition_hash": _stable_hash(config),
        "full_matrix_trajectory_count": len(matrix),
        "selected_trajectory_count": len(summaries),
        "annual_result_row_count": len(annual_rows),
        "gate_result_row_count": len(gate_rows),
        "unknown_target_scale_trajectory_count": len(unknown_scale_rows),
        "classification_counts": dict(Counter(item["classification"] for item in summaries)),
        "unresolved_target_semantic_branches": 1,
        "live_web_retrieval": False,
        "claim_level": "prospective_conditional_constraint_analysis",
    }
    return {
        "scenario_matrix": matrix,
        "annual_results": annual_rows,
        "gate_results": gate_rows,
        "trajectory_summary": summaries,
        "unknown_target_scales": unknown_scale_rows,
        "manifest": manifest,
    }
