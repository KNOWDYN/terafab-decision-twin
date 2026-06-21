from __future__ import annotations

import math
from typing import Any, Dict, Iterable, List, Mapping

REQUIRED_RESULT_KEYS = [
    "metadata",
    "summary",
    "time_series",
    "gates",
    "passed",
    "evidence",
    "unknowns",
    "matrices",
    "output_records",
]


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(float(value))


def validate_result_structure(result: Mapping[str, Any]) -> Dict[str, Any]:
    missing = [key for key in REQUIRED_RESULT_KEYS if key not in result]
    summary = result.get("summary", {}) if isinstance(result.get("summary", {}), Mapping) else {}
    nonfinite = [key for key, value in summary.items() if isinstance(value, (int, float)) and not math.isfinite(float(value))]
    matrix = result.get("matrices", {}) if isinstance(result.get("matrices", {}), Mapping) else {}
    matrix_presence = {name: name in matrix for name in ["gate_matrix", "module_output_matrix", "subsystem_state_matrix"]}
    passed = not missing and not nonfinite and all(matrix_presence.values())
    return {
        "check": "structural_validation",
        "passed": passed,
        "missing_result_keys": missing,
        "nonfinite_summary_fields": nonfinite,
        "matrix_presence": matrix_presence,
    }


def validate_reference_ranges(summary: Mapping[str, Any], reference_ranges: Mapping[str, Any]) -> Dict[str, Any]:
    flags: List[Dict[str, Any]] = []
    checked = 0
    for metric, spec in reference_ranges.items():
        if metric not in summary:
            continue
        value = summary.get(metric)
        if not _is_number(value):
            continue
        checked += 1
        low = spec.get("low")
        high = spec.get("high")
        status = spec.get("status", "reference_range")
        if low is not None and float(value) < float(low):
            flags.append({"metric": metric, "value": value, "bound": "low", "limit": low, "status": status, "notes": spec.get("notes", "")})
        if high is not None and float(value) > float(high):
            flags.append({"metric": metric, "value": value, "bound": "high", "limit": high, "status": status, "notes": spec.get("notes", "")})
    return {
        "check": "public_reference_range_validation",
        "passed": len(flags) == 0,
        "metrics_checked": checked,
        "range_flags": flags,
        "caution": "Reference ranges are screening aids unless replaced with authoritative, case-specific data.",
    }


def validation_scorecard(checks: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    rows = list(checks)
    passed = sum(1 for row in rows if row.get("passed"))
    total = len(rows)
    return {
        "checks_total": total,
        "checks_passed": passed,
        "checks_failed": total - passed,
        "score": passed / total if total else None,
        "validation_level": "Level 2 - structural and public-reference screening" if passed == total and total else "Level 1 - structural/calibration-gap screening",
    }
