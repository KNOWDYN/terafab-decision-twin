from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Tuple

CANONICAL_STATUSES = {
    "verified_project_fact",
    "model_identity",
    "filed_claimed",
    "reported",
    "user_provided",
    "scenario_assumption",
    "stress_test_assumption",
    "unknown",
    "confidential_private_input",
    "derived_output",
}

STATUS_ALIASES = {
    "verified_fact": "verified_project_fact",
    "verified": "verified_project_fact",
    "locked_model_identity": "model_identity",
    "filed_claim": "filed_claimed",
    "reported_claim": "reported",
    "user_input": "user_provided",
    "assumption": "scenario_assumption",
    "confidential_input": "confidential_private_input",
    "private_confidential_input": "confidential_private_input",
}

ALLOWED_STATUSES = CANONICAL_STATUSES | set(STATUS_ALIASES)
UNVERIFIED_STATUSES = CANONICAL_STATUSES - {"verified_project_fact", "model_identity", "derived_output"}
INPUT_SECTIONS = {
    "terafab_phase", "energy", "cooling", "water", "manufacturing", "economics", "governance", "policy", "control"
}

@dataclass(frozen=True)
class EvidenceIssue:
    path: str
    severity: str
    message: str

@dataclass(frozen=True)
class EvidenceInput:
    value: Any
    unit: str
    status: str
    source_ref: str
    confidence: str
    notes: str

@dataclass(frozen=True)
class UnknownValue:
    path: str
    unit: str = ""
    reason: str = "Input was declared unknown."

    def to_dict(self) -> Dict[str, str]:
        return {"path": self.path, "unit": self.unit, "reason": self.reason}


def normalize_status(status: Any, default: str = "scenario_assumption") -> str:
    raw = str(status if status is not None else default).strip()
    return STATUS_ALIASES.get(raw, raw)


def is_evidence_object(value: Any) -> bool:
    return isinstance(value, dict) and "value" in value and ("status" in value or "unit" in value or "source" in value or "source_ref" in value)


def ensure_evidence_object(value: Any, *, status: str = "scenario_assumption", unit: str = "", source_ref: str = "scenario_author", confidence: str = "declared", notes: str = "Scenario-declared value; not a verified Terafab operating fact.") -> Dict[str, Any]:
    if is_evidence_object(value):
        obj = dict(value)
        obj["status"] = normalize_status(obj.get("status", status))
        obj.setdefault("unit", unit)
        if "source_ref" not in obj and "source" in obj:
            obj["source_ref"] = obj.get("source")
        obj.setdefault("source_ref", source_ref)
        obj.setdefault("confidence", confidence)
        if "notes" not in obj and "rationale" in obj:
            obj["notes"] = obj.get("rationale")
        obj.setdefault("notes", notes)
        return obj
    return {
        "value": value,
        "unit": unit,
        "status": normalize_status(status),
        "source_ref": source_ref,
        "confidence": confidence,
        "notes": notes,
    }


def unwrap(value: Any, default: Any = None) -> Any:
    if is_evidence_object(value):
        return value.get("value", default)
    if value is None:
        return default
    return value


def status_of(value: Any, default: str = "scenario_assumption") -> str:
    if is_evidence_object(value):
        return normalize_status(value.get("status", default), default)
    return normalize_status(default)


def unit_of(value: Any, default: str = "") -> str:
    if is_evidence_object(value):
        return str(value.get("unit", default))
    return default


def source_of(value: Any, default: str = "") -> str:
    if is_evidence_object(value):
        return str(value.get("source_ref", value.get("source", default)))
    return default


def confidence_of(value: Any, default: str = "") -> str:
    if is_evidence_object(value):
        return str(value.get("confidence", default))
    return default


def notes_of(value: Any, default: str = "") -> str:
    if is_evidence_object(value):
        return str(value.get("notes", value.get("rationale", default)))
    return default


