from __future__ import annotations

from dataclasses import dataclass, asdict
from math import isfinite
from typing import Dict, List

@dataclass
class GateResult:
    name: str
    passed: bool
    severity: str
    margin: float | None
    message: str

    def to_dict(self):
        return asdict(self)


def gate(name: str, passed: bool, severity: str, margin: float | None, message: str) -> GateResult:
    return GateResult(name, bool(passed), severity, margin, message)


def evaluate_gates(summary: Dict, evidence_errors: List[str] | None = None) -> List[GateResult]:
    evidence_errors = evidence_errors or []
    gates: List[GateResult] = []
    gates.append(gate("dimensional", all(v >= 0 for v in [summary.get("energy_MWh", 0), summary.get("water_withdrawal_m3", 0), summary.get("good_die", 0)]), "error", None, "Key extensive outputs must be non-negative."))
    hmargin = float(summary.get("minimum_heat_rejection_margin_MW", 0.0))
    gates.append(gate("thermodynamic_heat_rejection", hmargin >= 0, "error", hmargin, "Heat-rejection capacity must cover first-law heat load."))
    pmargin = float(summary.get("minimum_firm_capacity_margin_MW", 0.0))
    gates.append(gate("power_firm_capacity", pmargin >= 0, "error", pmargin, "Firm capacity must cover site load plus reserve margin."))
    wmargin = float(summary.get("minimum_water_withdrawal_margin_m3_per_day", 0.0))
    gates.append(gate("water_withdrawal_permit", wmargin >= 0, "error", wmargin, "Daily withdrawal must remain within permit capacity."))
    dmargin = float(summary.get("minimum_wastewater_discharge_margin_m3_per_day", 0.0))
    gates.append(gate("wastewater_discharge_permit", dmargin >= 0, "warning", dmargin, "Daily wastewater discharge should remain within permit capacity."))
    y = float(summary.get("average_effective_yield", 0.0))
    gates.append(gate("manufacturing_yield", 0 <= y <= 1 and y > 0, "error", y, "Effective yield must be finite and within (0,1]."))
    cpg = summary.get("cost_per_good_die_USD", float("inf"))
    gates.append(gate("economic_finiteness", isfinite(float(cpg)) and float(cpg) >= 0, "error", None if not isfinite(float(cpg)) else float(cpg), "Cost per good die must be finite and non-negative."))
    lm = float(summary.get("legitimacy_margin", 0.0))
    gates.append(gate("policy_legitimacy", lm >= -0.25, "warning", lm, "Public burden should not overwhelm modeled benefit."))
    gr = float(summary.get("maximum_governance_risk_index", 0.0))
    gates.append(gate("governance_risk", gr <= 0.75, "warning", 0.75 - gr, "Governance complexity should remain below high-risk threshold."))
    gates.append(gate("evidence", len(evidence_errors) == 0, "error", None, "Evidence-coded verified facts must have sources and valid statuses." if evidence_errors else "Evidence status audit passed."))
    return gates


def overall_passed(gates: List[GateResult]) -> bool:
    return not any((not g.passed and g.severity == "error") for g in gates)
