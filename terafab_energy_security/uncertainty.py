"""Reproducible uncertainty and sensitivity analysis for resource requirements.

The routines in this module quantify conditional manufacturing and facility
requirements.  They deliberately do not manufacture a feasibility probability
when required capacity or probabilistic adequacy evidence is unavailable.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping


PARAMETER_IDS = (
    "P_MODULE_RATED_POWER",
    "P_DIE_AREA",
    "P_EFFECTIVE_YIELD",
    "P_LOGIC_DIES_PER_MODULE",
    "P_FAB_ELECTRICITY_INTENSITY",
    "P_FAB_LOAD_FACTOR",
    "P_COOLING_COP",
    "P_TOTAL_WATER_INTENSITY",
    "P_UPW_INTENSITY",
    "P_WATER_RECYCLING",
)

RESOURCE_OUTPUTS = (
    "wafer_starts_per_year",
    "facility_electricity_MWh",
    "facility_peak_MW",
    "water_withdrawal_m3",
)


def load_uncertainty_contract(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as stream:
        contract = json.load(stream)
    validate_uncertainty_contract(contract)
    return contract


def validate_uncertainty_contract(contract: Mapping[str, Any]) -> None:
    distributions = contract["distributions"]
    if tuple(item["parameter_id"] for item in distributions) != PARAMETER_IDS:
        raise ValueError("uncertainty parameters or locked order changed")
    sampling = contract["sampling"]
    if sampling["method"] != "scrambled_sobol_qmc" or int(sampling["seed"]) != 20260801:
        raise ValueError("locked sampling method or seed changed")
    for key in ("preliminary_sample_count", "confirmation_sample_count"):
        value = int(sampling[key])
        if value <= 0 or value & (value - 1):
            raise ValueError(f"{key} must be a positive power of two")
    if int(sampling["confirmation_sample_count"]) != 2 * int(sampling["preliminary_sample_count"]):
        raise ValueError("confirmation sample must double the preliminary sample")
    if contract["dependence_model"]["method"] != "gaussian_copula_with_spearman_to_latent_pearson_transform":
        raise ValueError("dependence method changed")


def _scientific_stack() -> tuple[Any, Any, Any]:
    try:
        import numpy as np
        from scipy import stats
        from scipy.stats import qmc
    except ImportError as exc:  # pragma: no cover - exercised by packaging environments
        raise RuntimeError("uncertainty analysis requires the optional 'study' dependencies") from exc
    return np, stats, qmc


def _nearest_correlation(matrix: Any, np: Any) -> Any:
    symmetric = (matrix + matrix.T) / 2.0
    values, vectors = np.linalg.eigh(symmetric)
    clipped = vectors @ np.diag(np.maximum(values, 1e-10)) @ vectors.T
    scale = np.sqrt(np.diag(clipped))
    corrected = clipped / np.outer(scale, scale)
    np.fill_diagonal(corrected, 1.0)
    return corrected


def _copula_uniforms(
    base_uniforms: Any,
    contract: Mapping[str, Any],
    dependence: str,
    correlation_shift: float,
    np: Any,
    stats: Any,
) -> tuple[Any, Any]:
    dimension = len(PARAMETER_IDS)
    spearman = np.eye(dimension)
    if dependence == "correlated":
        index = {name: position for position, name in enumerate(PARAMETER_IDS)}
        for item in contract["dependence_model"]["correlations"]:
            value = float(item["rho"])
            if value:
                direction = 1.0 if value > 0.0 else -1.0
                value = float(np.clip(value + correlation_shift * direction, -0.99, 0.99))
            a = index[item["parameter_a"]]
            b = index[item["parameter_b"]]
            spearman[a, b] = spearman[b, a] = value
    elif dependence != "independent":
        raise ValueError("dependence must be 'correlated' or 'independent'")

    latent = 2.0 * np.sin(np.pi * spearman / 6.0)
    np.fill_diagonal(latent, 1.0)
    latent = _nearest_correlation(latent, np)
    if dependence == "independent":
        return base_uniforms, latent
    clipped_uniforms = np.clip(base_uniforms, np.finfo(float).eps, 1.0 - np.finfo(float).eps)
    normal = stats.norm.ppf(clipped_uniforms)
    correlated_normal = normal @ np.linalg.cholesky(latent).T
    return stats.norm.cdf(correlated_normal), latent


def _map_distribution(uniform: Any, specification: Mapping[str, Any], np: Any, stats: Any) -> Any:
    family = specification["family"]
    minimum = specification.get("minimum")
    maximum = specification.get("maximum")
    if family == "triangular":
        mode = float(specification["mode"])
        width = float(maximum) - float(minimum)
        return stats.triang.ppf(uniform, (mode - float(minimum)) / width, loc=float(minimum), scale=width)
    if family == "scaled_beta_pert":
        mode = float(specification["mode"])
        shape = float(specification["shape"])
        width = float(maximum) - float(minimum)
        alpha = 1.0 + shape * (mode - float(minimum)) / width
        beta = 1.0 + shape * (float(maximum) - mode) / width
        return float(minimum) + width * stats.beta.ppf(uniform, alpha, beta)
    if family == "discrete_uniform":
        values = np.asarray(specification["values"], dtype=float)
        return values[np.minimum((uniform * len(values)).astype(int), len(values) - 1)]
    if family == "loguniform":
        return np.exp(math.log(float(minimum)) + uniform * math.log(float(maximum) / float(minimum)))
    raise ValueError(f"unsupported distribution family: {family}")


def generate_samples(
    contract: Mapping[str, Any],
    sample_count: int,
    *,
    dependence: str = "correlated",
    correlation_shift: float = 0.0,
    seed: int | None = None,
) -> dict[str, Any]:
    """Generate a scrambled Sobol design and map it through locked marginals."""
    validate_uncertainty_contract(contract)
    if sample_count <= 0 or sample_count & (sample_count - 1):
        raise ValueError("sample_count must be a positive power of two")
    np, stats, qmc = _scientific_stack()
    actual_seed = int(contract["sampling"]["seed"] if seed is None else seed)
    sampler = qmc.Sobol(d=len(PARAMETER_IDS), scramble=True, seed=actual_seed)
    uniforms = sampler.random_base2(int(math.log2(sample_count)))
    uniforms, latent = _copula_uniforms(
        uniforms, contract, dependence, correlation_shift, np, stats,
    )
    columns = [
        _map_distribution(uniforms[:, position], specification, np, stats)
        for position, specification in enumerate(contract["distributions"])
    ]
    return {
        "parameter_ids": PARAMETER_IDS,
        "values": np.column_stack(columns),
        "latent_correlation": latent,
        "sample_count": sample_count,
        "seed": actual_seed,
        "dependence": dependence,
        "correlation_shift": correlation_shift,
    }


def evaluate_resource_samples(
    sample_design: Mapping[str, Any],
    *,
    public_target_W_per_year: float = 1e12,
    target_fraction: float = 1.0,
    wafer_diameter_mm: float = 300.0,
    coincident_peak_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Vectorized counterpart of the deterministic resource equations."""
    np, _, _ = _scientific_stack()
    values = np.asarray(sample_design["values"], dtype=float)
    if values.ndim != 2 or values.shape[1] != len(PARAMETER_IDS):
        raise ValueError("sample design has the wrong dimension")
    parameter = {name: values[:, index] for index, name in enumerate(PARAMETER_IDS)}
    diameter = float(wafer_diameter_mm)
    die_area = parameter["P_DIE_AREA"]
    gross_dies = np.pi * diameter * diameter / (4.0 * die_area) - np.pi * diameter / np.sqrt(2.0 * die_area)
    modules = float(public_target_W_per_year) * float(target_fraction) / parameter["P_MODULE_RATED_POWER"]
    good_dies = modules * parameter["P_LOGIC_DIES_PER_MODULE"]
    wafer_starts = good_dies / (gross_dies * parameter["P_EFFECTIVE_YIELD"])
    electricity = wafer_starts * parameter["P_FAB_ELECTRICITY_INTENSITY"] / 1000.0
    peak = electricity / 8766.0 / parameter["P_FAB_LOAD_FACTOR"] * float(coincident_peak_multiplier)
    withdrawal = wafer_starts * parameter["P_TOTAL_WATER_INTENSITY"]
    return {
        "wafer_starts_per_year": wafer_starts,
        "facility_electricity_MWh": electricity,
        "facility_peak_MW": peak,
        "water_withdrawal_m3": withdrawal,
        "upw_not_greater_than_total_water": parameter["P_UPW_INTENSITY"] <= parameter["P_TOTAL_WATER_INTENSITY"],
        "parameter_values": values,
    }


