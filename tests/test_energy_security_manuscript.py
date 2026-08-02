from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = (
    ROOT
    / "studies"
    / "ecm_terafab_energy_security"
    / "paper"
    / "validate_manuscript.py"
)


def _load_validator():
    spec = importlib.util.spec_from_file_location("terafab_manuscript_validator", VALIDATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load manuscript validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EnergySecurityManuscriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = _load_validator()

    def test_submission_structure_and_scientific_boundaries(self) -> None:
        report = self.validator.validate_structure()
        self.assertLessEqual(report["abstract_words"], 250)
        self.assertEqual(10, report["figure_count"])
        self.assertEqual(6, report["table_count"])
        self.assertTrue(all(length <= 85 for length in report["highlight_lengths"]))

    def test_hu_doi_matches_publisher_record(self) -> None:
        registry = (
            ROOT
            / "studies"
            / "ecm_terafab_energy_security"
            / "evidence"
            / "source_registry.json"
        ).read_text(encoding="utf-8")
        bibliography = (VALIDATOR.parent / "references.bib").read_text(encoding="utf-8")
        self.assertIn("10.1093/ijlct/ctz041", registry)
        self.assertIn("10.1093/ijlct/ctz041", bibliography)
        self.assertNotIn("10.1093/ijlct/ctz040", registry + bibliography)

    def test_manuscript_sources_are_included_in_source_distribution(self) -> None:
        manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
        study_rule = next(
            line
            for line in manifest.splitlines()
            if line.startswith("recursive-include studies/ecm_terafab_energy_security")
        )
        for pattern in ("*.tex", "*.bib", "*.txt", "*.csv", "Makefile"):
            self.assertIn(pattern, study_rule)
        self.assertIn("prune studies/ecm_terafab_energy_security/outputs", manifest)

    def test_root_documentation_exposes_the_study_without_overclaiming(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        self.assertIn("## Terafab energy-security study", readme)
        self.assertIn("terafab-energy-security build-publication", readme)
        self.assertIn("not proof of feasibility or infeasibility", readme)
        self.assertIn("`terafab_energy_security` overlay", changelog)


if __name__ == "__main__":
    unittest.main()
