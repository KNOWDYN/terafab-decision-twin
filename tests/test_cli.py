import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

class CliTests(unittest.TestCase):
    def test_validate_cli(self):
        proc = subprocess.run([sys.executable, "-m", "terafab_decision_twin.cli", "scenario", "validate", str(ROOT / "scenarios" / "baseline_2026.json")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("VALID", proc.stdout)

    def test_legacy_validate_cli(self):
        proc = subprocess.run([sys.executable, "-m", "terafab_decision_twin.cli", "validate", str(ROOT / "scenarios" / "baseline_2026.json")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)

    def test_report_cli(self):
        proc = subprocess.run([sys.executable, "-m", "terafab_decision_twin.cli", "report", str(ROOT / "scenarios" / "baseline_2026.json")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("Terafab Decision Twin Report", proc.stdout)
        self.assertIn("What this scenario cannot conclude", proc.stdout)

    def test_outputs_list_cli(self):
        proc = subprocess.run([sys.executable, "-m", "terafab_decision_twin.cli", "outputs", "list"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("scalar", proc.stdout)
        self.assertIn("gate_matrix", proc.stdout)

    def test_schema_show_and_version_cli(self):
        proc = subprocess.run([sys.executable, "-m", "terafab_decision_twin.cli", "schema", "show"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("Terafab Decision Twin Scenario Schema", proc.stdout)
        proc = subprocess.run([sys.executable, "-m", "terafab_decision_twin.cli", "version"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("0.3.0", proc.stdout)


    def test_schema_show_falls_back_to_packaged_resource(self):
        from terafab_decision_twin import cli
        with mock.patch.object(cli, "SCHEMA_PATH", Path("/definitely/missing/scenario_schema.json")):
            text = cli._scenario_schema_text()
        self.assertIn("Terafab Decision Twin Scenario Schema", text)

    def test_export_cli(self):
        with tempfile.TemporaryDirectory() as td:
            proc = subprocess.run([sys.executable, "-m", "terafab_decision_twin.cli", "export", str(ROOT / "scenarios" / "baseline_2026.json"), td], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
            self.assertTrue((Path(td) / "result.json").exists())
            self.assertTrue((Path(td) / "report.md").exists())
            self.assertTrue((Path(td) / "summary.csv").exists())
            self.assertTrue((Path(td) / "gate_matrix.csv").exists())

if __name__ == "__main__":
    unittest.main()
