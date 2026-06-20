from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from importlib import resources

from .schema import load_scenario, validate_scenario
from .engine import run_scenario, MODEL_VERSION
from .report import markdown_report
from .outputs import SCALAR_OUTPUTS, VECTOR_OUTPUTS, MATRIX_OUTPUTS, OUTPUT_UNITS, OUTPUT_EQUATIONS

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "scenario_schema.json"


def _scenario_schema_text() -> str:
    """Return scenario_schema.json in source-tree and installed-package contexts."""
    if SCHEMA_PATH.exists():
        return SCHEMA_PATH.read_text(encoding="utf-8")
    return resources.files("terafab_decision_twin.data").joinpath("scenario_schema.json").read_text(encoding="utf-8")


def _write_json(path: str | Path, obj) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def cmd_schema_show(args) -> int:
    text = _scenario_schema_text()
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


def _ev(value, unit, notes="Scenario-declared value; not a verified Terafab operating fact."):
    return {"value": value, "unit": unit, "status": "scenario_assumption", "source_ref": "scenario_author", "confidence": "declared", "notes": notes}


def cmd_scenario_new(args) -> int:
    sid = args.scenario_id
    scenario = {
        "metadata": {
            "scenario_id": sid, "title": args.title or sid.replace("_", " ").title(), "version": "0.3.0",
            "scenario_author": "KNOWDYN", "scenario_date": "2026-01-01", "model_version": MODEL_VERSION,
            "schema_version": "0.3.0", "source_bundle_version": "public-source-manifest-v0.3",
            "scenario_purpose": "Template scenario for evidence-gated Terafab-scale analysis.",
            "scenario_type": args.scenario_type, "calendar_basis": "model year", "discount_basis": "real annual"
        },
        "time": {"start_year": 2026, "end_year": 2026, "time_step": "annual"},
        "terafab_phase": {"phase": _ev("concept", "category"), "one_terawatt_treatment": _ev("not_used", "category")},
        "energy": {"site_electric_load_MW": _ev(150, "MW"), "load_factor": _ev(0.85, "fraction"), "firm_capacity_MW": _ev(200, "MW"), "reserve_margin_fraction": _ev(0.15, "fraction"), "grid_carbon_intensity_kg_per_MWh": _ev(350, "kg/MWh")},
        "cooling": {"heat_rejection_capacity_MW": _ev(170, "MW"), "heat_rejection_fraction": _ev(0.98, "fraction"), "cooling_reserve_margin_fraction": _ev(0.10, "fraction"), "cop": _ev(6.0, "ratio")},
        "water": {"withdrawal_m3_per_MWh": _ev(1.2, "m3/MWh"), "consumptive_fraction": _ev(0.55, "fraction"), "wastewater_fraction": _ev(0.45, "fraction"), "permit_withdrawal_m3_per_day": _ev(5000, "m3/day"), "permit_discharge_m3_per_day": _ev(3000, "m3/day"), "water_reserve_margin_fraction": _ev(0.10, "fraction"), "wastewater_reserve_margin_fraction": _ev(0.10, "fraction"), "upw_m3_per_wafer": _ev(0.2, "m3/wafer")},
        "manufacturing": {"wafer_starts_per_month": _ev(25000, "wafers/month"), "die_per_wafer": _ev(500, "die/wafer"), "baseline_yield": _ev(0.72, "fraction"), "learning_rate_per_year": _ev(0.02, "fraction/year"), "contamination_loss_fraction": _ev(0.03, "fraction"), "qualification_readiness": _ev(0.85, "fraction"), "contamination_readiness": _ev(0.9, "fraction"), "packaging_readiness": _ev(0.85, "fraction"), "compute_watts_per_good_die": _ev(50, "W/die")},
        "economics": {"electricity_price_USD_per_MWh": _ev(70, "USD/MWh"), "water_price_USD_per_m3": _ev(2.0, "USD/m3"), "capex_USD": _ev(10000000000, "USD"), "annual_fixed_opex_USD": _ev(500000000, "USD/year"), "discount_rate": _ev(0.08, "fraction"), "asset_life_years": _ev(20, "years"), "incentive_public_USD": _ev(0, "USD")},
        "governance": {"partner_count": _ev(1, "count"), "governance_complexity_index": _ev(0.2, "index"), "decision_latency_months": _ev(2, "months")},
        "policy": {"jobs_created": _ev(1000, "jobs"), "domestic_supply_security_index": _ev(0.5, "index"), "local_water_stress_index": _ev(0.3, "index"), "public_legitimacy_index": _ev(0.7, "index"), "regulatory_readiness_index": _ev(0.8, "index"), "emissions_price_USD_per_tCO2": _ev(0, "USD/tCO2")},
        "control": {"strict_evidence": False, "fail_on_unverified_claims": False, "allow_unknown_substitution": False, "allowed_actions": ["build", "delay", "scale", "redesign", "allocate", "contract", "license", "partner", "curtail", "abandon"], "output_registry": ["scalar_outputs", "vector_outputs", "matrix_outputs"], "report_format": "json"}
    }
    _write_json(args.output, scenario)
    print(args.output)
    return 0


