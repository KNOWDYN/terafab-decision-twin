from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass(frozen=True)
class ContaminationState:
    particle_control_index: float
    chemical_control_index: float
    excursion_rate_per_year: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def contamination_loss_fraction(particle_control_index: float, chemical_control_index: float, excursion_rate_per_year: float, sensitivity: float = 0.05) -> float:
    pc = max(0.0, min(1.0, float(particle_control_index)))
    cc = max(0.0, min(1.0, float(chemical_control_index)))
    excursions = max(0.0, float(excursion_rate_per_year))
    loss = (1.0 - pc) * 0.5 + (1.0 - cc) * 0.5 + excursions * float(sensitivity)
    return max(0.0, min(1.0, loss))


def contamination_readiness(state: ContaminationState) -> float:
    loss = contamination_loss_fraction(state.particle_control_index, state.chemical_control_index, state.excursion_rate_per_year)
    return max(0.0, min(1.0, 1.0 - loss))
