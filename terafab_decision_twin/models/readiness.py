from __future__ import annotations

from math import prod
from ..units import clamp


def readiness_index(*components: float, mode: str = "geometric") -> float:
    vals = [clamp(c) for c in components]
    if not vals:
        return 0.0
    if mode == "minimum":
        return min(vals)
    product = prod(vals)
    return clamp(product ** (1.0 / len(vals)))


def readiness_bottleneck(components: dict[str, float]) -> str:
    if not components:
        return "none"
    return min(components, key=lambda k: float(components[k]))
