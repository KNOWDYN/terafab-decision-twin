from __future__ import annotations
from ..units import clamp, safe_div


def public_benefit_index(domestic_supply_security_index: float, jobs_created: float, public_legitimacy_index: float, water_stress_index: float, emissions_tCO2: float, energy_MWh: float) -> float:
    jobs_term = min(1.0, max(0.0, float(jobs_created) / 10000.0))
    emissions_intensity_t_per_MWh = safe_div(emissions_tCO2, energy_MWh, 0.0)
    emissions_term = max(0.0, 1.0 - min(1.0, emissions_intensity_t_per_MWh))
    water_term = 1.0 - clamp(water_stress_index)
    return clamp(
        0.35 * clamp(domestic_supply_security_index)
        + 0.20 * jobs_term
        + 0.20 * clamp(public_legitimacy_index)
        + 0.15 * water_term
        + 0.10 * emissions_term
    )


def public_burden_index(incentive_public_USD: float, water_stress_index: float, emissions_tCO2: float, energy_MWh: float) -> float:
    incentive_term = min(1.0, max(0.0, float(incentive_public_USD) / 10_000_000_000.0))
    emissions_term = min(1.0, safe_div(emissions_tCO2, max(energy_MWh, 1.0), 0.0))
    return clamp(0.45 * incentive_term + 0.35 * clamp(water_stress_index) + 0.20 * emissions_term)


def legitimacy_margin(public_benefit: float, public_burden: float) -> float:
    return float(public_benefit) - float(public_burden)
