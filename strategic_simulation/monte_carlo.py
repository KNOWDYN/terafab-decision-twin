from __future__ import annotations

import copy
import math
import random
import statistics
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence

from terafab_decision_twin.engine import run_scenario
from terafab_decision_twin.schema import load_scenario, validate_scenario

DEFAULT_METRICS = [
    "minimum_firm_capacity_margin_MW",
    "minimum_heat_rejection_margin_MW",
    "minimum_water_withdrawal_margin_m3_per_day",
    "minimum_wastewater_discharge_margin_m3_per_day",
    "average_effective_yield",
    "average_readiness_index",
    "total_cost_USD",
    "cost_per_good_die_USD",
    "cost_per_compute_watt_USD",
    "emissions_tCO2",
    "legitimacy_margin",
    "maximum_governance_risk_index",
]


def _load_scenario_obj(scenario: str | Path | Mapping[str, Any]) -> Dict[str, Any]:
    if isinstance(scenario, (str, Path)):
        return load_scenario(scenario)
    return copy.deepcopy(dict(scenario))


def _get_path(root: Mapping[str, Any], dotted_path: str) -> Any:
    current: Any = root
    for part in dotted_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise KeyError(f"Path not found: {dotted_path}")
        current = current[part]
    return current


def _set_path(root: MutableMapping[str, Any], dotted_path: str, value: Any, spec: Mapping[str, Any] | None = None) -> None:
    parts = dotted_path.split(".")
    current: Any = root
    for part in parts[:-1]:
        if not isinstance(current, MutableMapping) or part not in current:
            raise KeyError(f"Path not found: {dotted_path}")
        current = current[part]
    leaf = parts[-1]
    if leaf not in current:
        raise KeyError(f"Path not found: {dotted_path}")
    existing = current[leaf]
    if isinstance(existing, MutableMapping) and "value" in existing:
        updated = dict(existing)
        updated["value"] = value
        if spec:
            if spec.get("unit"):
                updated["unit"] = spec["unit"]
            if spec.get("status"):
                updated["status"] = spec["status"]
            if spec.get("source_ref"):
                updated["source_ref"] = spec["source_ref"]
            if spec.get("confidence"):
                updated["confidence"] = spec["confidence"]
        base_note = str(updated.get("notes", "")).strip()
        mc_note = f"Monte Carlo sampled value for {dotted_path}; not a verified operating fact."
        updated["notes"] = (base_note + " " + mc_note).strip() if base_note else mc_note
        current[leaf] = updated
    else:
        current[leaf] = value


def sample_distribution(spec: Mapping[str, Any], rng: random.Random) -> Any:
    """Sample a value from a dependency-free distribution spec.

    Supported distribution names:
    fixed, uniform, triangular, normal_clipped, lognormal, discrete.
    """
    dist = str(spec.get("distribution", "fixed")).lower()
    if dist == "fixed":
        return spec.get("value")
    if dist == "uniform":
        return rng.uniform(float(spec["low"]), float(spec["high"]))
    if dist == "triangular":
        return rng.triangular(float(spec["low"]), float(spec["high"]), float(spec.get("mode", (float(spec["low"]) + float(spec["high"])) / 2.0)))
    if dist == "normal_clipped":
        mean = float(spec["mean"])
        sd = float(spec["sd"])
        low = spec.get("low")
        high = spec.get("high")
        value = rng.gauss(mean, sd)
        if low is not None:
            value = max(float(low), value)
        if high is not None:
            value = min(float(high), value)
        return value
    if dist == "lognormal":
        return rng.lognormvariate(float(spec["mu"]), float(spec["sigma"]))
    if dist == "discrete":
        values = list(spec.get("values", []))
        if not values:
            raise ValueError("discrete distribution requires non-empty values")
        weights = spec.get("weights")
        if weights is None:
            return rng.choice(values)
        if len(weights) != len(values):
            raise ValueError("discrete distribution weights must match values")
        return rng.choices(values, weights=[float(w) for w in weights], k=1)[0]
    raise ValueError(f"Unsupported distribution: {dist}")


def _quantile(values: Sequence[float], q: float) -> float | None:
    clean = sorted(float(v) for v in values if v is not None and math.isfinite(float(v)))
    if not clean:
        return None
    if len(clean) == 1:
        return clean[0]
    pos = (len(clean) - 1) * q
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return clean[lo]
    weight = pos - lo
    return clean[lo] * (1.0 - weight) + clean[hi] * weight


def _metric_quantiles(results: Iterable[Mapping[str, Any]], metrics: Sequence[str]) -> Dict[str, Dict[str, float | None]]:
    out: Dict[str, Dict[str, float | None]] = {}
    for metric in metrics:
        vals: List[float] = []
        for result in results:
            value = result.get("summary", {}).get(metric)
            if isinstance(value, (int, float)) and math.isfinite(value):
                vals.append(float(value))
        out[metric] = {
            "p05": _quantile(vals, 0.05),
            "p10": _quantile(vals, 0.10),
            "p50": _quantile(vals, 0.50),
            "p90": _quantile(vals, 0.90),
            "p95": _quantile(vals, 0.95),
            "mean": statistics.fmean(vals) if vals else None,
        }
    return out


