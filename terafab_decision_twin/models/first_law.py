from __future__ import annotations


def open_system_energy_rate_MW(enthalpy_in_MW: float, enthalpy_out_MW: float, heat_in_MW: float, work_in_MW: float) -> float:
    return float(enthalpy_in_MW) - float(enthalpy_out_MW) + float(heat_in_MW) + float(work_in_MW)


def heat_rejection_required_MW(site_electric_load_MW: float, heat_rejection_fraction: float = 0.98, waste_heat_MW: float = 0.0, stored_product_energy_MW: float = 0.0) -> float:
    return max(0.0, float(site_electric_load_MW) * float(heat_rejection_fraction) + float(waste_heat_MW) - float(stored_product_energy_MW))
