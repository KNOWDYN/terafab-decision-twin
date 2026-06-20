# Public Release Final Pass Report

Date: 2026-06-20
Package path: `/mnt/data/tdt_upgrade/terafab-decision-twin`
Release candidate: `0.3.0`

This pass prepared the Python package working tree for the next explicit command that will produce the final public-release ZIP. The website was not merged and no final release ZIP was produced in this pass.

## Final-pass changes

1. **Installed-package schema access fixed**
   - Added `terafab_decision_twin/data/scenario_schema.json`.
   - Added package-data configuration in `pyproject.toml`.
   - Updated `terafab schema show` to work from both source-tree and non-editable installed contexts.
   - Added `MANIFEST.in` for source distributions.

2. **Release-candidate version alignment**
   - Set package/model release candidate to `0.3.0`.
   - Updated scenario metadata to `model_version = 0.3.0` and `schema_version = 0.3.0`.
   - Updated source-bundle metadata to `public-source-manifest-v0.3`.

3. **Documentation consistency pass**
   - Rewrote `docs/EVIDENCE_POLICY.md` around canonical statuses.
   - Rewrote `docs/CLI.md` around the final command structure.
   - Expanded `docs/REPORTING.md` with report sections and evidence boundaries.
   - Updated `docs/ARCHITECTURE.md`, `docs/BUILD_ACCEPTANCE.md`, `docs/OUTPUT_REGISTRY.md`, `docs/COLAB_DASHBOARD.md`, and `docs/TRACEABILITY.md`.
   - Removed stale public wording from the v0.1 evidence dialect except as documented legacy aliases.

4. **Public infographic assets added**
   - Added `assets/terafab_one_page_infographic.svg`.
   - Added `assets/terafab_one_page_infographic.png`.
   - Added `assets/terafab_one_page_infographic.pdf`.
   - Render-verified the PDF to PNG using the PDF workflow.

5. **CI hardening**
   - Updated test and schema workflows to install the package non-editably with `pip install .`.
   - Removed permissive `|| true` from stress-scenario validation.
   - Added `docs-links.yml` for public-doc and infographic guard checks.

6. **Example runner fixed**
   - Updated `scripts/run_all_examples.py` so it works when run directly from the repository without requiring editable installation.

7. **Expanded release tests**
   - Added release-guard tests for version consistency, schema packaged-copy consistency, canonical status documentation, infographic assets, and restricted-source absence.
   - Test count increased from 28 to 34.

8. **Working-tree hygiene**
   - Removed generated `build/`, `*.egg-info`, `__pycache__/`, `.pyc`, and run-output artifacts from the working tree.

## Validation performed

```text
python -m unittest discover -s tests -v
Ran 34 tests
OK
```

```text
pip install .
terafab version
terafab schema show
terafab scenario validate scenarios/baseline_2026.json
terafab scenario validate scenarios/terawatt_stress_2026.json
terafab scenario validate scenarios/multi_year_2026_2030.json
terafab export scenarios/baseline_2026.json /tmp/tdt_final_export2
```

All commands completed successfully. The export smoke test produced:

```text
gate_matrix.csv
report.md
result.json
summary.csv
```

Additional guards passed:

- restricted source documents absent from the working tree;
- public docs guard passed;
- no `TODO`, `FIXME`, placeholder marker, or `source-bounded` string remains in the public package files scanned;
- infographic PDF rendered successfully to an inspection PNG.

## Remaining before final public ZIP

The next pass should:

1. merge the final minimal-premium `/docs` GitHub Pages website layer;
2. run one combined restricted-source scan across package and site;
3. run the full tests one more time after merge;
4. create the final public-release ZIP only after explicit command.
