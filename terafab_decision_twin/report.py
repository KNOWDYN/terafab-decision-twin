from __future__ import annotations
from typing import Dict, Any


def _fmt(v):
    if v is None:
        return "n/a"
    if isinstance(v, float):
        if abs(v) >= 1_000_000:
            return f"{v:,.3g}"
        return f"{v:,.4g}"
    return str(v)


def markdown_report(result: Dict[str, Any]) -> str:
    meta = result.get("metadata", {})
    summary = result.get("summary", {})
    lines = []
    lines.append(f"# Terafab Decision Twin Report — {meta.get('title', meta.get('scenario_id', 'scenario'))}")
    lines.append("")
    lines.append("## Executive status")
    lines.append("")
    lines.append(f"- Scenario ID: `{meta.get('scenario_id')}`")
    lines.append(f"- Overall gate result: **{'PASS' if result.get('passed') else 'FAIL'}**")
    lines.append(f"- Recommended phase action: `{summary.get('recommended_phase_action')}`")
    lines.append("")
    lines.append("## Key scalar outputs")
    lines.append("")
    rows = [
        ("Energy", "energy_MWh", "MWh"),
        ("Peak site load", "peak_site_load_MW", "MW"),
        ("Heat rejection required", "heat_rejection_required_MW", "MW"),
        ("Water withdrawal", "water_withdrawal_m3", "m3"),
        ("Good die", "good_die", "die"),
        ("Average effective yield", "average_effective_yield", "fraction"),
        ("Total cost", "total_cost_USD", "USD"),
        ("Cost per good die", "cost_per_good_die_USD", "USD/die"),
        ("Emissions", "emissions_tCO2", "tCO2"),
        ("Public benefit", "public_benefit_index", "index"),
        ("Public burden", "public_burden_index", "index"),
        ("Legitimacy margin", "legitimacy_margin", "index"),
    ]
    lines.append("| Metric | Value | Unit |")
    lines.append("|---|---:|---|")
    for label, key, unit in rows:
        lines.append(f"| {label} | {_fmt(summary.get(key))} | {unit} |")
    lines.append("")
    lines.append("## Due-diligence gates")
    lines.append("")
    lines.append("| Gate | Status | Severity | Margin | Message |")
    lines.append("|---|---|---|---:|---|")
    for gate in result.get("gates", []):
        status = "PASS" if gate.get("passed") else "FAIL"
        lines.append(f"| {gate.get('name')} | {status} | {gate.get('severity')} | {_fmt(gate.get('margin'))} | {gate.get('message')} |")
    lines.append("")
    lines.append("## Evidence audit")
    lines.append("")
    ev = result.get("evidence", {})
    lines.append("Status counts:")
    for status, count in ev.get("status_counts", {}).items():
        lines.append(f"- `{status}`: {count}")
    if ev.get("warnings"):
        lines.append("")
        lines.append("Warnings:")
        for w in ev["warnings"]:
            lines.append(f"- {w}")
    if ev.get("errors"):
        lines.append("")
        lines.append("Errors:")
        for e in ev["errors"]:
            lines.append(f"- {e}")
    lines.append("")
    lines.append("## Reproducibility")
    lines.append("")
    for key, val in result.get("hashes", {}).items():
        lines.append(f"- `{key}`: `{val}`")
    lines.append("")
    lines.append("This report is a scenario-dependent model output, not a verified Terafab operating fact.")
    return "\n".join(lines) + "\n"
