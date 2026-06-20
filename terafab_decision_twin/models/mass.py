from __future__ import annotations
from typing import Dict


def species_balance(inflows: Dict[str, float], outflows: Dict[str, float], reaction_sources: Dict[str, float] | None = None) -> Dict[str, float]:
    reaction_sources = reaction_sources or {}
    species = set(inflows) | set(outflows) | set(reaction_sources)
    return {k: float(inflows.get(k, 0.0)) - float(outflows.get(k, 0.0)) + float(reaction_sources.get(k, 0.0)) for k in species}


def campus_mass_residual_mdot(inputs: Dict[str, float], outputs: Dict[str, float]) -> float:
    return sum(float(v) for v in inputs.values()) - sum(float(v) for v in outputs.values())