def summarize_resource_samples(outputs: Mapping[str, Any]) -> dict[str, Any]:
    np, _, _ = _scientific_stack()
    return {
        "wafer_starts_per_year_median": float(np.median(outputs["wafer_starts_per_year"])),
        "facility_electricity_MWh_median": float(np.median(outputs["facility_electricity_MWh"])),
        "facility_peak_MW_p95": float(np.quantile(outputs["facility_peak_MW"], 0.95)),
        "water_withdrawal_m3_p95": float(np.quantile(outputs["water_withdrawal_m3"], 0.95)),
        "physical_water_identity_pass_fraction": float(np.mean(outputs["upw_not_greater_than_total_water"])),
        "feasibility_probability": None,
        "feasibility_probability_status": "indeterminate_missing_required_capacity_and_probabilistic_adequacy_evidence",
    }


def convergence_diagnostic(
    contract: Mapping[str, Any],
    *,
    preliminary_count: int | None = None,
    confirmation_count: int | None = None,
    dependence: str = "correlated",
    correlation_shift: float = 0.0,
) -> dict[str, Any]:
    """Apply the locked doubling rule to estimable resource outputs."""
    validate_uncertainty_contract(contract)
    sampling = contract["sampling"]
    preliminary = int(preliminary_count or sampling["preliminary_sample_count"])
    confirmation = int(confirmation_count or sampling["confirmation_sample_count"])
    if confirmation != 2 * preliminary:
        raise ValueError("confirmation_count must double preliminary_count")
    design = generate_samples(
        contract, confirmation, dependence=dependence,
        correlation_shift=correlation_shift,
    )
    full_outputs = evaluate_resource_samples(design)
    preliminary_outputs = {
        key: value[:preliminary] if hasattr(value, "__len__") else value
        for key, value in full_outputs.items()
        if key != "parameter_values"
    }
    preliminary_summary = summarize_resource_samples(preliminary_outputs)
    confirmation_summary = summarize_resource_samples(full_outputs)
    estimable = [name for name in sampling["convergence_outputs"] if name != "feasibility_probability"]
    relative_changes = {
        name: abs(confirmation_summary[name] - preliminary_summary[name])
        / max(abs(confirmation_summary[name]), 1e-30)
        for name in estimable
    }
    limit = float(sampling["doubling_convergence_relative_change_max"])
    return {
        "preliminary_sample_count": preliminary,
        "confirmation_sample_count": confirmation,
        "dependence": dependence,
        "correlation_shift": correlation_shift,
        "preliminary": preliminary_summary,
        "confirmation": confirmation_summary,
        "relative_changes": relative_changes,
        "convergence_limit": limit,
        "estimable_outputs_pass": all(value < limit for value in relative_changes.values()),
        "feasibility_probability_convergence": "not_evaluable",
    }


