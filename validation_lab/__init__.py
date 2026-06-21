"""Validation-readiness tools for advanced Terafab scenario simulation.

The validation lab provides structural checks, public-reference range checks,
and calibration-gap reporting. It does not certify official Terafab reality.
"""

from .validators import validate_result_structure, validate_reference_ranges, validation_scorecard
from .validation_report import build_validation_report

__all__ = [
    "validate_result_structure",
    "validate_reference_ranges",
    "validation_scorecard",
    "build_validation_report",
]
