# Terafab Decision Twin Reference Wiki

This directory is the text-first reference wiki for the Terafab Decision Twin. The deployed stakeholder-facing PWA lives in `website/`; these documents provide the deeper technical, evidence, validation, and operational context linked from that one-page site.

## Required interpretation boundary

This repository is source-available, not open-source software. The Terafab Decision Twin is an independent KNOWDYN analytical model. It does not claim Terafab endorsement, authorization, private data access, official operating status, permitting conclusions, investment advice, engineering certification, or verified Terafab operating facts.

Scenario outputs are scenario-dependent analytical estimates derived from declared assumptions, model structure, and available public or user-supplied inputs. Evidence status, unknown-value discipline, restricted-source boundaries, and assumption boundaries must remain visible when using or summarizing the package.

## Start here

- [Evidence Policy](EVIDENCE_POLICY.md) — canonical evidence statuses, non-promotion rules, unknown handling, and restricted-source boundaries.
- [Architecture](ARCHITECTURE.md) — scenario validation, evidence audit, solver flow, output generation, and model module map.
- [Stakeholder Decision Surfaces](STAKEHOLDER_DECISION_SURFACES.md) — board, investor, policy, and research views for decision screening.
- [Validation Lab](VALIDATION_LAB.md) — validation-readiness levels and boundaries.
- [Traceability](TRACEABILITY.md) — blueprint requirements mapped to implemented files.

## Model and output references

- [Equations](EQUATIONS.md) — formal equation references and model identities.
- [Output Registry](OUTPUT_REGISTRY.md) — scalar, vector, and matrix output families.
- [Reporting](REPORTING.md) — Markdown, JSON, CSV, and bundle reporting behavior.
- [Advanced Simulation](ADVANCED_SIMULATION.md) — uncertainty, strategy, reduced-order models, and advanced screening overlays.

## Run and operate

- [CLI](CLI.md) — command-line validation, simulation, gates, reporting, and export workflows.
- [LLM Guidance](llms.txt) — concise guidance for language models and automated summarizers.

## Licensing

The root license files govern use:

- [`../ACADEMIC_LICENSE.md`](../ACADEMIC_LICENSE.md)
- [`../COMMERCIAL_LICENSE.md`](../COMMERCIAL_LICENSE.md)

Commercial use requires separate written permission from KNOWDYN.