def correlation_stress_test(
    contract: Mapping[str, Any],
    *,
    preliminary_count: int | None = None,
    confirmation_count: int | None = None,
) -> list[dict[str, Any]]:
    cases = (("independent", 0.0), ("correlated", -0.20), ("correlated", 0.0), ("correlated", 0.20))
    return [
        convergence_diagnostic(
            contract,
            preliminary_count=preliminary_count,
            confirmation_count=confirmation_count,
            dependence=dependence,
            correlation_shift=shift,
        )
        for dependence, shift in cases
    ]


def _independent_marginal_values(uniforms: Any, contract: Mapping[str, Any], np: Any, stats: Any) -> Any:
    return np.column_stack([
        _map_distribution(uniforms[:, position], item, np, stats)
        for position, item in enumerate(contract["distributions"])
    ])


def _peak_from_values(values: Any, np: Any) -> Any:
    die_area = values[:, 1]
    gross_dies = np.pi * 300.0**2 / (4.0 * die_area) - np.pi * 300.0 / np.sqrt(2.0 * die_area)
    wafers = (1e12 / values[:, 0]) * values[:, 3] / (gross_dies * values[:, 2])
    electricity = wafers * values[:, 4] / 1000.0
    return electricity / 8766.0 / values[:, 5]


def independent_sobol_sensitivity(
    contract: Mapping[str, Any],
    *,
    base_sample_count: int = 4096,
    bootstrap_replicates: int | None = None,
) -> dict[str, Any]:
    """Independent-marginal Sobol diagnostic for conditional facility peak."""
    validate_uncertainty_contract(contract)
    if base_sample_count <= 0 or base_sample_count & (base_sample_count - 1):
        raise ValueError("base_sample_count must be a positive power of two")
    np, stats, qmc = _scientific_stack()
    d = len(PARAMETER_IDS)
    seed = int(contract["sampling"]["seed"])
    sampler = qmc.Sobol(d=2 * d, scramble=True, seed=seed + 41)
    uniforms = sampler.random_base2(int(math.log2(base_sample_count)))
    a = _independent_marginal_values(uniforms[:, :d], contract, np, stats)
    b = _independent_marginal_values(uniforms[:, d:], contract, np, stats)
    fa = np.log10(_peak_from_values(a, np))
    fb = np.log10(_peak_from_values(b, np))
    variance = float(np.var(np.concatenate([fa, fb]), ddof=1))
    first_terms = np.empty((base_sample_count, d))
    total_terms = np.empty((base_sample_count, d))
    for index in range(d):
        ab = a.copy()
        ab[:, index] = b[:, index]
        fab = np.log10(_peak_from_values(ab, np))
        first_terms[:, index] = fb * (fab - fa)
        total_terms[:, index] = 0.5 * (fa - fab) ** 2
    first = np.mean(first_terms, axis=0) / variance
    total = np.mean(total_terms, axis=0) / variance

    bootstrap_count = int(
        contract["sensitivity"]["bootstrap_replicates"]
        if bootstrap_replicates is None else bootstrap_replicates
    )
    rng = np.random.default_rng(seed + 42)
    boot_total = np.empty((bootstrap_count, d))
    for replicate in range(bootstrap_count):
        indices = rng.integers(0, base_sample_count, base_sample_count)
        boot_total[replicate] = np.mean(total_terms[indices], axis=0) / variance
    base_order = np.argsort(-total)
    base_ranks = np.empty(d, dtype=float)
    base_ranks[base_order] = np.arange(d)
    correlations = np.empty(bootstrap_count)
    top_count = max(1, math.ceil(float(contract["sensitivity"]["h4_top_fraction"]) * d))
    base_top = set(base_order[:top_count])
    inclusion = {index: 0 for index in base_top}
    for replicate in range(bootstrap_count):
        order = np.argsort(-boot_total[replicate])
        ranks = np.empty(d, dtype=float)
        ranks[order] = np.arange(d)
        correlations[replicate] = float(stats.spearmanr(base_ranks, ranks).statistic)
        selected = set(order[:top_count])
        for index in base_top:
            inclusion[index] += int(index in selected)
    normalized = np.maximum(total, 0.0)
    normalized = normalized / normalized.sum()
    top_mass = float(normalized[base_order[:top_count]].sum())
    inclusion_frequencies = {PARAMETER_IDS[index]: count / bootstrap_count for index, count in inclusion.items()}
    rank_rule = contract["sensitivity"]["rank_stability"]
    stability = {
        "top_set_inclusion_frequency_min": min(inclusion_frequencies.values()),
        "median_spearman_rank_correlation": float(np.median(correlations)),
        "fifth_percentile_spearman_rank_correlation": float(np.quantile(correlations, 0.05)),
    }
    stability_pass = (
        stability["top_set_inclusion_frequency_min"] >= float(rank_rule["top_set_inclusion_frequency_min"])
        and stability["median_spearman_rank_correlation"] >= float(rank_rule["median_spearman_rank_correlation_min"])
        and stability["fifth_percentile_spearman_rank_correlation"] >= float(rank_rule["fifth_percentile_spearman_rank_correlation_min"])
    )
    concentration_pass = top_mass >= float(contract["sensitivity"]["h4_required_total_order_mass"])
    rows = []
    for index, parameter_id in enumerate(PARAMETER_IDS):
        rows.append({
            "parameter_id": parameter_id,
            "first_order": float(first[index]),
            "total_order": float(total[index]),
            "normalized_total_order_mass": float(normalized[index]),
            "total_order_ci95_low": float(np.quantile(boot_total[:, index], 0.025)),
            "total_order_ci95_high": float(np.quantile(boot_total[:, index], 0.975)),
            "rank": int(np.where(base_order == index)[0][0]) + 1,
        })
    return {
        "outcome": "log10_facility_peak_MW",
        "scope": "conditional_resource_requirement_diagnostic",
        "base_sample_count": base_sample_count,
        "bootstrap_replicates": bootstrap_count,
        "indices": rows,
        "top_parameter_count": top_count,
        "top_normalized_total_order_mass": top_mass,
        "rank_stability": stability,
        "rank_stability_pass": stability_pass,
        "diagnostic_concentration_pass": concentration_pass and stability_pass,
        "H4_status": "indeterminate",
        "H4_reason": "The locked H4 outcome is realization year or joint feasibility; required feasibility evidence is unavailable, so resource-peak sensitivity cannot substitute for it.",
    }


