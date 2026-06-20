from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .evidence import audit_evidence

REQUIRED_TOP_LEVEL = [
    "metadata", "time", "terafab_phase", "energy", "cooling", "water",
    "manufacturing", "economics", "governance", "policy", "control"
]

REQUIRED_SECTIONS = {
    "metadata": ["scenario_id", "title", "version"],
    "time": ["start_year", "end_year", "time_step"],
    "terafab_phase": ["phase"],
    "energy": ["site_electric_load_MW", "load_factor", "firm_capacity_MW"],
    "cooling": ["heat_rejection_capacity_MW", "heat_rejection_fraction", "cop"],
    "water": ["withdrawal_m3_per_MWh", "consumptive_fraction", "permit_withdrawal_m3_per_day"],
    "manufacturing": ["wafer_starts_per_month", "die_per_wafer", "baseline_yield"],
    "economics": ["electricity_price_USD_per_MWh", "water_price_USD_per_m3", "capex_USD"],
    "governance": ["partner_count", "governance_complexity_index"],
    "policy": ["jobs_created", "domestic_supply_security_index", "public_legitimacy_index"],
}


def load_scenario(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _has_value(section: Dict[str, Any], key: str) -> bool:
    if key not in section:
        return False
    value = section[key]
    if isinstance(value, dict) and "value" in value:
        return value.get("value") is not None or value.get("status") == "unknown"
    return value is not None


def validate_scenario(scenario: Dict[str, Any], strict: bool | None = None) -> List[str]:
    errors: List[str] = []
    for section in REQUIRED_TOP_LEVEL:
        if section not in scenario:
            errors.append(f"Missing required top-level section: {section}")
    for section, keys in REQUIRED_SECTIONS.items():
        if section not in scenario or not isinstance(scenario.get(section), dict):
            continue
        for key in keys:
            if not _has_value(scenario[section], key):
                errors.append(f"Missing required field: {section}.{key}")
    time = scenario.get("time", {})
    if time:
        start = int(time.get("start_year", 0))
        end = int(time.get("end_year", 0))
        if start < 2026:
            errors.append("time.start_year must be >= 2026 for this forward-looking model.")
        if end < start:
            errors.append("time.end_year must be >= time.start_year.")
        if time.get("time_step") not in {"monthly", "quarterly", "annual"}:
            errors.append("time.time_step must be monthly, quarterly, or annual.")
    strict_mode = bool(scenario.get("control", {}).get("strict_evidence", False)) if strict is None else strict
    for issue in audit_evidence(scenario, strict=strict_mode):
        if issue.severity == "error":
            errors.append(f"Evidence error at {issue.path}: {issue.message}")
    return errors


def assert_valid_scenario(scenario: Dict[str, Any]) -> None:
    errors = validate_scenario(scenario)
    if errors:
        raise ValueError("Invalid scenario:\n" + "\n".join(f"- {e}" for e in errors))
