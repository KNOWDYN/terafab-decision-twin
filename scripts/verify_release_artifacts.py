#!/usr/bin/env python3
"""Verify public-release source distribution and wheel contents.

The source distribution is the complete source-available review artifact. The
wheel is the installable runtime artifact and must still carry the root legal
files in wheel metadata.
"""
from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

REQUIRED_SDIST = {
    "README.md",
    "LICENSE.md",
    "ACADEMIC_LICENSE.md",
    "COMMERCIAL_LICENSE.md",
    "NOTICE.md",
    "CITATION.cff",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "MANIFEST.in",
    "pyproject.toml",
    "docs/RELEASE_CHECKLIST.md",
    "docs/EVIDENCE_POLICY.md",
    "docs/TRACEABILITY.md",
    "schema/scenario_schema.json",
    "scenarios/baseline_2026.json",
    "sources/restricted_sources_exclusion.md",
    "sources/source_manifest.json",
    "examples/README.md",
    "website/index.html",
    "website/assets/fonts.css",
    "website/service-worker.js",
    "notebooks/terafab_decision_twin_colab_lab.ipynb",
    "assets/terafab_one_page_infographic.svg",
    "assets/terafab_one_page_infographic.png",
    "assets/terafab_one_page_infographic.pdf",
    "tests/test_release_guards.py",
    ".github/workflows/tests.yml",
    ".github/workflows/pages.yml",
    "scripts/verify_release_artifacts.py",
}

REQUIRED_WHEEL_SUFFIXES = {
    "terafab_decision_twin/__init__.py",
    "terafab_decision_twin/cli.py",
    "terafab_decision_twin/data/scenario_schema.json",
    "strategic_simulation/__init__.py",
    "strategic_simulation/examples/uncertainty_baseline_2026.json",
    "validation_lab/__init__.py",
    "validation_lab/reference_ranges.json",
    "validation_lab/examples/public_reference_validation_case.json",
}

REQUIRED_WHEEL_LEGAL_FILENAMES = {
    "LICENSE.md",
    "ACADEMIC_LICENSE.md",
    "COMMERCIAL_LICENSE.md",
    "NOTICE.md",
}

OBSOLETE_PRIMARY_LICENSE_NAMES = {
    "LICENSE-ACADEMIC.md",
    "LICENSE-COMMERCIAL.md",
}

BANNED_RESTRICTED_SOURCE_NAMES = {
    "KNOWDYN_Terafab_Intelligence_Report_2026.pdf",
    "terafab.docx",
    "Terafab_Formal_JV_Exergy_Yield_Policy_Model.md",
    "Terafab_review.md.txt",
    "terafab_decision_twin-2.md",
}


def _single(pattern: str) -> Path:
    matches = sorted(DIST.glob(pattern))
    if len(matches) != 1:
        raise SystemExit(f"Expected exactly one {pattern} in {DIST}, found {len(matches)}: {matches}")
    return matches[0]


def _strip_sdist_root(names: set[str]) -> set[str]:
    stripped: set[str] = set()
    for name in names:
        parts = Path(name).parts
        if len(parts) > 1:
            stripped.add(str(Path(*parts[1:])))
    return stripped


def _assert_missing(label: str, required: set[str], present: set[str]) -> None:
    missing = sorted(required - present)
    if missing:
        raise SystemExit(f"{label} missing required paths:\n" + "\n".join(f"- {m}" for m in missing))


def _assert_no_banned(label: str, present: set[str]) -> None:
    found_names = {Path(path).name for path in present}
    obsolete = sorted(found_names & OBSOLETE_PRIMARY_LICENSE_NAMES)
    if obsolete:
        raise SystemExit(f"{label} contains obsolete primary license filenames: {obsolete}")
    banned = sorted(found_names & BANNED_RESTRICTED_SOURCE_NAMES)
    if banned:
        raise SystemExit(f"{label} contains restricted source filenames: {banned}")


def verify_sdist(path: Path) -> None:
    with tarfile.open(path) as archive:
        raw_names = {member.name for member in archive.getmembers() if member.isfile()}
    names = _strip_sdist_root(raw_names)
    _assert_missing("sdist", REQUIRED_SDIST, names)
    _assert_no_banned("sdist", names)


def verify_wheel(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = {name for name in archive.namelist() if not name.endswith("/")}
    _assert_missing("wheel", REQUIRED_WHEEL_SUFFIXES, names)
    _assert_no_banned("wheel", names)

    legal_present = {Path(name).name for name in names if ".dist-info/licenses/" in name or ".dist-info/" in name}
    missing_legal = sorted(REQUIRED_WHEEL_LEGAL_FILENAMES - legal_present)
    if missing_legal:
        raise SystemExit("wheel metadata missing legal files:\n" + "\n".join(f"- {m}" for m in missing_legal))

    entry_points = [name for name in names if name.endswith(".dist-info/entry_points.txt")]
    if not entry_points:
        raise SystemExit("wheel missing console-script entry_points.txt")


def main() -> int:
    sdist = _single("*.tar.gz")
    wheel = _single("*.whl")
    verify_sdist(sdist)
    verify_wheel(wheel)
    print(f"Verified release artifacts: {sdist.name}, {wheel.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
