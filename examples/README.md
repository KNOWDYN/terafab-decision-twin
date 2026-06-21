# Public Monitoring Examples

This directory is an audit-friendly playbook for using the Terafab Decision Twin with public information, verifiable available sources, and clearly labeled assumptions.

It is designed for technical and non-technical stakeholders who want to monitor public progress signals without exaggerating them.

## What this directory provides

| File | Purpose |
|---|---|
| `public_monitoring_checklist.md` | Plain-English checklist for public progress monitoring. |
| `evidence_intake_template.json` | Template for turning a public claim into an evidence-coded model input. |
| `source_register_template.json` | Template for classifying source types and source-status boundaries. |
| `stakeholder_board_monitoring.md` | Board and executive monitoring workflow. |
| `stakeholder_policy_monitoring.md` | Public-policy and permitting workflow. |
| `stakeholder_engineering_monitoring.md` | Engineering and infrastructure-readiness workflow. |
| `stakeholder_investor_monitoring.md` | Investor and capital-allocation workflow. |
| `scenario_public_progress_watch.json` | Schema-valid demonstration scenario for public progress monitoring. |
| `scenario_public_infrastructure_watch.json` | Schema-valid demonstration scenario for public infrastructure monitoring. |

## Trust boundary

These examples do **not** claim official Terafab progress, private Terafab operating data, confidential access, Terafab endorsement, financing status, construction status, operation status, acquisition interest, or official validation.

They show how a user could convert public records, public statements, reported claims, or explicitly declared assumptions into scenario inputs while preserving evidence status.

## Recommended workflow

1. Start with `public_monitoring_checklist.md`.
2. Record each public claim in `evidence_intake_template.json`.
3. Classify sources with `source_register_template.json`.
4. Choose a stakeholder workflow.
5. Update a scenario JSON with evidence-coded inputs.
6. Run validation before interpreting any result.

## Validation commands

From the repository root:

```bash
python -m json.tool examples/evidence_intake_template.json
python -m json.tool examples/source_register_template.json
python -m json.tool examples/scenario_public_progress_watch.json
python -m json.tool examples/scenario_public_infrastructure_watch.json
python - <<'PY'
from pathlib import Path
from terafab_decision_twin.schema import load_scenario, validate_scenario
for path in [
    Path('examples/scenario_public_progress_watch.json'),
    Path('examples/scenario_public_infrastructure_watch.json'),
]:
    errors = validate_scenario(load_scenario(path))
    if errors:
        raise SystemExit(f'{path}: {errors}')
    print(f'VALID {path}')
PY
```

Passing validation means the files satisfy the public scenario schema. It does not mean the numerical values are verified Terafab facts.
