import json
import unittest
from pathlib import Path

from strategic_simulation import (
    analyze_normal_form_game,
    build_stakeholder_decision_surface,
    run_monte_carlo,
    sample_distribution,
    simulate_reduced_order_model,
)

ROOT = Path(__file__).resolve().parents[1]


class StrategicSimulationTests(unittest.TestCase):
    def test_monte_carlo_is_reproducible_with_seed(self):
        config = json.loads((ROOT / "strategic_simulation" / "examples" / "uncertainty_baseline_2026.json").read_text())
        config["runs"] = 12
        first = run_monte_carlo(ROOT / "scenarios" / "baseline_2026.json", config, retain_runs=True)
        second = run_monte_carlo(ROOT / "scenarios" / "baseline_2026.json", config, retain_runs=True)
        self.assertEqual(first["runs_completed"], 12)
        self.assertEqual(first["runs"], second["runs"])
        self.assertIn("gate_failure_probability", first)
        self.assertIn("metric_quantiles", first)
        self.assertIn("sensitivity", first)

    def test_distribution_sampling_bounds(self):
        import random
        rng = random.Random(1)
        vals = [sample_distribution({"distribution": "triangular", "low": 1, "mode": 2, "high": 3}, rng) for _ in range(20)]
        self.assertTrue(all(1 <= value <= 3 for value in vals))

    def test_game_theory_finds_pure_equilibrium(self):
        config = json.loads((ROOT / "strategic_simulation" / "examples" / "strategic_game_2026.json").read_text())
        result = analyze_normal_form_game(config)
        self.assertEqual(result["profile_count"], 4)
        self.assertTrue(result["pure_strategy_nash_equilibria"])
        self.assertIn("conflict_index", result)

    def test_rom_trajectory_dimensions(self):
        config = json.loads((ROOT / "strategic_simulation" / "examples" / "rom_transition_2026_2030.json").read_text())
        result = simulate_reduced_order_model(config)
        self.assertEqual(result["diagnostics"]["trajectory_length"], config["steps"] + 1)
        self.assertEqual(set(result["final_state"].keys()), set(config["state_variables"]))
        self.assertFalse(result["diagnostics"]["stability_warning"])

    def test_stakeholder_surface_combines_results(self):
        mc = {"failed_probability": 0.1, "runs_completed": 10, "metric_quantiles": {"total_cost_USD": {"p50": 1}}}
        game = {"conflict_index": 0.2, "profile_count": 4}
        rom = {"diagnostics": {"stability_warning": False}, "steps": 3}
        validation = {"validation_level": "Level 2", "range_flags": []}
        surface = build_stakeholder_decision_surface(monte_carlo=mc, game=game, rom=rom, validation=validation)
        self.assertIn("board_view", surface)
        self.assertEqual(surface["recommended_phase_posture"], "stage_and_monitor")


if __name__ == "__main__":
    unittest.main()
