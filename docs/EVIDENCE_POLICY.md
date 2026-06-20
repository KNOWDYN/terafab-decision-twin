# Evidence Policy

The package is evidence-gated by design. Every material scenario input must identify what kind of claim it is, where it came from, and whether it may support a conclusion.

## Canonical input statuses

- `verified_project_fact`: fact about this public repository or model package, with a source reference.
- `model_identity`: locked model rule, schema rule, equation identity, or source-boundary rule.
- `filed_claimed`: claim found in an official filing or similarly attributable public document.
- `reported`: media, analyst, or secondary-source report.
- `user_provided`: value supplied by the scenario author.
- `scenario_assumption`: ordinary scenario assumption.
- `stress_test_assumption`: intentionally extreme or stress-test value.
- `unknown`: material value is not known and must not be silently defaulted into a conclusion.
- `confidential_private_input`: private input supplied outside the public repo; no private source content is redistributed.
- `derived_output`: model output, not a valid way to smuggle an input claim into a scenario.

Legacy v0.1 aliases such as `verified_fact`, `filed_claim`, `reported_claim`, `user_input`, `assumption`, and `confidential_input` are normalized at runtime for backward compatibility. Public reports emit canonical status names.

## Required evidence fields

Material inputs must be objects with:

```json
{
  "value": 150,
  "unit": "MW",
  "status": "scenario_assumption",
  "source_ref": "scenario_author",
  "confidence": "declared",
  "notes": "Scenario-declared value; not a verified Terafab operating fact."
}
```

## Non-promotion rule

Scenario assumptions, stress-test values, reported claims, user inputs, Bayesian confidence, and confidential inputs must not be promoted into verified project facts.

## Unknown-value rule

A material value marked `unknown`, `null`, empty, or unparseable is recorded as unresolved. If unknown substitution is not explicitly allowed, the unknown-discipline gate fails and affected conclusions remain underdetermined. Unknowns are never treated as verified values.

## Verified/project-identity source rule

`verified_project_fact`, `model_identity`, `filed_claimed`, and `reported` values require non-empty `source_ref` metadata. The public repository does not require raw confidential documents to be committed, but it does require status honesty.

## One-terawatt rule

A one-terawatt case is a scenario or stress test unless separately verified by admissible evidence. Included samples label one-terawatt inputs as `stress_test_assumption`, not verified Terafab site load.

## Restricted-source rule

Restricted source documents are excluded from the repo. Source manifests may record source class, role, hash fields where appropriate, and handling rules without redistributing content.
