# Evidence Policy

## Allowed input statuses

- `verified_fact`
- `filed_claim`
- `reported_claim`
- `user_input`
- `assumption`
- `stress_test_assumption`
- `unknown`
- `confidential_input`
- `derived_output`

## Non-promotion rule

Scenario assumptions, stress-test values, reported claims, user inputs, and confidential inputs must not be promoted to verified facts.

## Verified fact rule

A `verified_fact` must carry a non-empty source. The repository does not require raw confidential documents to be committed, but it does require status honesty.

## One-terawatt rule

A one-terawatt load is not treated as a verified site load unless a future scenario supplies admissible verification. In included samples it appears only as a `stress_test_assumption`.

## Restricted-source rule

Restricted source documents are excluded from the repo. Source manifests may record filenames, hashes, status, and citation notes without redistributing content.
