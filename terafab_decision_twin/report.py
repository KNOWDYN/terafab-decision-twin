from __future__ import annotations
from typing import Dict, Any, Iterable


def _fmt(v):
    if v is None:
        return "underdetermined"
    if isinstance(v, float):
        if abs(v) >= 1_000_000:
            return f"{v:,.3g}"
        return f"{v:,.4g}"
    return str(v)


def _table(lines, rows, headers):
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("|" + "|".join(["---" for _ in headers]) + "|")
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")


def markdown_report(result: Dict[str, Any]) -> str:
    meta = result.get("metadata", {})
    summary = result.get("summary", {})
    lines = []
    lines.append(f"# Terafab Decision Twin Report — {meta.get('title', meta.get('scenario_id', 'scenario'))}")
    lines.append("")
    lines.append("This report is a conditional model output. It is not a verified Terafab operating fact and does not imply Terafab endorsement or confidential access.")
    lines.append("")
    lines.append("## Scenario identity")
    lines.append("")
    _table(lines, [
        ["Scenario ID", f"`{meta.get('scenario_id')}`"],
        ["Model version", f"`{meta.get('model_version') or meta.get('version')}`"],
        ["Schema version", f"`{meta.get('schema_version')}`"],
        ["Source bundle", f"`{meta.get('source_bundle_version')}`"],
        ["Scenario type", f"`{meta.get('scenario_type')}`"],
        ["Purpose", meta.get('scenario_purpose')],
        ["Overall gate result", "PASS" if result.get('passed') else "FAIL"],
    ], ["Field", "Value"])
    lines.append("")
    lines.append("## Executive status")
    lines.append("")
    lines.append(f"- Recommended phase action: `{summary.get('recommended_phase_action')}`")
    lines.append(f"- Unknown discipline: **{'UNDERDETERMINED' if result.get('unknowns', {}).get('underdetermined') else 'CLEAR'}**")
    lines.append(f"- One-terawatt status: `{summary.get('one_terawatt_status')}`")
    lines.append("")
    lines.append("## Key scalar outputs")
    lines.append("")
    rows = [
        ("Energy", "energy_MWh", "MWh"),
        ("Peak site load", "peak_site_load_MW", "MW"),
        ("Firm capacity margin", "minimum_firm_capacity_margin_MW", "MW"),
        ("Heat rejection required", "heat_rejection_required_MW", "MW"),
        ("Cooling margin", "minimum_heat_rejection_margin_MW", "MW"),
        ("Water withdrawal", "water_withdrawal_m3", "m3"),
        ("Withdrawal permit margin", "minimum_water_withdrawal_margin_m3_per_day", "m3/day"),
        ("Good die", "good_die", "die"),
        ("Average effective yield", "average_effective_yield", "fraction"),
        ("Average readiness", "average_readiness_index", "fraction"),
        ("Total cost", "total_cost_USD", "USD"),
        ("Cost per good die", "cost_per_good_die_USD", "USD/die"),
        ("Emissions", "emissions_tCO2", "tCO2"),
        ("Legitimacy margin", "legitimacy_margin", "index"),
    ]
    _table(lines, [[label, _fmt(summary.get(key)), unit] for label, key, unit in rows], ["Metric", "Value", "Unit"])
    lines.append("")
    lines.append("## Due-diligence gates")
    lines.append("")
    _table(lines, [[g.get('name'), "PASS" if g.get('passed') else "FAIL", g.get('severity'), _fmt(g.get('margin')), g.get('message')] for g in result.get('gates', [])], ["Gate", "Status", "Severity", "Margin", "Message"])
    lines.append("")
    lines.append("## Evidence summary")
    lines.append("")
    ev = result.get("evidence", {})
    for status, count in sorted(ev.get("status_counts", {}).items()):
        lines.append(f"- `{status}`: {count}")
    lines.append("")
    if ev.get("verified_or_reported_inputs"):
        lines.append("### Verified / filed / reported inputs")
        lines.append("")
        _table(lines, [[r.get('path'), r.get('status'), r.get('source_ref')] for r in ev.get("verified_or_reported_inputs", [])[:20]], ["Path", "Status", "Source"])
        lines.append("")
    lines.append("### Assumptions used")
    lines.append("")
    assumptions = ev.get("assumptions_used", [])
    _table(lines, [[r.get('path'), r.get('status'), _fmt(r.get('value')), r.get('unit')] for r in assumptions[:30]], ["Path", "Status", "Value", "Unit"])
    if len(assumptions) > 30:
        lines.append(f"\nAdditional assumptions not shown: {len(assumptions) - 30}.")
    lines.append("")
    lines.append("## Unresolved variables")
    lines.append("")
    unresolved = result.get("unknowns", {}).get("unresolved_variables", [])
    if unresolved:
        _table(lines, [[u.get('path'), u.get('status'), u.get('unit'), u.get('reason')] for u in unresolved], ["Path", "Status", "Unit", "Reason"])
    else:
        lines.append("No material unknown variables were substituted.")
    lines.append("")
    lines.append("## Formal module outputs")
    lines.append("")
    fm = result.get("formal_modules", {})
    _table(lines, [
        ["cleanroom", _fmt(summary.get("average_cleanroom_readiness_index")), "cleanroom readiness proxy"],
        ["contamination", _fmt(summary.get("average_contamination_readiness_index")), "contamination readiness proxy"],
        ["packaging", _fmt(summary.get("average_packaging_readiness_index")), "packaging readiness proxy"],
        ["qualification", _fmt(summary.get("average_qualification_readiness_index")), "qualification readiness proxy"],
    ], ["Module", "Value", "Meaning"])
    lines.append("")
    lines.append("## What this scenario can conclude")
    lines.append("")
    for item in result.get("interpretation", {}).get("can_conclude", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## What this scenario cannot conclude")
    lines.append("")
    for item in result.get("interpretation", {}).get("cannot_conclude", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Data that would change the result most")
    lines.append("")
    for item in result.get("interpretation", {}).get("highest_value_next_data", []):
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Reproducibility")
    lines.append("")
    for key, val in result.get("hashes", {}).items():
        lines.append(f"- `{key}`: `{val}`")
    lines.append("")
    lines.append("Rights and boundaries: KNOWDYN reserves all rights in the package. Terafab is owned by the official Terafab entity. This independent model is not affiliated with, endorsed by, authorized by, or connected to Terafab or its employees.")
    return "\n".join(lines) + "\n"
