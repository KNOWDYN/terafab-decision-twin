from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .schema import load_scenario, validate_scenario
from .engine import run_scenario
from .report import markdown_report


def cmd_validate(args) -> int:
    scenario = load_scenario(args.scenario)
    errors = validate_scenario(scenario, strict=args.strict)
    if errors:
        print("INVALID")
        for e in errors:
            print(f"- {e}")
        return 1
    print("VALID")
    return 0


def cmd_run(args) -> int:
    scenario = load_scenario(args.scenario)
    result = run_scenario(scenario)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
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
    print(markdown_report(result))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="terafab", description="Run the Terafab Decision Twin.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("validate", help="Validate a scenario JSON file.")
    p.add_argument("scenario")
    p.add_argument("--strict", action="store_true", help="Apply stricter evidence-audit behavior.")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("run", help="Run a scenario and emit JSON outputs.")
    p.add_argument("scenario")
    p.add_argument("--output", "-o")
    p.add_argument("--report", "-r")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("gates", help="Run a scenario and print gate results.")
    p.add_argument("scenario")
    p.set_defaults(func=cmd_gates)

    p = sub.add_parser("report", help="Run a scenario and print a Markdown report.")
    p.add_argument("scenario")
    p.set_defaults(func=cmd_report)
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