def walk_inputs(obj: Any, prefix: str = "") -> Iterable[Tuple[str, Any]]:
    if is_evidence_object(obj):
        yield prefix, obj
        return
    if isinstance(obj, dict):
        for key, child in obj.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            yield from walk_inputs(child, child_prefix)
    elif isinstance(obj, list):
        for idx, child in enumerate(obj):
            yield from walk_inputs(child, f"{prefix}[{idx}]")


def normalize_evidence_tree(obj: Any) -> Any:
    if is_evidence_object(obj):
        return ensure_evidence_object(obj)
    if isinstance(obj, dict):
        return {k: normalize_evidence_tree(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize_evidence_tree(v) for v in obj]
    return obj


def material_input_paths(scenario: Mapping[str, Any]) -> Iterable[Tuple[str, Any]]:
    for section_name in INPUT_SECTIONS:
        section = scenario.get(section_name)
        if not isinstance(section, dict):
            continue
        for key, value in section.items():
            if key in {"strict_evidence", "fail_on_unverified_claims", "allow_unknown_substitution", "output_format"}:
                continue
            yield f"{section_name}.{key}", value


def audit_evidence(scenario: Dict[str, Any], strict: bool = False) -> List[EvidenceIssue]:
    issues: List[EvidenceIssue] = []
    for path, obj in walk_inputs(scenario):
        status = normalize_status(obj.get("status", "scenario_assumption"))
        if status not in CANONICAL_STATUSES:
            issues.append(EvidenceIssue(path, "error", f"Invalid evidence status '{obj.get('status')}'."))
        if status in {"verified_project_fact", "model_identity", "filed_claimed", "reported"} and not source_of(obj).strip():
            issues.append(EvidenceIssue(path, "error", f"{status} requires a non-empty source_ref."))
        if status == "unknown" and obj.get("value") not in (None, "", "unknown"):
            issues.append(EvidenceIssue(path, "warning", "unknown status should not carry a concrete value."))
        if status == "derived_output":
            issues.append(EvidenceIssue(path, "warning", "derived_output should normally appear in outputs, not input scenarios."))
        if strict:
            if not source_of(obj).strip():
                issues.append(EvidenceIssue(path, "warning", "Strict evidence mode expects source_ref for every evidence-coded input."))
            if not str(obj.get("confidence", "")).strip():
                issues.append(EvidenceIssue(path, "warning", "Strict evidence mode expects confidence for every evidence-coded input."))
            if not notes_of(obj).strip():
                issues.append(EvidenceIssue(path, "warning", "Strict evidence mode expects notes for every evidence-coded input."))
    for path, value in material_input_paths(scenario):
        if not is_evidence_object(value):
            sev = "error" if strict else "warning"
            issues.append(EvidenceIssue(path, sev, "Material scenario inputs should be evidence-coded objects."))
    return issues


def summarize_statuses(scenario: Dict[str, Any]) -> Dict[str, int]:
    counts = {status: 0 for status in sorted(CANONICAL_STATUSES)}
    for _, obj in walk_inputs(scenario):
        status = normalize_status(obj.get("status", "scenario_assumption"))
        counts[status] = counts.get(status, 0) + 1
    return {k: v for k, v in counts.items() if v}


def collect_assumptions(scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for path, obj in walk_inputs(scenario):
        status = normalize_status(obj.get("status", "scenario_assumption"))
        if status in {"scenario_assumption", "stress_test_assumption", "user_provided", "unknown"}:
            rows.append({
                "path": path,
                "value": obj.get("value"),
                "unit": unit_of(obj),
                "status": status,
                "source_ref": source_of(obj),
                "confidence": confidence_of(obj),
                "notes": notes_of(obj),
            })
    return rows


def collect_verified_facts(scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for path, obj in walk_inputs(scenario):
        status = normalize_status(obj.get("status", "scenario_assumption"))
        if status in {"verified_project_fact", "model_identity", "filed_claimed", "reported"}:
            rows.append({"path": path, "value": obj.get("value"), "unit": unit_of(obj), "status": status, "source_ref": source_of(obj), "confidence": confidence_of(obj), "notes": notes_of(obj)})
    return rows


def v(section: Dict[str, Any], key: str, default: Any = None) -> Any:
    return unwrap(section.get(key), default)
