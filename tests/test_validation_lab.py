import json
import unittest
from pathlib import Path

from terafab_decision_twin.engine import run_scenario
from terafab_decision_twin.schema import load_scenario
from validation_lab import build_validation_report, validate_reference_ranges, validate_result_structure

ROOT = Path(__file__).resolve().parents[1]


class ValidationLabTests(unittest.TestCase):
    def test_structure_validation_on_baseline_result(self):
        result = run_scenario(load_scenario(ROOT / "scenarios" / "baseline_2026.json"))
        check = validate_result_structure(result)
        self.assertTrue(check["passed"])
        self.assertEqual(check["missing_result_keys"], [])

    def test_reference_ranges_flag_bad_margin(self):
        ranges = json.loads((ROOT / "validation_lab" / "reference_ranges.json").read_text())
        check = validate_reference_ranges({"minimum_firm_capacity_margin_MW": -1}, ranges)
        self.assertFalse(check["passed"])
        self.assertTrue(check["range_flags"])

    def test_validation_report_contains_level_and_calibration_gaps(self):
        result = run_scenario(load_scenario(ROOT / "scenarios" / "baseline_2026.json"))
        ranges = json.loads((ROOT / "validation_lab" / "reference_ranges.json").read_text())
        report = build_validation_report(result, ranges)
        self.assertIn("validation_level", report)
        self.assertIn("calibration_gaps", report)
        self.assertEqual(report["kind"], "validation_readiness_report")


if __name__ == "__main__":
    unittest.main()
