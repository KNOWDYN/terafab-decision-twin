"""Advanced strategic simulation layer for the Terafab Decision Twin.

This root-level package is intentionally thin: it uses the existing
``terafab_decision_twin`` deterministic kernel rather than replacing it.
It adds uncertainty propagation, finite game analysis, reduced-order
trajectory simulation, and stakeholder-facing decision surfaces.
"""

from .monte_carlo import run_monte_carlo, sample_distribution
from .game_theory import analyze_normal_form_game
from .reduced_order_model import simulate_reduced_order_model
from .stakeholder_surface import build_stakeholder_decision_surface

__all__ = [
    "run_monte_carlo",
    "sample_distribution",
    "analyze_normal_form_game",
    "simulate_reduced_order_model",
    "build_stakeholder_decision_surface",
]
