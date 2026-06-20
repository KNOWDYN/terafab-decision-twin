from __future__ import annotations

from ..units import clamp


def learned_yield(base_yield: float, learning_rate_per_year: float, years_since_start: float) -> float:
    return clamp(float(base_yield) + float(learning_rate_per_year) * float(years_since_start), 0.0, 1.0)


def effective_yield(base_yield: float, contamination_loss_fraction: float, qualification_readiness: float, packaging_readiness: float) -> float:
    y = float(base_yield) * (1.0 - float(contamination_loss_fraction)) * float(qualification_readiness) * float(packaging_readiness)
    return clamp(y, 0.0, 1.0)


def good_die_output(wafer_starts: float, die_per_wafer: float, yield_fraction: float) -> float:
    return max(0.0, float(wafer_starts) * float(die_per_wafer) * float(yield_fraction))


def compute_output_proxy(good_die: float, compute_watts_per_good_die: float) -> float:
    return max(0.0, float(good_die) * float(compute_watts_per_good_die))
