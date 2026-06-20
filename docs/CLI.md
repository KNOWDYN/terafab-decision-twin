# CLI Usage

The public command group is explicit and evidence-oriented.

## Schema

```bash
terafab schema show
terafab schema show --output schema/scenario_schema.copy.json
```

`schema show` works both from the source tree and from a non-editable installed package.

## Scenarios

Create a starter scenario:

```bash
terafab scenario new board_baseline scenarios/board_baseline.json --scenario-type demonstration
```

Validate a scenario:

```bash
terafab scenario validate scenarios/baseline_2026.json
terafab scenario validate scenarios/baseline_2026.json --strict
```

## Simulation

```bash
terafab simulate scenarios/baseline_2026.json --output runs/baseline_2026.json --report runs/baseline_2026.md
```

## Gates

```bash
terafab gates scenarios/terawatt_stress_2026.json
```

## Outputs

```bash
terafab outputs list
terafab outputs list --kind scalar
terafab outputs list --kind vector
terafab outputs list --kind matrix
```

## Reports and exports

```bash
terafab report scenarios/baseline_2026.json --output runs/baseline_2026.md
terafab export scenarios/baseline_2026.json runs/baseline_bundle
```

Export bundles contain:

```text
result.json
report.md
summary.csv
gate_matrix.csv
```

## Version

```bash
terafab version
```

## Backward-compatible aliases

Legacy v0.1 aliases remain available but should not be used in final documentation:

```bash
terafab validate scenarios/baseline_2026.json
terafab run scenarios/baseline_2026.json
```

## Exit codes

- `0`: command succeeded and error-level gates passed;
- `1`: validation/runtime error;
- `2`: scenario executed but at least one error-level gate failed.