def _pearson(x: Sequence[float], y: Sequence[float]) -> float | None:
    pairs = [(float(a), float(b)) for a, b in zip(x, y) if math.isfinite(float(a)) and math.isfinite(float(b))]
    if len(pairs) < 3:
        return None
    xs, ys = zip(*pairs)
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    dx = [a - mx for a in xs]
    dy = [b - my for b in ys]
    sx = math.sqrt(sum(a * a for a in dx))
    sy = math.sqrt(sum(b * b for b in dy))
    if sx == 0 or sy == 0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / (sx * sy)


def _sensitivity(samples: Sequence[Mapping[str, Any]], results: Sequence[Mapping[str, Any]], target_metric: str) -> List[Dict[str, Any]]:
    target = [r.get("summary", {}).get(target_metric) for r in results]
    ranking: List[Dict[str, Any]] = []
    if not samples:
        return ranking
    for param in samples[0].keys():
        x = [s.get(param) for s in samples]
        if all(isinstance(v, (int, float)) for v in x) and all(isinstance(v, (int, float)) for v in target):
            corr = _pearson([float(v) for v in x], [float(v) for v in target])
            if corr is not None:
                ranking.append({"parameter": param, "target_metric": target_metric, "pearson_correlation": corr, "absolute_correlation": abs(corr)})
    ranking.sort(key=lambda row: row["absolute_correlation"], reverse=True)
    return ranking


def _gate_failure_probabilities(results: Sequence[Mapping[str, Any]]) -> Dict[str, float]:
    counts: Dict[str, int] = {}
    total = len(results)
    if total == 0:
        return {}
    for result in results:
        for gate in result.get("gates", []):
            name = str(gate.get("name"))
            if not gate.get("passed", False):
                counts[name] = counts.get(name, 0) + 1
            else:
                counts.setdefault(name, counts.get(name, 0))
    return {name: count / total for name, count in sorted(counts.items())}


def _compact_run_record(index: int, result: Mapping[str, Any], samples: Mapping[str, Any]) -> Dict[str, Any]:
    summary = result.get("summary", {})
    failed_gates = [g.get("name") for g in result.get("gates", []) if not g.get("passed", False)]
    return {
        "run_index": index,
        "passed": bool(result.get("passed")),
        "samples": dict(samples),
        "failed_gates": failed_gates,
        "summary": {metric: summary.get(metric) for metric in DEFAULT_METRICS if metric in summary},
    }


def run_monte_carlo(
    scenario: str | Path | Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    retain_runs: bool = True,
) -> Dict[str, Any]:
    """Propagate declared uncertainty through the existing deterministic kernel.

    The function does not validate reality. It samples declared distributions,
    preserves evidence status on mutated scenario values, calls
    ``terafab_decision_twin.run_scenario()``, and summarizes the resulting
    distribution of gates and outputs.
    """
    base = _load_scenario_obj(scenario)
    base_errors = validate_scenario(base)
    if base_errors:
        raise ValueError("Base scenario is invalid:\n" + "\n".join(base_errors))
    runs = int(config.get("runs", 100))
    if runs <= 0:
        raise ValueError("Monte Carlo runs must be positive")
    seed = int(config.get("seed", 42))
    rng = random.Random(seed)
    parameters = dict(config.get("parameters", {}))
    if not parameters:
        raise ValueError("Monte Carlo config requires at least one parameter distribution")
    metrics = list(config.get("metrics", DEFAULT_METRICS))
    target_metric = str(config.get("sensitivity_target", "total_cost_USD"))

    full_results: List[Dict[str, Any]] = []
    sample_records: List[Dict[str, Any]] = []
    compact_runs: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []

    for i in range(runs):
        scenario_i = copy.deepcopy(base)
        sample_i: Dict[str, Any] = {}
        for path, spec in parameters.items():
            if not isinstance(spec, Mapping):
                raise ValueError(f"Distribution spec for {path} must be an object")
            _get_path(scenario_i, path)  # explicit path validation before sampling
            value = sample_distribution(spec, rng)
            _set_path(scenario_i, path, value, spec)
            sample_i[path] = value
        result_i = run_scenario(scenario_i)
        full_results.append(result_i)
        sample_records.append(sample_i)
        if retain_runs:
            compact_runs.append(_compact_run_record(i, result_i, sample_i))
        if not result_i.get("passed"):
            failures.append(_compact_run_record(i, result_i, sample_i))

    passed_count = sum(1 for r in full_results if r.get("passed"))
    out: Dict[str, Any] = {
        "kind": "monte_carlo_result",
        "model_boundary": "Declared uncertainty propagation through the existing deterministic decision twin; not official Terafab validation.",
        "runs_requested": runs,
        "runs_completed": len(full_results),
        "seed": seed,
        "parameters": sorted(parameters.keys()),
        "passed_probability": passed_count / len(full_results),
        "failed_probability": 1.0 - passed_count / len(full_results),
        "gate_failure_probability": _gate_failure_probabilities(full_results),
        "metric_quantiles": _metric_quantiles(full_results, metrics),
        "sensitivity": _sensitivity(sample_records, full_results, target_metric),
        "worst_runs": failures[: min(10, len(failures))],
    }
    if retain_runs:
        out["runs"] = compact_runs
    return out
