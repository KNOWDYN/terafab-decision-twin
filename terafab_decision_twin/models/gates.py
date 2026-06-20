from __future__ import annotations

from dataclasses import dataclass, asdict
from math import isfinite
from typing import Any, Dict, List

@dataclass
class GateResult:
    name: str
    passed: bool
    severity: str
    margin: float | None
    message: str
    details: Dict[str, Any] | None = None

    def to_dict(self):
        return asdict(self)


def gate(name: str, passed: bool, severity: str, margin: float | None, message: str, details: Dict[str, Any] | None = None) -> GateResult:
    return GateResult(name, bool(passed), severity, margin, message, details or {})


def _num(summary: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        val = summary.get(key, default)
        return default if val is None else float(val)
    except Exception:
        return default


def evaluate_gates(summary: Dict[str, Any], evidence_errors: List[str] | None = None, unresolved_variables: List[Dict[str, Any]] | None = None) -> List[GateResult]:
    evidence_errors = evidence_errors or []
    unresolved_variables = unresolved_variables or []
    gates: List[GateResult] = []
    gates.append(gate(
        "unknown_input_discipline",
        len(unresolved_variables) == 0,
        "error",
        None,
        "No material unknown values were substituted." if not unresolved_variables else "Material unknown values make affected outputs underdetermined.",
        {"unresolved_count": len(unresolved_variables)},
    ))
    gates.append(gate("dimensional", all(_num(summary, k) >= 0 for k in ["energy_MWh", "water_withdrawal_m3", "good_die"]), "error", None, "Key extensive outputs must be non-negative."))
    hmargin = _num(summary, "minimum_heat_rejection_margin_MW")
    gates.append(gate("thermodynamic_heat_rejection", hmargin >= 0, "error", hmargin, "Cooling capacity after reserve margin must cover first-law heat load."))
    pmargin = _num(summary, "minimum_firm_capacity_margin_MW")
    gates.append(gate("power_firm_capacity", pmargin >= 0, "error", pmargin, "Firm power must cover site load plus reserve margin."))
    wmargin = _num(summary, "minimum_water_withdrawal_margin_m3_per_day")
    gates.append(gate("water_withdrawal_permit", wmargin >= 0, "error", wmargin, "Daily withdrawal must remain within permit capacity after water reserve margin."))
    dmargin = _num(summary, "minimum_wastewater_discharge_margin_m3_per_day")
    gates.append(gate("wastewater_discharge_permit", dmargin >= 0, "warning", dmargin, "Daily wastewater discharge should remain within permit capacity after wastewater reserve margin."))
    y = _num(summary, "average_effective_yield")
    gates.append(gate("manufacturing_yield", 0 <= y <= 1 and y > 0, "error", y, "Effective yield must be finite and within (0,1]."))
    cpg = summary.get("cost_per_good_die_USD")
    finite_cpg = cpg is not None and isfinite(float(cpg)) and float(cpg) >= 0
    gates.append(gate("economic_finiteness", finite_cpg, "error", None if cpg is None or not isfinite(float(cpg)) else float(cpg), "Cost per good die must be finite, non-negative, and supported by nonzero modeled good output."))
    lm = _num(summary, "legitimacy_margin")
    gates.append(gate("policy_legitimacy", lm >= -0.25, "warning", lm, "Public burden should not overwhelm modeled benefit."))
    gr = _num(summary, "maximum_governance_risk_index")
    gates.append(gate("governance_risk", gr <= 0.75, "warning", 0.75 - gr, "Governance complexity should remain below high-risk threshold."))
    gates.append(gate("evidence", len(evidence_errors) == 0, "error", None, "Evidence status audit passed." if not evidence_errors else "Evidence-coded inputs have invalid statuses or unsupported verified/filer/reported claims.", {"errors": evidence_errors}))
    return gates


def overall_passed(gates: List[GateResult]) -> bool:
    return not any((not g.passed and g.severity == "error") for g in gates)