def _subset_r2(correlation: Any, response_correlation: Any, subset: tuple[int, ...], np: Any) -> float:
    if not subset:
        return 0.0
    indices = np.asarray(subset, dtype=int)
    matrix = correlation[np.ix_(indices, indices)]
    vector = response_correlation[indices]
    value = float(vector @ np.linalg.pinv(matrix, rcond=1e-10) @ vector)
    return min(1.0, max(0.0, value))


def _exact_linear_shapley(values: Any, response: Any, np: Any) -> tuple[Any, float]:
    d = values.shape[1]
    standardized = (values - np.mean(values, axis=0)) / np.std(values, axis=0, ddof=1)
    y = (response - np.mean(response)) / np.std(response, ddof=1)
    joint = np.corrcoef(np.column_stack([standardized, y]), rowvar=False)
    correlation = joint[:d, :d]
    response_correlation = joint[:d, d]
    cache: dict[tuple[int, ...], float] = {}
    for size in range(d + 1):
        for subset in itertools.combinations(range(d), size):
            cache[subset] = _subset_r2(correlation, response_correlation, subset, np)
    effects = np.zeros(d)
    for index in range(d):
        others = [item for item in range(d) if item != index]
        for size in range(d):
            weight = 1.0 / d / math.comb(d - 1, size)
            for subset in itertools.combinations(others, size):
                expanded = tuple(sorted((*subset, index)))
                effects[index] += weight * (cache[expanded] - cache[tuple(sorted(subset))])
    total_r2 = cache[tuple(range(d))]
    if effects.sum() > 0:
        effects = effects / effects.sum()
    return effects, total_r2


