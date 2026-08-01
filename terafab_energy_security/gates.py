"""Tri-state scientific decision gates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Iterable


class GateStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    status: GateStatus
    required: bool
    margin: float | None
    reason: str
    details: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["status"] = self.status.value
        return payload


def classify(gates: Iterable[GateResult]) -> str:
    required = [gate for gate in gates if gate.required]
    if any(gate.status is GateStatus.INDETERMINATE for gate in required):
        return "indeterminate"
    if any(gate.status is GateStatus.FAIL for gate in required):
        return "not_demonstrated"
    return "conditionally_feasible"


def binding_constraint(gates: Iterable[GateResult]) -> str | None:
    required = [gate for gate in gates if gate.required]
    indeterminate = [gate for gate in required if gate.status is GateStatus.INDETERMINATE]
    if indeterminate:
        return indeterminate[0].gate_id
    failed = [gate for gate in required if gate.status is GateStatus.FAIL]
    if failed:
        numeric = [gate for gate in failed if gate.margin is not None]
        return min(numeric, key=lambda item: item.margin).gate_id if numeric else failed[0].gate_id
    numeric = [gate for gate in required if gate.margin is not None]
    return min(numeric, key=lambda item: item.margin).gate_id if numeric else None
