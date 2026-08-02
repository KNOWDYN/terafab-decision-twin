"""Dimensionally explicit governing equations for the study overlay."""

from __future__ import annotations

import math
from typing import Any


HOURS_PER_YEAR = 8766.0


def require_finite(name: str, value: float, *, positive: bool = False, nonnegative: bool = False) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{name} must be finite")
    if positive and number <= 0:
        raise ValueError(f"{name} must be positive")
    if nonnegative and number < 0:
        raise ValueError(f"{name} must be non-negative")
    return number


def require_fraction(name: str, value: float) -> float:
    number = require_finite(name, value)
    if not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be within [0, 1]")
    return number


def relative_residual(calculated: float, reference: float) -> float:
    scale = max(abs(float(reference)), 1e-30)
    return abs(float(calculated) - float(reference)) / scale


def gross_dies_per_wafer(wafer_diameter_mm: float, die_area_mm2: float) -> float:
    """Continuous dies-per-wafer approximation including circular edge loss.

    DPW = pi*d^2/(4*A) - pi*d/sqrt(2*A). Scribe-lane and defect effects are
    not hidden here; they belong in die area and effective yield scenarios.
    """
    diameter = require_finite("wafer_diameter_mm", wafer_diameter_mm, positive=True)
    area = require_finite("die_area_mm2", die_area_mm2, positive=True)
    result = math.pi * diameter * diameter / (4.0 * area) - math.pi * diameter / math.sqrt(2.0 * area)
    if result <= 0:
        raise ValueError("die area is too large for a positive gross dies-per-wafer estimate")
    return result


def translate_target(
    rated_output_W_per_year: float,
    target_fraction: float,
    module_rated_power_W: float,
    logic_dies_per_module: float,
    dies_per_wafer: float,
    effective_yield: float,
) -> dict[str, float]:
    target = require_finite("rated_output_W_per_year", rated_output_W_per_year, nonnegative=True)
    fraction = require_fraction("target_fraction", target_fraction)
    power = require_finite("module_rated_power_W", module_rated_power_W, positive=True)
    dies_per_module = require_finite("logic_dies_per_module", logic_dies_per_module, positive=True)
    gross_dpw = require_finite("dies_per_wafer", dies_per_wafer, positive=True)
    yield_fraction = require_fraction("effective_yield", effective_yield)
    if yield_fraction == 0:
        raise ValueError("effective_yield must be greater than zero")

    admitted_target = target * fraction
    modules = admitted_target / power
    good_dies = modules * dies_per_module
    wafers = good_dies / (gross_dpw * yield_fraction)
    reconstructed = wafers * gross_dpw * yield_fraction / dies_per_module * power
    return {
        "rated_output_W_per_year": admitted_target,
        "modules_per_year": modules,
        "good_logic_dies_per_year": good_dies,
        "gross_dies_per_wafer": gross_dpw,
        "wafer_starts_per_year": wafers,
        "wafer_starts_per_month": wafers / 12.0,
        "packaging_throughput_modules_per_year": modules,
        "rated_output_identity_residual": relative_residual(reconstructed, admitted_target),
    }


