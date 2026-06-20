from __future__ import annotations

from dataclasses import dataclass, asdict
from math import exp
from typing import Dict, Any

@dataclass(frozen=True)
class CleanroomState:
    airflow_turnovers_per_hour: float
    filtration_efficiency: float
    particle_load_index: float
    thermal_stability_index: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def particle_control_index(airflow_turnovers_per_hour: float, filtration_efficiency: float, particle_load_index: float) -> float:
    """Dimensionless proxy for cleanroom particle control; higher is better."""
    if airflow_turnovers_per_hour < 0 or particle_load_index < 0:
        raise ValueError("Cleanroom inputs must be non-negative.")
    removal = 1.0 - exp(-float(airflow_turnovers_per_hour) * max(0.0, min(1.0, float(filtration_efficiency))) / 100.0)
    burden = 1.0 / (1.0 + float(particle_load_index))
    return max(0.0, min(1.0, removal * burden))


def cleanroom_readiness(state: CleanroomState) -> float:
    pci = particle_control_index(state.airflow_turnovers_per_hour, state.filtration_efficiency, state.particle_load_index)
    return max(0.0, min(1.0, (pci * max(0.0, min(1.0, state.thermal_stability_index))) ** 0.5))
