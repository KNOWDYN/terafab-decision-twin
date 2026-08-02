from __future__ import annotations

import contextlib
import csv
import io
import json
import tempfile
import unittest
from pathlib import Path

from terafab_energy_security.cli import main as cli_main
from terafab_energy_security.evidence import FrozenEvidence
from terafab_energy_security.pathways import (
    build_scenario_matrix,
    load_scenario_config,
    run_scenario_matrix,
)


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "studies" / "ecm_terafab_energy_security"


class ScenarioPathwayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_scenario_config(STUDY / "scenarios" / "scenario_matrix.json")
        cls.evidence = FrozenEvidence.load(STUDY)

    def _run(self, *scenario_ids: str):
        return run_scenario_matrix(self.config, self.evidence, scenario_ids)

    def test_matrix_is_locked_and_complete(self) -> None:
        matrix = build_scenario_matrix(self.config)
        self.assertEqual(337, len(matrix))
        self.assertEqual(224, sum(row["numerical_status"] == "indeterminate_target_scale" for row in matrix))
        self.assertEqual(1, sum(row["target_scale"] == "no_build" for row in matrix))
        self.assertEqual("indeterminate", self.config["target_semantic_branches"]["other_publicly_undefined_meaning"]["numerical_status"])

    def test_unknown_phase_scales_are_not_silently_quantified(self) -> None:
        result = self._run("research_fab__accelerated__grid_dominant__normal")
        self.assertEqual([], result["annual_results"])
        self.assertEqual("indeterminate", result["trajectory_summary"][0]["classification"])
        self.assertIn("no defensible public numerical value", result["trajectory_summary"][0]["reason"])

    def test_no_build_counterfactual_has_zero_increment(self) -> None:
        result = self._run("no_build__counterfactual")
        self.assertEqual(25, len(result["annual_results"]))
        for row in result["annual_results"]:
            self.assertEqual(0.0, row["annual_electricity_MWh"])
            self.assertEqual(0.0, row["coincident_peak_load_MW"])
            self.assertEqual("not_applicable_counterfactual", row["classification"])

    def test_active_path_has_one_row_per_year_and_ten_gates(self) -> None:
        scenario = "full_announced_target__accelerated__grid_dominant__normal"
        result = self._run(scenario)
        self.assertEqual(25, len(result["annual_results"]))
        self.assertEqual(22, sum(row["row_type"] == "active_conditional_case" for row in result["annual_results"]))
        self.assertEqual(220, len(result["gate_results"]))

    def test_post_2030_ercot_baseline_is_unknown_not_extrapolated(self) -> None:
        scenario = "full_announced_target__accelerated__grid_dominant__normal"
        row = next(row for row in self._run(scenario)["annual_results"] if row["year"] == 2031)
        self.assertIsNone(row["protocol_counterfactual_peak_MW"])
        self.assertIsNone(row["protocol_counterfactual_PRM_fraction"])
        self.assertEqual("indeterminate", row["regional_adequacy_status"])

    def test_protocol_and_sb6_counterfactuals_remain_separate(self) -> None:
        scenario = "full_announced_target__accelerated__grid_dominant__normal"
        row = next(row for row in self._run(scenario)["annual_results"] if row["year"] == 2029)
        self.assertNotEqual(row["protocol_counterfactual_PRM_fraction"], row["sb6_counterfactual_PRM_fraction"])

    def test_yield_stress_increases_required_throughput(self) -> None:
        normal = "full_announced_target__accelerated__grid_dominant__normal"
        stress = "full_announced_target__accelerated__grid_dominant__yield_underperformance"
        result = self._run(normal, stress)
        row = {(item["scenario_id"], item["year"]): item for item in result["annual_results"]}
        ratio = row[(stress, 2037)]["wafer_starts_per_year"] / row[(normal, 2037)]["wafer_starts_per_year"]
        self.assertAlmostEqual(1.0 / 0.75, ratio, places=12)

    def test_cooling_and_water_stress_fails_both_capacity_gates(self) -> None:
        scenario = "full_announced_target__accelerated__grid_dominant__cooling_or_water_constraint"
        gates = self._run(scenario)["gate_results"]
        statuses = {(row["year"], row["gate_id"]): row["status"] for row in gates}
        self.assertEqual("fail", statuses[(2037, "thermal_capacity")])
        self.assertEqual("fail", statuses[(2037, "water_capacity")])

    def test_infrastructure_delay_exposes_schedule_precedence_failure(self) -> None:
        scenario = "full_announced_target__accelerated__firm_onsite__infrastructure_delay"
        gates = self._run(scenario)["gate_results"]
        status = next(row["status"] for row in gates if row["year"] == 2029 and row["gate_id"] == "schedule_precedence")
        self.assertEqual("fail", status)

    def test_firm_outage_removes_accredited_firm_capacity(self) -> None:
        normal = "full_announced_target__accelerated__firm_onsite__normal"
        outage = "full_announced_target__accelerated__firm_onsite__firm_supply_outage"
        result = self._run(normal, outage)
        row = {(item["scenario_id"], item["year"]): item for item in result["annual_results"]}
        self.assertGreater(row[(normal, 2037)]["onsite_accredited_capacity_MW"], 0.0)
        self.assertEqual(0.0, row[(outage, 2037)]["onsite_accredited_capacity_MW"])
        self.assertGreater(row[(outage, 2037)]["net_grid_coincident_peak_MW"], row[(normal, 2037)]["net_grid_coincident_peak_MW"])

    def test_full_matrix_is_deterministic(self) -> None:
        scenario = "full_announced_target__reference__renewable_storage_grid__summer_peak"
        first = self._run(scenario)
        second = self._run(scenario)
        self.assertEqual(first, second)

    def test_cli_exports_the_same_selected_trajectory(self) -> None:
        scenario = "full_announced_target__reference__renewable_storage_grid__summer_peak"
        expected = self._run(scenario)
        with tempfile.TemporaryDirectory() as directory, contextlib.redirect_stdout(io.StringIO()):
            status = cli_main([
                "run-matrix", str(STUDY), "--output-directory", directory,
                "--scenario-id", scenario,
            ])
            self.assertEqual(0, status)
            manifest = json.loads((Path(directory) / "run_manifest.json").read_text(encoding="utf-8"))
            with (Path(directory) / "annual_results.csv").open(encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
        self.assertEqual(expected["manifest"], manifest)
        self.assertEqual(
            [row["reproducibility_hash"] for row in expected["annual_results"]],
            [row["reproducibility_hash"] for row in rows],
        )


if __name__ == "__main__":
    unittest.main()