def facility_resources(
    wafer_starts_per_year: float,
    electricity_kWh_per_wafer: float,
    load_factor: float,
    coincident_peak_multiplier: float,
    cooling_cop: float,
    total_water_m3_per_wafer: float,
    total_water_intensity_basis: str,
    upw_m3_per_wafer: float,
    water_recycling_fraction: float,
    recycling_displacement_fraction: float | None,
    consumptive_fraction: float | None,
    operating_days_per_year: float,
) -> dict[str, Any]:
    wafers = require_finite("wafer_starts_per_year", wafer_starts_per_year, nonnegative=True)
    electricity_intensity = require_finite("electricity_kWh_per_wafer", electricity_kWh_per_wafer, nonnegative=True)
    lf = require_fraction("load_factor", load_factor)
    if lf == 0:
        raise ValueError("load_factor must be greater than zero")
    peak_multiplier = require_finite("coincident_peak_multiplier", coincident_peak_multiplier, positive=True)
    cop = require_finite("cooling_cop", cooling_cop, positive=True)
    water_intensity = require_finite("total_water_m3_per_wafer", total_water_m3_per_wafer, nonnegative=True)
    allowed_water_bases = {
        "gross_process_demand_before_reuse",
        "external_withdrawal_after_reuse",
    }
    if total_water_intensity_basis not in allowed_water_bases:
        raise ValueError(
            "total_water_intensity_basis must be gross_process_demand_before_reuse "
            "or external_withdrawal_after_reuse"
        )
    upw_intensity = require_finite("upw_m3_per_wafer", upw_m3_per_wafer, nonnegative=True)
    recycle = require_fraction("water_recycling_fraction", water_recycling_fraction)
    days = require_finite("operating_days_per_year", operating_days_per_year, positive=True)

    total_electricity_MWh = wafers * electricity_intensity / 1000.0
    average_load_MW = total_electricity_MWh / HOURS_PER_YEAR
    peak_load_MW = average_load_MW / lf * peak_multiplier

    # The admitted intensity is total facility electricity. A fixed-point split
    # prevents cooling from being added a second time: E=B+B/COP.
    core_electricity_MWh = total_electricity_MWh * cop / (cop + 1.0)
    cooling_electricity_MWh = total_electricity_MWh / (cop + 1.0)
    cooling_auxiliary_peak_MW = peak_load_MW / (cop + 1.0)
    thermal_process_peak_MW = peak_load_MW * cop / (cop + 1.0)
    heat_rejection_peak_MW = thermal_process_peak_MW + cooling_auxiliary_peak_MW
    energy_balance_residual = relative_residual(
        core_electricity_MWh + cooling_electricity_MWh,
        total_electricity_MWh,
    )
    heat_balance_residual = relative_residual(heat_rejection_peak_MW, peak_load_MW)

    gross_water_demand_m3 = wafers * water_intensity
    upw_demand_m3 = wafers * upw_intensity
    internal_recycled_flow_m3 = gross_water_demand_m3 * recycle

    external_withdrawal_m3: float | None = (
        gross_water_demand_m3
        if total_water_intensity_basis == "external_withdrawal_after_reuse"
        else None
    )
    water_consumption_m3: float | None = None
    wastewater_m3: float | None = None
    water_balance_residual: float | None = None
    effective_reuse_m3: float | None = None
    if recycling_displacement_fraction is not None:
        displacement = require_fraction("recycling_displacement_fraction", recycling_displacement_fraction)
        effective_reuse_m3 = internal_recycled_flow_m3 * displacement
        if total_water_intensity_basis == "gross_process_demand_before_reuse":
            external_withdrawal_m3 = max(0.0, gross_water_demand_m3 - effective_reuse_m3)
    if external_withdrawal_m3 is not None and consumptive_fraction is not None:
        consumptive = require_fraction("consumptive_fraction", consumptive_fraction)
        water_consumption_m3 = external_withdrawal_m3 * consumptive
        wastewater_m3 = external_withdrawal_m3 - water_consumption_m3
        water_balance_residual = relative_residual(
            water_consumption_m3 + wastewater_m3,
            external_withdrawal_m3,
        )

    return {
        "annual_electricity_MWh": total_electricity_MWh,
        "average_electric_load_MW": average_load_MW,
        "coincident_peak_load_MW": peak_load_MW,
        "coincident_peak_multiplier": peak_multiplier,
        "component_electricity_MWh": {
            "unallocated_core_facility": core_electricity_MWh,
            "cooling_auxiliary": cooling_electricity_MWh,
        },
        "cooling_auxiliary_peak_MW": cooling_auxiliary_peak_MW,
        "thermal_process_peak_MW": thermal_process_peak_MW,
        "heat_rejection_peak_MW": heat_rejection_peak_MW,
        "energy_balance_relative_residual": energy_balance_residual,
        "heat_balance_relative_residual": heat_balance_residual,
        "gross_water_demand_m3": gross_water_demand_m3,
        "total_water_intensity_basis": total_water_intensity_basis,
        "upw_demand_m3": upw_demand_m3,
        "internal_recycled_flow_m3": internal_recycled_flow_m3,
        "effective_reuse_m3": effective_reuse_m3,
        "external_water_withdrawal_m3": external_withdrawal_m3,
        "water_consumption_m3": water_consumption_m3,
        "wastewater_m3": wastewater_m3,
        "water_balance_relative_residual": water_balance_residual,
        "external_water_withdrawal_m3_per_day": None if external_withdrawal_m3 is None else external_withdrawal_m3 / days,
        "wastewater_m3_per_day": None if wastewater_m3 is None else wastewater_m3 / days,
        "upw_not_greater_than_gross_water": upw_demand_m3 <= gross_water_demand_m3 + 1e-12,
    }


def reserve_margin(accredited_capacity_MW: float, peak_load_MW: float) -> float:
    capacity = require_finite("accredited_capacity_MW", accredited_capacity_MW, nonnegative=True)
    peak = require_finite("peak_load_MW", peak_load_MW, positive=True)
    return (capacity - peak) / peak
