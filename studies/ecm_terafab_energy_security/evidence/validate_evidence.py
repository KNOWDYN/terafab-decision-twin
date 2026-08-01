#!/usr/bin/env python3
"""Offline integrity checks for the frozen Step 2 evidence foundation."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SNAPSHOTS = ROOT / "snapshots"
ALLOWED_EVIDENCE_STATUSES = {
    "verified_project_fact",
    "model_identity",
    "filed_claimed",
    "reported",
    "user_provided",
    "scenario_assumption",
    "stress_test_assumption",
    "unknown",
    "derived_output",
}


class Checks:
    def __init__(self) -> None:
        self.count = 0
        self.errors: list[str] = []

    def require(self, condition: bool, message: str) -> None:
        self.count += 1
        if not condition:
            self.errors.append(message)


def load_json(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_positive_semidefinite(matrix: list[list[float]], tolerance: float = 1e-12) -> bool:
    """LDL-style check that accepts positive semidefinite matrices."""
    n = len(matrix)
    lower = [[0.0] * n for _ in range(n)]
    diagonal = [0.0] * n
    for i in range(n):
        lower[i][i] = 1.0
        for j in range(i):
            residual = matrix[i][j] - sum(
                lower[i][k] * diagonal[k] * lower[j][k] for k in range(j)
            )
            if abs(diagonal[j]) <= tolerance:
                if abs(residual) > tolerance:
                    return False
                lower[i][j] = 0.0
            else:
                lower[i][j] = residual / diagonal[j]
        diagonal[i] = matrix[i][i] - sum(
            lower[i][k] * lower[i][k] * diagonal[k] for k in range(i)
        )
        if diagonal[i] < -tolerance:
            return False
    return True


def main() -> int:
    checks = Checks()
    sources_doc = load_json(ROOT / "source_registry.json")
    parameters_doc = load_json(ROOT / "parameter_registry.json")
    uncertainty_doc = load_json(ROOT / "uncertainty_dependencies.json")
    validation_doc = load_json(ROOT / "validation_contract.json")
    manifest = load_json(ROOT / "snapshot_manifest.json")

    sources = sources_doc["sources"]
    source_ids = [item["source_id"] for item in sources]
    source_set = set(source_ids)
    checks.require(len(source_ids) == len(source_set), "source IDs must be unique")

    parameters = parameters_doc["parameters"]
    parameter_ids = [item["parameter_id"] for item in parameters]
    parameter_set = set(parameter_ids)
    checks.require(len(parameter_ids) == len(parameter_set), "parameter IDs must be unique")

    for parameter in parameters:
        pid = parameter["parameter_id"]
        checks.require(
            parameter["evidence_status"] in ALLOWED_EVIDENCE_STATUSES,
            f"{pid}: invalid evidence_status",
        )
        checks.require(
            all(source_id in source_set for source_id in parameter.get("source_ids", [])),
            f"{pid}: unknown source reference",
        )
        checks.require(bool(parameter.get("unit")), f"{pid}: unit is required")
        if parameter["evidence_status"] == "unknown":
            checks.require(parameter.get("value") is None, f"{pid}: unknown values must be null")
        if "bounds" in parameter:
            lower, upper = parameter["bounds"]
            checks.require(lower < upper, f"{pid}: bounds must be strictly ordered")
            value = parameter.get("value")
            if isinstance(value, (int, float)):
                checks.require(lower <= value <= upper, f"{pid}: value outside bounds")

    distributions = uncertainty_doc["distributions"]
    distribution_ids = [item["distribution_id"] for item in distributions]
    checks.require(
        len(distribution_ids) == len(set(distribution_ids)),
        "distribution IDs must be unique",
    )
    for distribution in distributions:
        checks.require(
            distribution["parameter_id"] in parameter_set,
            f"{distribution['distribution_id']}: unknown parameter",
        )
    for parameter in parameters:
        if "distribution_id" in parameter:
            checks.require(
                parameter["distribution_id"] in set(distribution_ids),
                f"{parameter['parameter_id']}: unknown distribution",
            )

    correlated_ids = sorted(
        {
            item[key]
            for item in uncertainty_doc["dependence_model"]["correlations"]
            for key in ("parameter_a", "parameter_b")
        }
    )
    correlation_matrix = [
        [1.0 if a == b else 0.0 for b in correlated_ids] for a in correlated_ids
    ]
    index = {parameter_id: position for position, parameter_id in enumerate(correlated_ids)}
    for relation in uncertainty_doc["dependence_model"]["correlations"]:
        a, b, rho = relation["parameter_a"], relation["parameter_b"], relation["rho"]
        checks.require(a in parameter_set and b in parameter_set, "correlation has unknown parameter")
        checks.require(-1.0 <= rho <= 1.0, f"correlation {a}/{b} is outside [-1, 1]")
        correlation_matrix[index[a]][index[b]] = rho
        correlation_matrix[index[b]][index[a]] = rho
    checks.require(
        is_positive_semidefinite(correlation_matrix),
        "declared rank-correlation matrix is not positive semidefinite",
    )
    latent_matrix = [
        [
            1.0 if row == column else 2.0 * math.sin(math.pi * correlation_matrix[row][column] / 6.0)
            for column in range(len(correlated_ids))
        ]
        for row in range(len(correlated_ids))
    ]
    checks.require(
        is_positive_semidefinite(latent_matrix),
        "Spearman-to-Gaussian latent correlation matrix is not positive semidefinite",
    )

    required_sources = {
        "SRC_PUCT_25_508",
        "SRC_PUCT_MAGNITUDE_2026",
        "SRC_ERCOT_CDR_2025_12",
        "SRC_EIA_AEO2026_TABLE8_CB",
        "SRC_EIA_AEO2026_TABLE8_HIGH",
        "SRC_EIA_AEO2026_EMM_TABLE3",
    }
    checks.require(required_sources <= source_set, "official baseline sources are incomplete")

    admissible = {item["source_id"]: set(item["admissibility"]) for item in sources}
    checks.require(
        sum("validation" in roles for roles in admissible.values()) >= 2,
        "at least two independent validation sources are required",
    )
    checks.require(
        any("cooling_reference" in roles or "component_validation" in roles for roles in admissible.values()),
        "a cooling or component benchmark is required",
    )
    checks.require(
        any("water_reference" in roles for roles in admissible.values()),
        "a water benchmark is required",
    )
    checks.require(
        "SRC_ASML_NXE3400B" in source_set and "SRC_TSMC_GIGAFAB_2025" in source_set,
        "tool and industry throughput comparators are required",
    )

    target = next(item for item in parameters if item["parameter_id"] == "P_TARGET_RATED_OUTPUT")
    facility_load = next(item for item in parameters if item["parameter_id"] == "P_PROJECT_FACILITY_LOAD")
    checks.require(target["unit"] == "W_rated/year", "target must retain W_rated/year")
    checks.require(
        facility_load["value"] is None,
        "facility load must remain unknown; do not substitute the 1 TW/year target",
    )
    checks.require(
        target.get("prohibited_use") == "facility_electric_load",
        "target-to-load prohibition must be machine readable",
    )

    schedule = load_json(SNAPSHOTS / "terafab_public_schedule.json")
    phases = schedule["phases"]
    checks.require([item["phase"] for item in phases] == [1, 2, 3, 4], "phase order is invalid")
    for phase in phases:
        checks.require(
            phase["construction_start_year"] <= phase["construction_end_year"]
            < phase["first_incentive_or_operations_year"],
            f"phase {phase['phase']}: construction must precede operations",
        )
        checks.require(
            phase["facility_electric_load_MW"] is None,
            f"phase {phase['phase']}: filed load must remain null",
        )

    ercot = load_json(SNAPSHOTS / "ercot_adequacy.json")
    standard = ercot["regulatory_standard"]
    checks.require(standard["frequency"]["threshold"] == 0.1, "LOLE threshold changed")
    checks.require(standard["duration"]["threshold"] == 12, "duration threshold changed")
    checks.require(standard["magnitude"]["annual_update_required"], "magnitude must be annual")
    prescribed = ercot["cdr_december_2025"]["protocol_prescribed"]
    checks.require([row["year"] for row in prescribed] == list(range(2026, 2031)), "CDR years invalid")
    checks.require(
        len(ercot["cdr_december_2025"]["sb6_base_case_peak_load_hour_PRM_fraction"])
        == len(prescribed),
        "both CDR baselines must be retained",
    )

    aeo = load_json(SNAPSHOTS / "aeo2026_national_electricity.json")
    baseline = aeo["cases"]["counterfactual_baseline"]["series"]
    high = aeo["cases"]["high_electricity_demand"]["series"]
    years = list(range(2025, 2051))
    checks.require([row[0] for row in baseline] == years, "AEO baseline years invalid")
    checks.require([row[0] for row in high] == years, "AEO high-demand years invalid")
    checks.require(
        all(high_row[1] >= base_row[1] for base_row, high_row in zip(baseline, high)),
        "AEO high-demand total use must not be below baseline",
    )

    validation_sources = set(
        validation_doc["calibration_validation_separation"]["external_validation_sources"]
    )
    calibration_sources = set(validation_doc["calibration_validation_separation"]["calibration_sources"])
    checks.require(not (validation_sources & calibration_sources), "calibration and validation sources overlap")
    checks.require(
        validation_doc["claim_level"] == "prospective_constraint_analysis",
        "claim level must remain prospective constraint analysis",
    )
    checks.require(
        validation_doc["empirical_validation_thresholds"]["minimum_independent_numeric_holdouts_for_validated_claim"] >= 5,
        "validated-claim holdout minimum is too small",
    )
    sensitivity = uncertainty_doc["sensitivity"]
    checks.require(
        "independent_marginal" in sensitivity["h4_primary_method"],
        "H4 Sobol design must state the independence condition",
    )
    checks.require(
        "shapley" in sensitivity["dependence_aware_method"],
        "correlated sensitivity requires a dependence-aware allocation",
    )

    manifest_paths = [entry["path"] for entry in manifest["files"]]
    actual_paths = sorted(path.name for path in SNAPSHOTS.glob("*.json"))
    checks.require(sorted(manifest_paths) == actual_paths, "snapshot manifest file set is stale")
    for entry in manifest["files"]:
        path = SNAPSHOTS / entry["path"]
        checks.require(path.exists(), f"manifest file missing: {entry['path']}")
        if path.exists():
            checks.require(sha256(path) == entry["sha256"], f"hash mismatch: {entry['path']}")

    if checks.errors:
        print(f"FAIL: {len(checks.errors)} of {checks.count} evidence checks failed")
        for error in checks.errors:
            print(f"- {error}")
        return 1
    print(
        f"PASS: {checks.count} evidence checks; "
        f"{len(source_ids)} sources, {len(parameter_ids)} parameters, "
        f"{len(actual_paths)} frozen snapshots"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