def dependence_aware_sensitivity(
    contract: Mapping[str, Any],
    *,
    sample_count: int = 4096,
    bootstrap_replicates: int | None = None,
) -> dict[str, Any]:
    """Gaussian-copula, dependence-aware linear-surrogate Shapley allocation."""
    np, _, _ = _scientific_stack()
    design = generate_samples(contract, sample_count, dependence="correlated")
    values = design["values"]
    response = np.log10(_peak_from_values(values, np))
    effects, r2 = _exact_linear_shapley(values, response, np)
    bootstrap_count = int(
        contract["sensitivity"]["bootstrap_replicates"]
        if bootstrap_replicates is None else bootstrap_replicates
    )
    rng = np.random.default_rng(int(contract["sampling"]["seed"]) + 43)
    boot = np.empty((bootstrap_count, len(PARAMETER_IDS)))
    for replicate in range(bootstrap_count):
        indices = rng.integers(0, sample_count, sample_count)
        boot[replicate], _ = _exact_linear_shapley(values[indices], response[indices], np)
    order = np.argsort(-effects)
    rows = []
    for index, parameter_id in enumerate(PARAMETER_IDS):
        rows.append({
            "parameter_id": parameter_id,
            "shapley_effect": float(effects[index]),
            "shapley_ci95_low": float(np.quantile(boot[:, index], 0.025)),
            "shapley_ci95_high": float(np.quantile(boot[:, index], 0.975)),
            "rank": int(np.where(order == index)[0][0]) + 1,
        })
    return {
        "outcome": "log10_facility_peak_MW",
        "scope": "conditional_resource_requirement_diagnostic",
        "method": "exact_conditional_variance_shapley_for_linear_surrogate",
        "sample_count": sample_count,
        "bootstrap_replicates": bootstrap_count,
        "surrogate_R2": float(r2),
        "effects": rows,
        "H4_status": "not_applicable_to_correlated_design",
    }
