import copy
import unittest
from pathlib import Path

from terafab_decision_twin.schema import load_scenario, validate_scenario

ROOT = Path(__file__).resolve().parents[1]

class SchemaTests(unittest.TestCase):
    def test_baseline_validates(self):
        scenario = load_scenario(ROOT / "scenarios" / "baseline_2026.json")
        self.assertEqual(validate_scenario(scenario), [])

    def test_time_before_2026_fails(self):
        scenario = load_scenario(ROOT / "scenarios" / "baseline_2026.json")
        scenario["time"]["start_year"] = 2025
        self.assertTrue(any("start_year" in e for e in validate_scenario(scenario)))

    def test_material_input_requires_evidence_object(self):
        scenario = load_scenario(ROOT / "scenarios" / "baseline_2026.json")
        scenario["energy"]["site_electric_load_MW"] = 150
        errors = validate_scenario(scenario)
        self.assertTrue(any("evidence-coded" in e for e in errors))

    def test_invalid_control_action_fails(self):
        scenario = load_scenario(ROOT / "scenarios" / "baseline_2026.json")
        scenario["control"]["allowed_actions"] = ["build", "teleport"]
        errors = validate_scenario(scenario)
        self.assertTrue(any("allowed_actions" in e for e in errors))

if __name__ == "__main__":
    unittest.main()
