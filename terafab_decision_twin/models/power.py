from __future__ import annotations

from ..units import MWH_TO_KWH


def energy_consumption_MWh(load_MW: float, hours: float, load_factor: float) -> float:
    return max(0.0, float(load_MW) * float(hours) * float(load_factor))


def firm_capacity_margin_MW(firm_capacity_MW: float, site_load_MW: float, reserve_margin_fraction: float = 0.15) -> float:
    required = float(site_load_MW) * (1.0 + float(reserve_margin_fraction))
    return float(firm_capacity_MW) - required


def emissions_tCO2(energy_MWh: float, grid_carbon_intensity_kg_per_MWh: float) -> float:
    return max(0.0, float(energy_MWh) * float(grid_carbon_intensity_kg_per_MWh) / 1000.0)


def electricity_cost_USD(energy_MWh: float, price_USD_per_MWh: float) -> float:
    return max(0.0, float(energy_MWh) * float(price_USD_per_MWh))
