# Reporting

The package produces Markdown and JSON-compatible decision reports. Reports are conditional on the scenario inputs and do not verify Terafab operating facts.

Report sections include:

- scenario identity;
- model, schema, and source-bundle versions;
- executive status;
- key scalar outputs;
- due-diligence gates;
- evidence-status counts;
- assumptions used;
- verified, model-identity, filed, and reported inputs used;
- unresolved variables;
- formal module outputs;
- what the scenario can conclude;
- what the scenario cannot conclude;
- data that would change the result most;
- reproducibility hashes;
- KNOWDYN rights and Terafab non-affiliation boundaries.

Generate a report:

```bash
terafab simulate scenarios/baseline_2026.json \
  --output runs/baseline_2026.json \
  --report runs/baseline_2026.md
```

Or print/write only the Markdown report:

```bash
terafab report scenarios/baseline_2026.json --output runs/baseline_2026.md
```

Reports intentionally preserve evidence-status labels. A stress-test input remains a stress-test input in the report.
