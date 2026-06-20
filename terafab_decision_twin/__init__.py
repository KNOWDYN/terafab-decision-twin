"""Terafab Decision Twin: evidence-gated thermodynamic/economic/policy simulation."""

from .engine import run_scenario, MODEL_VERSION
from .schema import load_scenario, validate_scenario

__all__ = ["run_scenario", "load_scenario", "validate_scenario", "MODEL_VERSION"]
__version__ = MODEL_VERSION
