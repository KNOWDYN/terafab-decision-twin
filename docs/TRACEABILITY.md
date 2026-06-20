# Blueprint Traceability

This repository is a runnable v1 implementation of the Terafab Decision Twin blueprint. It maps the blueprint requirements to implemented files as follows.

| Blueprint requirement | Implemented location |
|---|---|
| Repository shell and README | `README.md`, `pyproject.toml`, `LICENSE.md` |
| Evidence registry and status discipline | `terafab_decision_twin/evidence.py`, `docs/EVIDENCE_POLICY.md`, `sources/admitted_facts.json` |
| Scenario schema | `schema/scenario_schema.json`, `terafab_decision_twin/schema.py` |
| Time-step solver | `terafab_decision_twin/time_axis.py`, `terafab_decision_twin/engine.py` |
| Mass/species equations | `terafab_decision_twin/models/mass.py` |
| First-law/heat-rejection equations | `terafab_decision_twin/models/first_law.py`, `terafab_decision_twin/models/cooling.py` |
| Entropy/exergy equations | `terafab_decision_twin/models/entropy.py`, `terafab_decision_twin/models/exergy.py` |
| Power/grid equations | `terafab_decision_twin/models/power.py` |
| Water/UPW/wastewater equations | `terafab_decision_twin/models/water.py` |
| Yield/readiness equations | `terafab_decision_twin/models/manufacturing.py`, `terafab_decision_twin/models/readiness.py` |
| Thermoeconomics | `terafab_decision_twin/models/economics.py` |
| Governance and partner-risk model | `terafab_decision_twin/models/governance.py` |
| Real-options phase-gate model | `terafab_decision_twin/models/real_options.py` |
| Policy/public-benefit model | `terafab_decision_twin/models/policy.py` |
| Optimization hook | `terafab_decision_twin/models/optimize.py` |
| Due-diligence gates | `terafab_decision_twin/models/gates.py` |
| Output registry | `terafab_decision_twin/outputs.py`, `docs/OUTPUT_REGISTRY.md` |
| CLI package | `terafab_decision_twin/cli.py`, `docs/CLI.md` |
| Report generation | `terafab_decision_twin/report.py`, `docs/REPORTING.md` |
| Sample scenarios | `scenarios/*.json` |
| Tests and success gates | `tests/*.py`, `Makefile` |
| Source redistribution gate | `sources/source_manifest.json`, `sources/restricted_sources_exclusion.md` |

## v1 scope boundary

The repository is non-hollow: equations are implemented and executable. It is still a v1 scenario engine, not a fully calibrated industrial model. Any missing proprietary input must be supplied later as an evidence-coded scenario value.
