"""Command-line interface for the prospective energy-security overlay."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .engine import run_case
from .evidence import FrozenEvidence
from .exports import write_json, write_scenario_outputs
from .pathways import load_scenario_config, run_scenario_matrix
from .publication import build_publication_bundle
from .uncertainty import (
    correlation_stress_test,
    dependence_aware_sensitivity,
    independent_sobol_sensitivity,
    load_uncertainty_contract,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="terafab-energy-security",
        description="Run evidence-gated Terafab production-to-energy constraint cases.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run one deterministic JSON case")
    run.add_argument("case", type=Path)
    run.add_argument("--output", type=Path)
    run.add_argument("--compact", action="store_true")

    evidence = subparsers.add_parser("validate-evidence", help="Verify the frozen Step 2 evidence foundation")
    evidence.add_argument("study_root", type=Path)

    matrix = subparsers.add_parser("run-matrix", help="Run the frozen 2026-2050 scenario matrix")
    matrix.add_argument("study_root", type=Path)
    matrix.add_argument("--config", type=Path)
    matrix.add_argument("--output-directory", type=Path, required=True)
    matrix.add_argument("--scenario-id", action="append")

    uncertainty = subparsers.add_parser("run-uncertainty", help="Run locked resource uncertainty diagnostics")
    uncertainty.add_argument("study_root", type=Path)
    uncertainty.add_argument("--output", type=Path, required=True)
    uncertainty.add_argument("--mode", choices=("quick", "final"), default="quick")

    publication = subparsers.add_parser("build-publication", help="Build all prespecified ECM figures, tables, and manifests")
    publication.add_argument("study_root", type=Path)
    publication.add_argument("--output-directory", type=Path, required=True)
    publication.add_argument("--mode", choices=("test", "quick", "final"), default="quick")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "validate-evidence":
        evidence = FrozenEvidence.load(args.study_root)
        payload = {
            "status": "pass",
            "sources": len(evidence.sources),
            "parameters": len(evidence.parameters),
            "snapshots": len(evidence.snapshot_hashes),
        }
    elif args.command == "run-matrix":
        evidence = FrozenEvidence.load(args.study_root)
        config_path = args.config or args.study_root / "scenarios" / "scenario_matrix.json"
        config = load_scenario_config(config_path)
        result = run_scenario_matrix(config, evidence, args.scenario_id)
        outputs = write_scenario_outputs(args.output_directory, result)
        payload = {"status": "pass", "manifest": result["manifest"], "outputs": [str(path) for path in outputs]}
    elif args.command == "run-uncertainty":
        contract = load_uncertainty_contract(args.study_root / "evidence" / "uncertainty_dependencies.json")
        if args.mode == "final":
            preliminary = int(contract["sampling"]["preliminary_sample_count"])
            confirmation = int(contract["sampling"]["confirmation_sample_count"])
            sensitivity_samples = 4096
            bootstrap = int(contract["sensitivity"]["bootstrap_replicates"])
        else:
            preliminary, confirmation, sensitivity_samples, bootstrap = 512, 1024, 512, 100
        payload = {
            "mode": args.mode,
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
        write_json(args.output, payload)
    elif args.command == "build-publication":
        payload = build_publication_bundle(
            args.study_root,
            args.output_directory,
            mode=args.mode,
        )
    else:
        with args.case.open(encoding="utf-8") as stream:
            payload = run_case(json.load(stream))

    text = json.dumps(
        payload,
        sort_keys=True,
        indent=None if getattr(args, "compact", False) else 2,
        separators=(",", ":") if getattr(args, "compact", False) else None,
        allow_nan=False,
    ) + "\n"
    output = getattr(args, "output", None)
    if output is None:
        sys.stdout.write(text)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
