# Architecture

The repository is a runnable Python implementation of the Terafab Decision Twin blueprint.

```text
scenario JSON
  -> schema validation
  -> evidence audit and status normalization
  -> unknown-value discipline
  -> time-axis expansion
  -> formal equation modules
  -> scalar/vector/matrix outputs
  -> due-diligence gate matrix
  -> JSON / Markdown / CSV export bundle
```

## Core modules

- `schema.py`: validates top-level scenario structure, required fields, canonical evidence metadata, time horizons, and control actions.
- `evidence.py`: defines canonical evidence statuses, legacy alias normalization, evidence audits, status summaries, and assumption/fact extraction.
- `unknowns.py`: records underdetermined inputs and prevents unknowns from silently becoming conclusions.
- `time_axis.py`: builds annual, quarterly, or monthly time steps beginning in 2026.
- `engine.py`: coordinates the time-step solver and emits reproducible results.
- `outputs.py`: defines scalar, vector, and matrix output registries and output records.
- `report.py`: produces Markdown decision reports.
- `models/`: mass, first law, entropy, exergy, power, cooling, water, yield, readiness, economics, governance, real options, policy, gates, and optimization hooks.

## First-class formal boundaries

The final public package keeps these domains visible rather than hiding them inside a generic manufacturing module:

```text
cleanroom/
contamination/
packaging/
qualification/
evidence_bayes/
```

These modules are conservative public abstractions. They do not imply access to private Terafab operating data.

## Evidence-gated design

The implementation separates numerical values from evidentiary status. A value can drive a scenario without becoming a verified Terafab fact. A one-terawatt input can be useful as a stress test while remaining labeled `stress_test_assumption`.
