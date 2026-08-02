"""Prospective Terafab production-to-energy constraint-analysis overlay.

This source-available module produces scenario-dependent analytical estimates.
It contains no verified Terafab operating data and makes no official
feasibility, engineering, regulatory, investment, or affiliation claim.
"""

from .engine import MODEL_VERSION, run_case
from .models import (
    EnergySecurityCase,
    ErcotInputs,
    FacilityInputs,
    ManufacturingInputs,
    NationalInputs,
    SupplyInputs,
    TargetInputs,
)
from .pathways import build_scenario_matrix, load_scenario_config, run_scenario_matrix
from .publication import build_publication_bundle
from .uncertainty import (
    correlation_stress_test,
    dependence_aware_sensitivity,
    independent_sobol_sensitivity,
    load_uncertainty_contract,
)

__all__ = [
    "MODEL_VERSION",
    "EnergySecurityCase",
    "ErcotInputs",
    "FacilityInputs",
    "ManufacturingInputs",
    "NationalInputs",
    "SupplyInputs",
    "TargetInputs",
    "run_case",
    "build_scenario_matrix",
    "load_scenario_config",
    "run_scenario_matrix",
    "build_publication_bundle",
    "correlation_stress_test",
    "dependence_aware_sensitivity",
    "independent_sobol_sensitivity",
    "load_uncertainty_contract",
]
