import unittest
from pathlib import Path

from terafab_decision_twin.schema import load_scenario
from terafab_decision_twin.engine import run_scenario

ROOT = Path(__file__).resolve().parents[1]

class EngineTests(unittest.TestCase):
    def test_baseline_run_is_implemented(self):
        result = run_scenario(load_scenario(ROOT / "scenarios" / "baseline_2026.json"))
        self.assertIn("summary", result)
        self.assertIn("time_series", result)
        self.assertGreater(result["summary"]["energy_MWh"], 0)
        self.assertGreater(result["summary"]["good_die"], 0)
        self.assertIn("gates", result)
        self.assertTrue(any(g["name"] == "thermodynamic_heat_rejection" for g in result["gates"]))
        self.assertIn("output_records", result)
        self.assertGreater(len(result["output_records"]), 20)

    def test_multiyear_has_quarterly_steps(self):
        result = run_scenario(load_scenario(ROOT / "scenarios" / "multi_year_2026_2030.json"))
        self.assertEqual(result["summary"]["time_steps"], 20)
        self.assertEqual(len(result["matrices"]["gate_matrix"]), 20 * len(result["gates"]))

    def test_stress_treats_terawatt_as_assumption(self):
        result = run_scenario(load_scenario(ROOT / "scenarios" / "terawatt_stress_2026.json"))
        self.assertIn("stress_test_assumption", result["evidence"]["status_counts"])
        self.assertEqual(result["summary"]["peak_site_load_MW"], 1_000_000)
        self.assertEqual(result["summary"]["one_terawatt_status"], "stress_test_assumption")

    def test_unknown_input_is_not_silently_defaulted(self):
        scenario = load_scenario(ROOT / "scenarios" / "baseline_2026.json")
        scenario["energy"]["site_electric_load_MW"]["value"] = None
        scenario["energy"]["site_electric_load_MW"]["status"] = "unknown"
        result = run_scenario(scenario)
        self.assertTrue(result["unknowns"]["underdetermined"])
        self.assertTrue(any(g["name"] == "unknown_input_discipline" and not g["passed"] for g in result["gates"]))
        self.assertIsNone(result["summary"]["cost_per_good_die_USD"])

    def test_output_records_have_required_metadata(self):
        result = run_scenario(load_scenario(ROOT / "scenarios" / "baseline_2026.json"))
        rec = result["output_records"][0]
        for key in ["name", "value", "unit", "kind", "scenario_id", "source_status", "equation_ref", "assumptions_used", "warning_flags", "reproducibility_hash"]:
            self.assertIn(key, rec)

if __name__ == "__main__":
    unittest.main()
