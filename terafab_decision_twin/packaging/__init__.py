from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass(frozen=True)
class PackagingState:
    substrate_availability_index: float
    advanced_packaging_capacity_index: float
    interconnect_yield_index: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def packaging_readiness(state: PackagingState) -> float:
    vals = [state.substrate_availability_index, state.advanced_packaging_capacity_index, state.interconnect_yield_index]
    bounded = [max(0.0, min(1.0, float(v))) for v in vals]
    return (bounded[0] * bounded[1] * bounded[2]) ** (1.0 / 3.0)


def packaging_capacity_good_die_limit(good_die: float, packaging_capacity_good_die: float) -> float:
    return max(0.0, min(float(good_die), float(packaging_capacity_good_die)))
