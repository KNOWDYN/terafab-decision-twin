from __future__ import annotations
from copy import deepcopy
from typing import Dict, Iterable, Tuple

from ..engine import run_scenario
from ..evidence import is_evidence_object


def _set_evidence_value(container: Dict, dotted_path: str, value: float) -> None:
    parts = dotted_path.split(".")
    obj = container
    for part in parts[:-1]:
        obj = obj[part]
    leaf = obj[parts[-1]]
    if is_evidence_object(leaf):
        leaf["value"] = value
    else:
        obj[parts[-1]] = value


def grid_search(scenario: Dict, variable_path: str, values: Iterable[float], objective: str = "legitimacy_margin") -> Tuple[float, Dict]:
    best_value = None
    best_result = None
    for value in values:
        trial = deepcopy(scenario)
        _set_evidence_value(trial, variable_path, float(value))
        result = run_scenario(trial)
        score = result["summary"].get(objective)
        if score is not None and (best_value is None or score > best_value):
            best_value = score
            best_result = result
    return best_value, best_result
