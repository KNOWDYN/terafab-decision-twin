"""Typed inputs for the Energy Conversion and Management study overlay."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any, Mapping, TypeVar


@dataclass(frozen=True)
class TargetInputs:
    rated_output_W_per_year: float
    target_fraction: float
    interpretation: str
    interpretation_admitted: bool


@dataclass(frozen=True)
class ManufacturingInputs:
    module_rated_power_W: float
    die_area_mm2: float
    wafer_diameter_mm: float
    effective_yield: float
    logic_dies_per_module: float
    capacity_wafers_per_month: float | None = None


@dataclass(frozen=True)
class FacilityInputs:
    electricity_kWh_per_wafer: float
    load_factor: float
    cooling_cop: float
    total_water_m3_per_wafer: float
    total_water_intensity_basis: str
    upw_m3_per_wafer: float
    water_recycling_fraction: float
    coincident_peak_multiplier: float = 1.0
    recycling_displacement_fraction: float | None = None
    consumptive_fraction: float | None = None
    heat_rejection_capacity_MW: float | None = None
    withdrawal_capacity_m3_per_day: float | None = None
    wastewater_capacity_m3_per_day: float | None = None
    operating_days_per_year: float = 365.25


@dataclass(frozen=True)
class SupplyInputs:
    grid_interconnection_capacity_MW: float | None
    grid_interconnection_year: int | None
    grid_accredited_addition_MW: float = 0.0
    firm_onsite_nameplate_MW: float = 0.0
    firm_onsite_availability_fraction: float = 0.0
    firm_fuel_availability_fraction: float = 0.0
    firm_onsite_commissioning_year: int | None = None
    renewable_nameplate_MW: float = 0.0
    renewable_elcc_fraction: float = 0.0
    renewable_commissioning_year: int | None = None
    storage_nameplate_MW: float = 0.0
    storage_elcc_fraction: float = 0.0
    storage_commissioning_year: int | None = None
    onsite_annual_energy_MWh: float = 0.0


@dataclass(frozen=True)
class ErcotInputs:
    year: int
    baseline_peak_load_MW: float | None
    baseline_reserve_margin_fraction: float | None
    lole_events_per_year: float | None = None
    maximum_event_duration_hours: float | None = None
    highest_hourly_average_load_shed_MW: float | None = None
    lole_limit_events_per_year: float = 0.1
    duration_limit_hours: float = 12.0
    magnitude_limit_MW: float | None = None


@dataclass(frozen=True)
class NationalInputs:
    annual_electricity_TWh: float
    peak_load_MW: float | None = None


@dataclass(frozen=True)
class EnergySecurityCase:
    case_id: str
    year: int
    facility_operation_year: int
    target: TargetInputs
    manufacturing: ManufacturingInputs
    facility: FacilityInputs
    supply: SupplyInputs
    ercot: ErcotInputs
    national: NationalInputs
    evidence_sufficient_for_case: bool | None = None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "EnergySecurityCase":
        return cls(
            case_id=str(payload["case_id"]),
            year=int(payload["year"]),
            facility_operation_year=int(payload["facility_operation_year"]),
            target=_from_mapping(TargetInputs, payload["target"]),
            manufacturing=_from_mapping(ManufacturingInputs, payload["manufacturing"]),
            facility=_from_mapping(FacilityInputs, payload["facility"]),
            supply=_from_mapping(SupplyInputs, payload["supply"]),
            ercot=_from_mapping(ErcotInputs, payload["ercot"]),
            national=_from_mapping(NationalInputs, payload["national"]),
            evidence_sufficient_for_case=payload.get("evidence_sufficient_for_case"),
        )


T = TypeVar("T")


def _from_mapping(model: type[T], payload: Mapping[str, Any]) -> T:
    allowed = {field.name for field in fields(model)}
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError(f"Unknown {model.__name__} fields: {unknown}")
    return model(**dict(payload))
