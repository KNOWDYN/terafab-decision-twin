from __future__ import annotations


def heat_exergy_MW(heat_MW: float, boundary_temperature_K: float, ambient_temperature_K: float = 298.15) -> float:
    if boundary_temperature_K <= 0 or ambient_temperature_K <= 0:
        raise ValueError("Temperatures must be positive Kelvin values.")
    carnot_factor = max(0.0, 1.0 - ambient_temperature_K / boundary_temperature_K)
    return float(heat_MW) * carnot_factor


def exergy_destroyed_MW(ambient_temperature_K: float, entropy_generation_MW_per_K: float) -> float:
    return max(0.0, float(ambient_temperature_K) * float(entropy_generation_MW_per_K))


def exergy_efficiency(useful_output_MW: float, exergy_input_MW: float) -> float:
    return 0.0 if exergy_input_MW <= 0 else max(0.0, min(1.0, useful_output_MW / exergy_input_MW))
