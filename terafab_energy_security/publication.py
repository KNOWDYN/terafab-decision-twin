"""Build the prespecified ECM publication-results bundle."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Mapping

from .evidence import FrozenEvidence
from .exports import write_json, write_scenario_outputs
from .pathways import load_scenario_config, run_scenario_matrix
from .publication_figures import FIGURE_TITLES, build_publication_figures
from .publication_tables import TABLE_FILENAMES, build_publication_tables
from .uncertainty import (
    correlation_stress_test,
    dependence_aware_sensitivity,
    independent_sobol_sensitivity,
    load_uncertainty_contract,
)


FIGURE_STATUS = {
    "figure_01": ("generated", "Product output and factory load are explicitly separated."),
    "figure_02": ("generated_limited_requirement_surface", "Evidence-supported parameter ranges are distinguished from extrapolation, but no project wafer capacity exists to draw a pass/fail feasibility boundary."),
    "figure_03": ("replacement_limited_diagnostic", "The independent-validation threshold is not met; assumption ranges and public comparators are shown without accuracy claims."),
    "figure_04": ("generated", "Conditional full-target trajectories only; research and first-phase scales remain unknown."),
    "figure_05": ("generated_with_omission", "Recoverable heat is not quantified because useful-temperature and sink evidence are unavailable."),
    "figure_06": ("generated_limited_horizon", "Official protocol/SB6 counterfactuals are available only through 2030; reserve margin remains screening-only."),
    "figure_07": ("replacement_screening_only", "LOLE and expected unserved energy cannot be constructed; accredited-capacity and reserve-margin screening is shown instead."),
    "figure_08": ("replacement_context_only", "National peak, fuel demand, and operational emissions are unavailable; only EIA annual-electricity share is shown."),
    "figure_09": ("generated", "Failure and indeterminate statuses use distinct categories; unknown target scales remain indeterminate."),
    "figure_10": ("generated_diagnostic_only", "Sensitivity is for conditional facility peak and cannot substitute for H4's unidentifiable joint-feasibility outcome."),
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _uncertainty_report(contract: Mapping[str, Any], mode: str) -> dict[str, Any]:
    if mode == "final":
        preliminary = int(contract["sampling"]["preliminary_sample_count"])
        confirmation = int(contract["sampling"]["confirmation_sample_count"])
        sensitivity_samples = 4096
        bootstrap = int(contract["sensitivity"]["bootstrap_replicates"])
    elif mode == "quick":
        preliminary, confirmation, sensitivity_samples, bootstrap = 512, 1024, 512, 100
    elif mode == "test":
        preliminary, confirmation, sensitivity_samples, bootstrap = 64, 128, 128, 10
    else:
        raise ValueError("mode must be 'test', 'quick', or 'final'")
    return {
        "mode": mode,
        "correlation_stress": correlation_stress_test(
            contract,
            preliminary_count=preliminary,
            confirmation_count=confirmation,
        ),
        "independent_sobol": independent_sobol_sensitivity(
            contract,
            base_sample_count=sensitivity_samples,
            bootstrap_replicates=bootstrap,
        ),
        "dependence_aware": dependence_aware_sensitivity(
            contract,
            sample_count=sensitivity_samples,
            bootstrap_replicates=bootstrap,
        ),
    }


def _artifact_entry(path: Path, output: Path) -> dict[str, Any]:
    return {
        "path": path.relative_to(output).as_posix(),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
    }


def build_publication_bundle(
    study_root: str | Path,
    output_directory: str | Path,
    *,
    mode: str = "quick",
) -> dict[str, Any]:
    """Generate all prespecified result tables, figures, and integrity records."""
    study = Path(study_root).resolve()
    output = Path(output_directory).resolve()
    output.mkdir(parents=True, exist_ok=True)
    evidence = FrozenEvidence.load(study)
    config_path = study / "scenarios" / "scenario_matrix.json"
    config = load_scenario_config(config_path)
    contract_path = study / "evidence" / "uncertainty_dependencies.json"
    uncertainty_contract = load_uncertainty_contract(contract_path)

    scenario_result = run_scenario_matrix(config, evidence)
    uncertainty_report = _uncertainty_report(uncertainty_contract, mode)

    raw_directory = output / "raw"
    scenario_files = write_scenario_outputs(raw_directory / "scenarios", scenario_result)
    uncertainty_file = write_json(raw_directory / "uncertainty_report.json", uncertainty_report)
    hypothesis_file = write_json(raw_directory / "hypothesis_disposition.json", {
        "H1": "indeterminate_missing_joint_gate_evidence",
        "H2": "indeterminate_missing_official_probabilistic_ercot_metrics",
        "H3": "indeterminate_missing_hourly_adequacy_or_accredited_capacity_evidence",
        "H4": "indeterminate_locked_outcome_unidentifiable",
    })
    tables = build_publication_tables(
        study, output / "tables", config, evidence, scenario_result, uncertainty_report,
    )
    figures = build_publication_figures(
        output / "figures", config, evidence, scenario_result, uncertainty_report,
    )

    figure_records = []
    for figure_id in sorted(figures):
        status, limitation = FIGURE_STATUS[figure_id]
        figure_records.append({
            "figure_id": figure_id,
            "title": FIGURE_TITLES[figure_id],
            "status": status,
            "limitation_or_replacement_reason": limitation,
            "artifacts": {kind: _artifact_entry(path, output) for kind, path in figures[figure_id].items()},
        })
    table_records = [
        {
            "table_id": table_id,
            "required_filename": TABLE_FILENAMES[table_id],
            "status": "generated",
            "artifact": _artifact_entry(tables[table_id], output),
        }
        for table_id in sorted(tables)
    ]
    other_files = [*scenario_files, uncertainty_file, hypothesis_file]
    manifest = {
        "study_id": config["study_id"],
        "bundle_mode": mode,
        "claim_level": "prospective_conditional_constraint_analysis",
        "prohibited_claim": "validated_digital_twin_of_Terafab",
        "source_available_notice": "Noncommercial academic use is governed by ACADEMIC_LICENSE.md; commercial use requires a separate license.",
        "non_affiliation": "Independent KNOWDYN analysis; no Terafab affiliation, endorsement, authorization, or verified operating data.",
        "scenario_manifest": scenario_result["manifest"],
        "hypothesis_disposition": {
            "H1": "indeterminate", "H2": "indeterminate", "H3": "indeterminate", "H4": "indeterminate",
        },
        "figures": figure_records,
        "tables": table_records,
        "supplementary_artifacts": [_artifact_entry(path, output) for path in other_files],
        "input_hashes": {
            "scenario_config_sha256": _sha256(config_path),
            "uncertainty_contract_sha256": _sha256(contract_path),
            "frozen_snapshot_manifest_sha256": _sha256(study / "evidence" / "snapshot_manifest.json"),
            "source_registry_sha256": _sha256(study / "evidence" / "source_registry.json"),
        },
        "output_integrity": {
            "prespecified_figure_count": 10,
            "generated_figure_count": len(figures),
            "figure_data_file_count": sum("data" in artifacts for artifacts in figures.values()),
            "prespecified_table_count": 6,
            "generated_table_count": len(tables),
            "every_figure_has_machine_readable_data": all("data" in artifacts for artifacts in figures.values()),
            "figure_replacements_are_declared": all(record["status"] and record["limitation_or_replacement_reason"] for record in figure_records),
            "live_web_retrieval": False,
        },
        "reproduction": {
            "cli": (
                "python -m terafab_energy_security build-publication "
                "studies/ecm_terafab_energy_security "
                f"--mode {mode} --output-directory OUTPUT_DIRECTORY"
            ),
            "notebook": "studies/ecm_terafab_energy_security/notebooks/terafab_energy_security_ecm.ipynb",
        },
    }
    manifest_path = write_json(output / "publication_manifest.json", manifest)
    return {**manifest, "manifest_path": str(manifest_path)}
