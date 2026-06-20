import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class CliTests(unittest.TestCase):
    def test_validate_cli(self):
        proc = subprocess.run([sys.executable, "-m", "terafab_decision_twin.cli", "validate", str(ROOT / "scenarios" / "baseline_2026.json")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("VALID", proc.stdout)

    def test_report_cli(self):
        proc = subprocess.run([sys.executable, "-m", "terafab_decision_twin.cli", "report", str(ROOT / "scenarios" / "baseline_2026.json")], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("Terafab Decision Twin Report", proc.stdout)

if __name__ == "__main__":
    unittest.main()
