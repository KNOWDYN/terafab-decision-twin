from __future__ import annotations


def cooling_auxiliary_power_MW(heat_rejected_MW: float, cop: float) -> float:
    if cop <= 0:
        raise ValueError("Cooling COP must be positive.")
    return max(0.0, float(heat_rejected_MW) / float(cop))


def heat_rejection_margin_MW(capacity_MW: float, required_MW: float) -> float:
    return float(capacity_MW) - float(required_MW)


def cooling_tower_evaporation_m3_per_h(heat_MW: float, latent_heat_kWh_per_m3: float = 630.0) -> float:
    # Approximate evaporated water from latent heat of vaporization.
    heat_kWh_per_h = float(heat_MW) * 1000.0
    return max(0.0, heat_kWh_per_h / float(latent_heat_kWh_per_m3))
