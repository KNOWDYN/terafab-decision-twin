# Public Release Checklist

This checklist qualifies a public release candidate for the source-available Terafab Decision Twin package. It must preserve the repository's licensing, restricted-source, evidence-status, no-verified-data, non-affiliation, assumption-boundary, and scenario-dependence notices.

## 1. Legal and public-boundary checks

- Confirm `LICENSE.md`, `ACADEMIC_LICENSE.md`, `COMMERCIAL_LICENSE.md`, `NOTICE.md`, and `CITATION.cff` exist at the repository root.
- Confirm README, docs, package metadata, and release manifests point to `ACADEMIC_LICENSE.md` and `COMMERCIAL_LICENSE.md` when referring to the academic/commercial license files.
- Confirm the project is described as source-available, not open source.
- Confirm no public file implies Terafab affiliation, endorsement, authorization, official status, verified Terafab operating data, investment advice, permitting certainty, construction status, operation status, or private-data calibration.

## 2. Restricted-source and public-content checks

- Run the restricted-source guard and confirm banned private or restricted source filenames are absent.
- Confirm public examples, docs, notebooks, generated reports, and release notes do not include private project-source files, confidential instructions, unpublished planning notes, AI-agent scratch files, or restricted materials.
- Confirm source/evidence manifests preserve evidence-status and assumption-boundary wording.

## 3. Tests and CLI checks

Run the unit and release-guard test suite:

```bash
python -m unittest discover -s tests -v
```

Validate core scenarios and CLI behavior from the repository checkout:

```bash
terafab scenario validate scenarios/baseline_2026.json
terafab scenario validate scenarios/terawatt_stress_2026.json
terafab scenario validate scenarios/multi_year_2026_2030.json
terafab export scenarios/baseline_2026.json runs/baseline_bundle
```

## 4. Build artifact checks

Build the source distribution and wheel:

```bash
python -m build
```

Inspect the artifacts:

```bash
python -m tarfile -l dist/*.tar.gz
python -m zipfile -l dist/*.whl
python scripts/verify_release_artifacts.py
```

The source distribution must include the public review assets defined in the README release artifact policy. The wheel must include installable runtime packages, runtime package data, package metadata, console script metadata, and root legal files in wheel metadata.

## 5. Installed-wheel smoke checks

Install the wheel in a clean environment or temporary validation environment:

```bash
python -m pip install --force-reinstall dist/*.whl
terafab version
terafab scenario validate scenarios/baseline_2026.json
terafab export scenarios/baseline_2026.json runs/baseline_bundle
```

## 6. GitHub Pages checks

Confirm the Pages workflow stages:

- root `index.html` redirect
- `/website` PWA files
- docs reference aliases
- `ACADEMIC_LICENSE.md`
- `COMMERCIAL_LICENSE.md`

The website font policy must avoid third-party font-host dependencies unless a maintainer explicitly approves and documents the exception.

## 7. Final gate

Before tagging or publishing:

- Confirm `git status --short` is clean.
- Confirm CI passed for tests, schema validation, docs links, restricted-source guard, build artifact verification, and Pages verification.
- Confirm release notes preserve source-available, non-affiliation, no-verified-data, and scenario-dependence language.
