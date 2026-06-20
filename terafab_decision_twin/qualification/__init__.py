from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass(frozen=True)
class QualificationState:
    tool_qualification_index: float
    process_window_index: float
    customer_acceptance_index: float
    regulatory_readiness_index: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def qualification_readiness(state: QualificationState) -> float:
    vals = [state.tool_qualification_index, state.process_window_index, state.customer_acceptance_index, state.regulatory_readiness_index]
    bounded = [max(0.0, min(1.0, float(v))) for v in vals]
    return min(bounded)


def qualification_gate(readiness: float, threshold: float = 0.75) -> bool:
    return max(0.0, min(1.0, float(readiness))) >= float(threshold)
