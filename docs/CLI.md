# CLI Usage

Validate a scenario:

```bash
terafab validate scenarios/baseline_2026.json
```

Run a scenario:

```bash
terafab run scenarios/baseline_2026.json --output runs/baseline_2026.json
```

Generate JSON and Markdown:

```bash
terafab run scenarios/baseline_2026.json \
  --output runs/baseline_2026.json \
  --report runs/baseline_2026.md
```

Show gate results:

```bash
terafab gates scenarios/terawatt_stress_2026.json
```

Print a Markdown report to stdout:

```bash
terafab report scenarios/baseline_2026.json
```

Exit codes:

- `0`: command succeeded and error-level gates passed;
- `1`: validation/runtime error;
- `2`: scenario executed but at least one error-level gate failed.