def cmd_scenario_validate(args) -> int:
    scenario = load_scenario(args.scenario)
    errors = validate_scenario(scenario, strict=args.strict)
    if errors:
        print("INVALID")
        for e in errors:
            print(f"- {e}")
        return 1
    print("VALID")
    return 0


def cmd_simulate(args) -> int:
    scenario = load_scenario(args.scenario)
    result = run_scenario(scenario)
    if args.output:
        _write_json(args.output, result)
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    if args.report:
        rep = Path(args.report)
        rep.parent.mkdir(parents=True, exist_ok=True)
        rep.write_text(markdown_report(result), encoding="utf-8")
    return 0 if result.get("passed") else 2


def cmd_gates(args) -> int:
    result = run_scenario(load_scenario(args.scenario))
    for gate in result["gates"]:
        status = "PASS" if gate["passed"] else "FAIL"
        print(f"{status:4} {gate['severity']:7} {gate['name']}: {gate['message']} margin={gate['margin']}")
    return 0 if result.get("passed") else 2


def cmd_report(args) -> int:
    result = run_scenario(load_scenario(args.scenario))
    report = markdown_report(result)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


def cmd_outputs_list(args) -> int:
    if args.kind in {"all", "scalar"}:
        for name in SCALAR_OUTPUTS:
            print(f"scalar\t{name}\t{OUTPUT_UNITS.get(name,'')}\t{OUTPUT_EQUATIONS.get(name,'')}")
    if args.kind in {"all", "vector"}:
        for name in VECTOR_OUTPUTS:
            print(f"vector\t{name}")
    if args.kind in {"all", "matrix"}:
        for name in MATRIX_OUTPUTS:
            print(f"matrix\t{name}")
    return 0


def cmd_export(args) -> int:
    result = run_scenario(load_scenario(args.scenario))
    outdir = Path(args.output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    _write_json(outdir / "result.json", result)
    (outdir / "report.md").write_text(markdown_report(result), encoding="utf-8")
    with open(outdir / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        for k, v in result.get("summary", {}).items():
            w.writerow([k, v])
    with open(outdir / "gate_matrix.csv", "w", newline="", encoding="utf-8") as f:
        rows = result.get("matrices", {}).get("gate_matrix", [])
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    print(outdir)
    return 0 if result.get("passed") else 2


def cmd_version(args) -> int:
    print(MODEL_VERSION)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="terafab", description="Run the Terafab Decision Twin.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_schema = sub.add_parser("schema", help="Schema utilities.")
    schema_sub = p_schema.add_subparsers(dest="schema_command", required=True)
    p = schema_sub.add_parser("show", help="Show scenario_schema.json.")
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_schema_show)

    p_scenario = sub.add_parser("scenario", help="Scenario utilities.")
    sc_sub = p_scenario.add_subparsers(dest="scenario_command", required=True)
    p = sc_sub.add_parser("new", help="Create a starter scenario.")
    p.add_argument("scenario_id")
    p.add_argument("output")
    p.add_argument("--title")
    p.add_argument("--scenario-type", default="demonstration")
    p.set_defaults(func=cmd_scenario_new)
    p = sc_sub.add_parser("validate", help="Validate a scenario JSON file.")
    p.add_argument("scenario")
    p.add_argument("--strict", action="store_true")
    p.set_defaults(func=cmd_scenario_validate)

    p = sub.add_parser("simulate", help="Run a scenario and emit JSON outputs.")
    p.add_argument("scenario")
    p.add_argument("--output", "-o")
    p.add_argument("--report", "-r")
    p.set_defaults(func=cmd_simulate)

    p = sub.add_parser("gates", help="Run a scenario and print gate results.")
    p.add_argument("scenario")
    p.set_defaults(func=cmd_gates)

    p = sub.add_parser("outputs", help="Output registry utilities.")
    out_sub = p.add_subparsers(dest="outputs_command", required=True)
    p = out_sub.add_parser("list", help="List registered outputs.")
    p.add_argument("--kind", choices=["all", "scalar", "vector", "matrix"], default="all")
    p.set_defaults(func=cmd_outputs_list)

    p = sub.add_parser("report", help="Run a scenario and write/print a Markdown report.")
    p.add_argument("scenario")
    p.add_argument("--output", "-o")
    p.set_defaults(func=cmd_report)

    p = sub.add_parser("export", help="Export result.json, report.md, summary.csv, and gate_matrix.csv.")
    p.add_argument("scenario")
    p.add_argument("output_dir")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("version", help="Print package model version.")
    p.set_defaults(func=cmd_version)

    # Backward-compatible v0.1 aliases.
    p = sub.add_parser("validate", help=argparse.SUPPRESS)
    p.add_argument("scenario")
    p.add_argument("--strict", action="store_true")
    p.set_defaults(func=cmd_scenario_validate)
    p = sub.add_parser("run", help=argparse.SUPPRESS)
    p.add_argument("scenario")
    p.add_argument("--output", "-o")
    p.add_argument("--report", "-r")
    p.set_defaults(func=cmd_simulate)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
