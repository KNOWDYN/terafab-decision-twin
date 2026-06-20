from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .evidence import audit_evidence, is_evidence_object, normalize_status, CANONICAL_STATUSES, INPUT_SECTIONS

REQUIRED_TOP_LEVEL = [
    "metadata", "time", "terafab_phase", "energy", "cooling", "water",
    "manufacturing", "economics", "governance", "policy", "control"
]

REQUIRED_SECTIONS = {
    "metadata": ["scenario_id", "title", "version", "scenario_author", "scenario_date", "model_version", "source_bundle_version", "scenario_purpose", "scenario_type"],
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

SCENARIO_TYPES = {"baseline", "stress_test", "counterfactual", "policy", "sensitivity", "multi_year", "demonstration"}
CONTROL_ACTIONS = {"build", "delay", "scale", "redesign", "allocate", "contract", "license", "partner", "curtail", "abandon"}


def load_scenario(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _has_value(section: Dict[str, Any], key: str) -> bool:
    if key not in section:
        return False
    value = section[key]
    if isinstance(value, dict) and "value" in value:
        return value.get("value") is not None or normalize_status(value.get("status")) == "unknown"
    return value is not None


def _validate_material_input(section_name: str, key: str, value: Any, strict: bool, errors: List[str]) -> None:
    if section_name not in INPUT_SECTIONS or section_name == "control":
        return
    if not is_evidence_object(value):
        errors.append(f"Material input must be evidence-coded: {section_name}.{key}")
        return
    status = normalize_status(value.get("status"))
    if status not in CANONICAL_STATUSES:
        errors.append(f"Invalid canonical evidence status at {section_name}.{key}: {value.get('status')}")
    for field in ["unit", "status", "source_ref", "confidence", "notes"]:
        if field not in value or value.get(field) in (None, ""):
            errors.append(f"Evidence input missing {field}: {section_name}.{key}")
    if status in {"verified_project_fact", "model_identity", "filed_claimed", "reported"} and not str(value.get("source_ref", "")).strip():
        errors.append(f"{status} requires source_ref: {section_name}.{key}")
    if strict and status in {"scenario_assumption", "stress_test_assumption"} and not str(value.get("notes", "")).strip():
        errors.append(f"Strict scenario requires notes for assumption: {section_name}.{key}")


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
    metadata = scenario.get("metadata", {})
    stype = metadata.get("scenario_type")
    if stype and stype not in SCENARIO_TYPES:
        errors.append(f"metadata.scenario_type must be one of {sorted(SCENARIO_TYPES)}")
    time = scenario.get("time", {})
    if time:
        try:
            start = int(time.get("start_year", 0))
            end = int(time.get("end_year", 0))
            if start < 2026:
                errors.append("time.start_year must be >= 2026 for this forward-looking model.")
            if end < start:
                errors.append("time.end_year must be >= time.start_year.")
        except Exception:
            errors.append("time.start_year and time.end_year must be integers.")
        if time.get("time_step") not in {"monthly", "quarterly", "annual"}:
            errors.append("time.time_step must be monthly, quarterly, or annual.")
    strict_mode = bool(scenario.get("control", {}).get("strict_evidence", False)) if strict is None else strict
    for section_name in ["terafab_phase", "energy", "cooling", "water", "manufacturing", "economics", "governance", "policy"]:
        section = scenario.get(section_name, {})
        if isinstance(section, dict):
            for key, value in section.items():
                _validate_material_input(section_name, key, value, strict_mode, errors)
    control = scenario.get("control", {})
    actions = control.get("allowed_actions", []) if isinstance(control, dict) else []
    if actions:
        bad = [a for a in actions if a not in CONTROL_ACTIONS]
        if bad:
            errors.append(f"control.allowed_actions contains invalid actions: {bad}")
    for issue in audit_evidence(scenario, strict=strict_mode):
        if issue.severity == "error":
            errors.append(f"Evidence error at {issue.path}: {issue.message}")
    return errors


def assert_valid_scenario(scenario: Dict[str, Any]) -> None:
    errors = validate_scenario(scenario)
    if errors:
        raise ValueError("Invalid scenario:\n" + "\n".join(f"- {e}" for e in errors))
