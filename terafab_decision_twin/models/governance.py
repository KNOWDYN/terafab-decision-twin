from __future__ import annotations
from ..units import clamp


def governance_risk_index(partner_count: int, complexity_index: float, decision_latency_months: float, public_legitimacy_index: float) -> float:
    partner_term = min(1.0, max(0.0, (int(partner_count) - 1) / 10.0))
    latency_term = min(1.0, max(0.0, float(decision_latency_months) / 24.0))
    legitimacy_risk = 1.0 - clamp(public_legitimacy_index)
    return clamp(0.35 * partner_term + 0.35 * clamp(complexity_index) + 0.20 * latency_term + 0.10 * legitimacy_risk)


def governance_readiness(public_legitimacy_index: float, regulatory_readiness_index: float, complexity_index: float) -> float:
    return clamp(0.45 * public_legitimacy_index + 0.45 * regulatory_readiness_index + 0.10 * (1.0 - complexity_index))
