from __future__ import annotations

from ..units import DAYS_PER_YEAR


def withdrawal_m3(energy_MWh: float, withdrawal_m3_per_MWh: float) -> float:
    return max(0.0, float(energy_MWh) * float(withdrawal_m3_per_MWh))


def consumptive_use_m3(withdrawal_m3_value: float, consumptive_fraction: float) -> float:
    return max(0.0, float(withdrawal_m3_value) * float(consumptive_fraction))


def wastewater_m3(withdrawal_m3_value: float, wastewater_fraction: float) -> float:
    return max(0.0, float(withdrawal_m3_value) * float(wastewater_fraction))


def permit_margin_m3_per_day(annual_volume_m3: float, permit_m3_per_day: float, days: float = DAYS_PER_YEAR) -> float:
    return float(permit_m3_per_day) - float(annual_volume_m3) / float(days)


def permit_margin_with_reserve_m3_per_day(annual_volume_m3: float, permit_m3_per_day: float, reserve_margin_fraction: float = 0.0, days: float = DAYS_PER_YEAR) -> float:
    """Water/wastewater convention: daily demand <= permit_capacity * (1 - reserve_margin)."""
    available = float(permit_m3_per_day) * (1.0 - float(reserve_margin_fraction))
    return available - float(annual_volume_m3) / float(days)


def upw_demand_m3(wafer_starts: float, upw_m3_per_wafer: float) -> float:
    return max(0.0, float(wafer_starts) * float(upw_m3_per_wafer))
