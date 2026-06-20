import unittest
from pathlib import Path

from terafab_decision_twin.schema import load_scenario
from terafab_decision_twin.engine import run_scenario

ROOT = Path(__file__).resolve().parents[1]

class EngineTests(unittest.TestCase):
    def test_baseline_run_is_nonhollow(self):
        result = run_scenario(load_scenario(ROOT / "scenarios" / "baseline_2026.json"))
        self.assertIn("summary", result)
        self.assertIn("time_series", result)
        self.assertGreater(result["summary"]["energy_MWh"], 0)
        self.assertGreater(result["summary"]["good_die"], 0)
        self.assertIn("gates", result)
        self.assertTrue(any(g["name"] == "thermodynamic_heat_rejection" for g in result["gates"]))

    def test_multiyear_has_quarterly_steps(self):
        result = run_scenario(load_scenario(ROOT / "scenarios" / "multi_year_2026_2030.json"))
        self.assertEqual(result["summary"]["time_steps"], 20)

    def test_stress_treats_terawatt_as_assumption(self):
        result = run_scenario(load_scenario(ROOT / "scenarios" / "terawatt_stress_2026.json"))
        self.assertIn("stress_test_assumption", result["evidence"]["status_counts"])
        self.assertEqual(result["summary"]["peak_site_load_MW"], 1_000_000)

if __name__ == "__main__":
    unittest.main()
