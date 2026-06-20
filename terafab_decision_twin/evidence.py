from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Tuple

ALLOWED_STATUSES = {
    "verified_fact",
    "filed_claim",
    "reported_claim",
    "user_input",
    "assumption",
    "stress_test_assumption",
    "unknown",
    "confidential_input",
    "derived_output",
}

UNVERIFIED_STATUSES = ALLOWED_STATUSES - {"verified_fact", "derived_output"}

@dataclass(frozen=True)
class EvidenceIssue:
    path: str
    severity: str
    message: str


def is_evidence_object(value: Any) -> bool:
    return isinstance(value, dict) and "value" in value and ("status" in value or "unit" in value or "source" in value)


def unwrap(value: Any, default: Any = None) -> Any:
    """Return the numerical/scalar value from an evidence-coded input."""
    if is_evidence_object(value):
        return value.get("value", default)
    if value is None:
        return default
    return value


def status_of(value: Any, default: str = "assumption") -> str:
    if is_evidence_object(value):
        return str(value.get("status", default))
    return default


def unit_of(value: Any, default: str = "") -> str:
    if is_evidence_object(value):
        return str(value.get("unit", default))
    return default


def source_of(value: Any, default: str = "") -> str:
    if is_evidence_object(value):
        return str(value.get("source", default))
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


def audit_evidence(scenario: Dict[str, Any], strict: bool = False) -> List[EvidenceIssue]:
    """Audit evidence-coded inputs without requiring confidential/raw sources."""
    issues: List[EvidenceIssue] = []
    for path, obj in walk_inputs(scenario):
        status = str(obj.get("status", "assumption"))
        if status not in ALLOWED_STATUSES:
            issues.append(EvidenceIssue(path, "error", f"Invalid evidence status '{status}'."))
        if status == "verified_fact" and not str(obj.get("source", "")).strip():
            issues.append(EvidenceIssue(path, "error", "verified_fact requires a non-empty source."))
        if status == "unknown" and obj.get("value") not in (None, "", "unknown"):
            issues.append(EvidenceIssue(path, "warning", "unknown status should not carry a concrete value."))
        if strict and not is_evidence_object(obj):
            issues.append(EvidenceIssue(path, "warning", "Strict evidence mode prefers evidence-coded input objects."))
    return issues


def summarize_statuses(scenario: Dict[str, Any]) -> Dict[str, int]:
    counts = {status: 0 for status in sorted(ALLOWED_STATUSES)}
    for _, obj in walk_inputs(scenario):
        counts[str(obj.get("status", "assumption"))] = counts.get(str(obj.get("status", "assumption")), 0) + 1
    return {k: v for k, v in counts.items() if v}


def v(section: Dict[str, Any], key: str, default: Any = None) -> Any:
    return unwrap(section.get(key), default)
