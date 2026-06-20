from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

from .units import HOURS_PER_YEAR

_STEP_HOURS = {
    "annual": HOURS_PER_YEAR,
    "quarterly": HOURS_PER_YEAR / 4.0,
    "monthly": HOURS_PER_YEAR / 12.0,
}

_STEP_COUNT = {"annual": 1, "quarterly": 4, "monthly": 12}

@dataclass(frozen=True)
class TimeStep:
    index: int
    year: int
    period: int
    label: str
    hours: float
    fraction_of_year: float


def build_time_axis(time_cfg: Dict) -> List[TimeStep]:
    start = int(time_cfg.get("start_year", 2026))
    end = int(time_cfg.get("end_year", start))
    step = str(time_cfg.get("time_step", "annual"))
    if end < start:
        raise ValueError("time.end_year must be >= time.start_year")
    if step not in _STEP_HOURS:
        raise ValueError(f"Unsupported time_step '{step}'. Use one of {sorted(_STEP_HOURS)}")
    axis: List[TimeStep] = []
    idx = 0
    for year in range(start, end + 1):
        for period in range(1, _STEP_COUNT[step] + 1):
            if step == "annual":
                label = f"{year}"
            elif step == "quarterly":
                label = f"{year}Q{period}"
            else:
                label = f"{year}M{period:02d}"
            axis.append(TimeStep(idx, year, period, label, _STEP_HOURS[step], _STEP_HOURS[step] / HOURS_PER_YEAR))
            idx += 1
    return axis
