import json
import unittest
from pathlib import Path

from terafab_decision_twin.engine import MODEL_VERSION
from terafab_decision_twin.evidence import CANONICAL_STATUSES

ROOT = Path(__file__).resolve().parents[1]

class ReleaseGuardTests(unittest.TestCase):
    def test_model_version_consistency(self):
        pyproject = (ROOT / "pyproject.toml").read_text()
        self.assertIn('version = "0.3.0"', pyproject)
        self.assertEqual(MODEL_VERSION, "0.3.0")
        for path in (ROOT / "scenarios").glob("*.json"):
            scenario = json.loads(path.read_text())
            self.assertEqual(scenario["metadata"]["model_version"], MODEL_VERSION)

    def test_schema_packaged_copy_matches_public_schema(self):
        self.assertEqual(
            (ROOT / "schema" / "scenario_schema.json").read_text(),
            (ROOT / "terafab_decision_twin" / "data" / "scenario_schema.json").read_text(),
        )

    def test_canonical_statuses_documented(self):
        text = (ROOT / "docs" / "EVIDENCE_POLICY.md").read_text()
        for status in CANONICAL_STATUSES:
            self.assertIn(status, text)

    def test_infographic_assets_exist(self):
        for name in [
            "terafab_one_page_infographic.svg",
            "terafab_one_page_infographic.png",
            "terafab_one_page_infographic.pdf",
        ]:
            path = ROOT / "assets" / name
            self.assertTrue(path.exists(), name)
            self.assertGreater(path.stat().st_size, 1000, name)

    def test_restricted_source_documents_absent(self):
        banned = {
            "KNOWDYN_Terafab_Intelligence_Report_2026.pdf",
            "terafab.docx",
            "Terafab_Formal_JV_Exergy_Yield_Policy_Model.md",
            "Terafab_review.md.txt",
            "terafab_decision_twin-2.md",
        }
        found = {p.name for p in ROOT.rglob("*") if p.is_file() and p.name in banned}
        self.assertEqual(found, set())

if __name__ == "__main__":
    unittest.main()
