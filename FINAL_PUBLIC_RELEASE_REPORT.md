# Terafab Decision Twin Final Public Release Report

## Release identity

- Repository package: `terafab-decision-twin`
- Public release version: `0.3.0`
- GitHub owner configured for Pages: `KNOWDYN`
- GitHub Pages path: `/docs`
- Expected Pages URL: `https://knowdyn.github.io/terafab-decision-twin/`

## Scope

This release combines the upgraded Python package with the final minimal-premium GitHub Pages site layer under `/docs`.

The release includes:

- evidence-hardened Python package;
- strict scenario schema and packaged schema copy;
- canonical evidence-status normalization;
- unknown-value discipline;
- first-class formal modules for cleanroom, contamination, packaging, qualification, and Bayesian evidence;
- output metadata, output registries, gate matrix, reports, and export bundles;
- expanded CLI commands;
- source-governance files;
- KNOWDYN license, notice, and citation files;
- public infographic assets;
- CI workflows;
- final minimal GitHub Pages site with PWA, SEO, sitemap, robots, JSON-LD, and `llms.txt`.

## Website merge

Merged from the minimal-premium GitHub Pages site package into `/docs`.

The public website is intentionally concise:

- digital-white background;
- black readable typography;
- one external CTA only: the GitHub repository icon;
- PWA button text: `Keep this site`;
- MathJax configured for LaTeX rendering;
- no dashboard bloat;
- no unsupported endorsement, affiliation, private-data, acquisition, financing, permitting, construction, or operating-status claims.

## Validation

Python test suite:

```text
Ran 34 tests
OK
```

Non-editable install smoke test passed:

```text
pip install .
terafab version
terafab schema show
terafab scenario validate scenarios/baseline_2026.json
terafab scenario validate scenarios/terawatt_stress_2026.json
terafab scenario validate scenarios/multi_year_2026_2030.json
terafab simulate scenarios/baseline_2026.json
terafab export scenarios/baseline_2026.json
```

Restricted-source scan passed. See `FINAL_RESTRICTED_SOURCE_SCAN.json`.

## Legal and source boundaries

Restricted source documents are not redistributed. The release reserves package rights to KNOWDYN and includes non-affiliation language for Terafab. Terafab is acknowledged as owned by its official entity. This release does not claim any connection with Terafab, its company, or its employees.
