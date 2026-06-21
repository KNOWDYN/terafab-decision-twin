# Validation Lab

The validation lab adds validation-readiness tooling under `validation_lab/`. Its purpose is to prevent the advanced simulation layer from becoming narrative machinery.

## Validation levels

```text
Level 0 - Code and schema execution
  The model runs and produces finite outputs.

Level 1 - Structural validation
  Required result fields, matrices, gates, and output structures are present.

Level 2 - Public-reference screening
  Outputs are checked against declared public-reference or dimensional ranges.

Level 3 - Benchmark comparison
  Requires curated public benchmark cases.

Level 4 - Expert/calibrated validation
  Requires official project data, stakeholder data, expert review, or proprietary calibration evidence.
```

The included update supports Level 1 and Level 2 screening. It does not claim Level 4 validation.

## Example use

```python
import json
from pathlib import Path
from terafab_decision_twin.schema import load_scenario
from terafab_decision_twin.engine import run_scenario
from validation_lab import build_validation_report

scenario = load_scenario("scenarios/baseline_2026.json")
result = run_scenario(scenario)
ranges = json.loads(Path("validation_lab/reference_ranges.json").read_text())
report = build_validation_report(result, ranges)
print(report["validation_level"])
print(report["calibration_gaps"])
```

## Boundary

Validation-lab checks are screening tools. They do not replace utility interconnection studies, water-authority records, permitting documents, official project data, expert engineering review, or investment diligence.
