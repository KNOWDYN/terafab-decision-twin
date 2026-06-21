from __future__ import annotations

from typing import Any, Dict, Mapping


def _first_quantile(mc: Mapping[str, Any], metric: str, q: str = "p50") -> Any:
    return mc.get("metric_quantiles", {}).get(metric, {}).get(q)


def build_stakeholder_decision_surface(
    *,
    monte_carlo: Mapping[str, Any] | None = None,
    game: Mapping[str, Any] | None = None,
    rom: Mapping[str, Any] | None = None,
    validation: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    """Combine advanced-layer results into a compact stakeholder surface."""
    mc = monte_carlo or {}
    gm = game or {}
    rm = rom or {}
    val = validation or {}
    gate_failure = mc.get("failed_probability")
    conflict = gm.get("conflict_index")
    rom_warning = rm.get("diagnostics", {}).get("stability_warning")
    range_flags = val.get("range_flags", [])
    concerns = []
    if isinstance(gate_failure, (int, float)) and gate_failure > 0.25:
        concerns.append("high_gate_failure_probability")
    if isinstance(conflict, (int, float)) and conflict > 0.5:
        concerns.append("high_stakeholder_conflict")
    if rom_warning:
        concerns.append("reduced_order_trajectory_instability")
    if range_flags:
        concerns.append("public_reference_range_flags")
    if not concerns:
        recommendation = "stage_and_monitor"
    elif "high_gate_failure_probability" in concerns or "reduced_order_trajectory_instability" in concerns:
        recommendation = "hold_or_redesign"
    else:
        recommendation = "stage_and_monitor"
    return {
        "kind": "stakeholder_decision_surface",
        "model_boundary": "Screening surface derived from declared scenarios and validation checks; not investment advice or official Terafab validation.",
        "board_view": {
            "gate_failure_probability": gate_failure,
            "dominant_gate_risks": mc.get("gate_failure_probability", {}),
            "recommended_phase_posture": recommendation,
        },
        "investor_view": {
            "total_cost_USD_p50": _first_quantile(mc, "total_cost_USD"),
            "cost_per_good_die_USD_p50": _first_quantile(mc, "cost_per_good_die_USD"),
            "cost_per_compute_watt_USD_p50": _first_quantile(mc, "cost_per_compute_watt_USD"),
            "strategic_conflict_index": conflict,
        },
        "policy_view": {
            "water_margin_p10": _first_quantile(mc, "minimum_water_withdrawal_margin_m3_per_day", "p10"),
            "wastewater_margin_p10": _first_quantile(mc, "minimum_wastewater_discharge_margin_m3_per_day", "p10"),
            "legitimacy_margin_p10": _first_quantile(mc, "legitimacy_margin", "p10"),
            "range_flags": range_flags,
        },
        "research_view": {
            "monte_carlo_runs": mc.get("runs_completed"),
            "game_profiles": gm.get("profile_count"),
            "rom_steps": rm.get("steps"),
            "validation_level": val.get("validation_level"),
        },
        "concerns": concerns,
        "recommended_phase_posture": recommendation,
    }
