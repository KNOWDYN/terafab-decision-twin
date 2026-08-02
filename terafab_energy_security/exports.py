"""Deterministic, machine-readable exports shared by the CLI and notebook."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


def write_json(path: str | Path, payload: Any) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return target


def _csv_value(value: Any) -> Any:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return value


def write_csv(path: str | Path, rows: Iterable[Mapping[str, Any]]) -> Path:
    materialized = list(rows)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    keys: list[str] = []
    seen: set[str] = set()
    for row in materialized:
        for key in row:
            if key not in seen:
                keys.append(key)
                seen.add(key)
    with target.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        for row in materialized:
            writer.writerow({key: _csv_value(row.get(key)) for key in keys})
    return target


def write_scenario_outputs(output_directory: str | Path, result: Mapping[str, Any]) -> list[Path]:
    output = Path(output_directory)
    return [
        write_csv(output / "scenario_matrix.csv", result["scenario_matrix"]),
        write_csv(output / "annual_results.csv", result["annual_results"]),
        write_csv(output / "gate_results.csv", result["gate_results"]),
        write_csv(output / "trajectory_summary.csv", result["trajectory_summary"]),
        write_json(output / "run_manifest.json", result["manifest"]),
    ]
