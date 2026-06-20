# Architecture

The runnable v1 repository follows the blueprint's simulation architecture:

```text
scenario JSON
  -> schema validation
  -> evidence audit
  -> time-axis expansion
  -> equation modules
  -> output aggregation
  -> due-diligence gates
  -> JSON / Markdown reports
```

## Core package modules

- `schema.py` validates top-level scenario structure, required fields, time horizons, and evidence-status errors.
- `evidence.py` defines allowed evidence statuses, unwraps evidence-coded inputs, audits verified-fact claims, and summarizes source discipline.
- `time_axis.py` builds annual, quarterly, or monthly time steps beginning in 2026.
- `engine.py` coordinates all model modules and emits reproducible run bundles.
- `report.py` produces Markdown decision reports.
- `models/` contains executable equations for mass, first law, entropy, exergy, power, cooling, water, yield, readiness, economics, governance, real options, policy, gates, and simple optimization.

## Evidence-gated design

The implementation intentionally separates input status from numerical value. A value may be useful in a stress test without being a verified fact. The engine runs declared scenarios, while the evidence gate prevents unsupported promotion of those scenarios into claims about actual Terafab operations.
