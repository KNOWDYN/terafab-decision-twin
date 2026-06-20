from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass(frozen=True)
class BayesianEvidenceUpdate:
    prior_probability: float
    likelihood_if_true: float
    likelihood_if_false: float
    posterior_probability: float
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def bayes_update(prior_probability: float, likelihood_if_true: float, likelihood_if_false: float) -> BayesianEvidenceUpdate:
    p = max(0.0, min(1.0, float(prior_probability)))
    lt = max(0.0, min(1.0, float(likelihood_if_true)))
    lf = max(0.0, min(1.0, float(likelihood_if_false)))
    denom = lt * p + lf * (1.0 - p)
    posterior = p if denom == 0 else (lt * p / denom)
    return BayesianEvidenceUpdate(p, lt, lf, posterior, "reported")


def posterior_to_status(posterior_probability: float, verification_threshold: float = 0.99) -> str:
    """Bayesian confidence never auto-upgrades to verified_project_fact without a primary source."""
    if float(posterior_probability) >= float(verification_threshold):
        return "reported"
    return "scenario_assumption"
