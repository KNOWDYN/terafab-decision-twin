from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List

@dataclass(frozen=True)
class UnderdeterminedOutput:
    name: str
    reason: str
    affected_by: List[str]
    unit: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def safe_number(value: Any) -> float | None:
    try:
        if value is None:
            return None
        if isinstance(value, str) and value.strip().lower() in {"", "unknown", "n/a", "none"}:
            return None
        return float(value)
    except Exception:
        return None
