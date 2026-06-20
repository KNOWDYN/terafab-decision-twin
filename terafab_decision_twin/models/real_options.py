from __future__ import annotations


def phase_gate_value(expected_value_USD: float, option_cost_USD: float, readiness: float, risk_index: float) -> float:
    return float(expected_value_USD) * max(0.0, min(1.0, readiness)) * (1.0 - max(0.0, min(1.0, risk_index))) - float(option_cost_USD)


def recommend_phase_action(phase_gate_value_USD: float, readiness: float, risk_index: float) -> str:
    if phase_gate_value_USD > 0 and readiness >= 0.7 and risk_index <= 0.5:
        return "advance"
    if readiness < 0.5 or risk_index > 0.75:
        return "hold_or_redesign"
    return "stage_and_monitor"
