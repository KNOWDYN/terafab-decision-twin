from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from terafab_decision_twin.schema import load_scenario
from terafab_decision_twin.engine import run_scenario
from terafab_decision_twin.report import markdown_report

OUT = ROOT / "runs"
OUT.mkdir(exist_ok=True)

for path in sorted((ROOT / "scenarios").glob("*.json")):
    result = run_scenario(load_scenario(path))
    stem = path.stem
    (OUT / f"{stem}.result.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (OUT / f"{stem}.report.md").write_text(markdown_report(result), encoding="utf-8")
    print(f"{stem}: {'PASS' if result['passed'] else 'FAIL'}")
