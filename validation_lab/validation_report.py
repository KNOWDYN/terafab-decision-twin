from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping

from .validators import validate_reference_ranges, validate_result_structure, validation_scorecard


def load_reference_ranges(path: str | Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_validation_report(result: Mapping[str, Any], reference_ranges: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    """Build a validation-readiness report for one deterministic or sampled result."""
    checks = [validate_result_structure(result)]
    range_check = {"range_flags": []}
    if reference_ranges:
        range_check = validate_reference_ranges(result.get("summary", {}), reference_ranges)
        checks.append(range_check)
    scorecard = validation_scorecard(checks)
    calibration_gaps = []
    evidence = result.get("evidence", {}) if isinstance(result.get("evidence", {}), Mapping) else {}
    if evidence.get("status_counts", {}).get("scenario_assumption", 0):
        calibration_gaps.append("scenario_assumptions_require_external calibration before official validation")
    if evidence.get("status_counts", {}).get("stress_test_assumption", 0):
        calibration_gaps.append("stress_test_assumptions_are_not_observed_operating_data")
    if result.get("unknowns", {}).get("underdetermined"):
        calibration_gaps.append("material_unknowns_make_outputs_underdetermined")
    return {
        "kind": "validation_readiness_report",
        "model_boundary": "Validation-readiness screen; not official Terafab certification.",
        "checks": checks,
        "scorecard": scorecard,
        "validation_level": scorecard.get("validation_level"),
        "range_flags": range_check.get("range_flags", []),
        "calibration_gaps": calibration_gaps,
    }
