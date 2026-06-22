import json
import unittest
from pathlib import Path

from terafab_decision_twin.engine import MODEL_VERSION
from terafab_decision_twin.evidence import CANONICAL_STATUSES

ROOT = Path(__file__).resolve().parents[1]
CURRENT_LICENSE_FILES = {
    "LICENSE.md",
    "ACADEMIC_LICENSE.md",
    "COMMERCIAL_LICENSE.md",
    "NOTICE.md",
}
OBSOLETE_PRIMARY_LICENSE_FILES = {
    "LICENSE-ACADEMIC.md",
    "LICENSE-COMMERCIAL.md",
}

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

    def test_current_license_files_are_release_metadata(self):
        for name in CURRENT_LICENSE_FILES:
            self.assertTrue((ROOT / name).is_file(), name)

        manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        for name in CURRENT_LICENSE_FILES:
            self.assertIn(name, manifest)
            self.assertIn(name, pyproject)

    def test_obsolete_license_filenames_not_publicly_referenced(self):
        public_paths = [
            ROOT / "MANIFEST.in",
            ROOT / "README.md",
            *sorted((ROOT / "docs").glob("*.md")),
        ]
        hits = []
        for path in public_paths:
            text = path.read_text(encoding="utf-8")
            for obsolete in OBSOLETE_PRIMARY_LICENSE_FILES:
                if obsolete in text:
                    hits.append(f"{path.relative_to(ROOT)} references {obsolete}")
        self.assertEqual(hits, [])

    def test_manifest_does_not_reference_missing_release_files(self):
        manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8").splitlines()
        missing = []
        for line in manifest:
            if not line.startswith("include "):
                continue
            path = ROOT / line.split(" ", 1)[1].strip()
            if not path.exists():
                missing.append(str(path.relative_to(ROOT)))
        self.assertEqual(missing, [])

    def test_release_artifact_policy_and_verifier_exist(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        checklist = ROOT / "docs" / "RELEASE_CHECKLIST.md"
        verifier = ROOT / "scripts" / "verify_release_artifacts.py"
        self.assertIn("### Release artifact policy", readme)
        self.assertTrue(checklist.is_file())
        self.assertTrue(verifier.is_file())

    def test_website_font_policy_avoids_third_party_font_hosts(self):
        fonts = (ROOT / "website" / "assets" / "fonts.css").read_text(encoding="utf-8")
        self.assertIn("Public-release font policy", fonts)
        self.assertNotIn("fonts.gstatic.com", fonts)
        self.assertNotIn("fonts.googleapis.com", fonts)

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
