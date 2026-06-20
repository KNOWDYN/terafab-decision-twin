import unittest
from terafab_decision_twin.models.first_law import heat_rejection_required_MW
from terafab_decision_twin.models.entropy import heat_transfer_entropy_generation_MW_per_K
from terafab_decision_twin.models.exergy import exergy_destroyed_MW
from terafab_decision_twin.models.water import permit_margin_m3_per_day
from terafab_decision_twin.models.manufacturing import effective_yield, good_die_output
from terafab_decision_twin.models.economics import capital_recovery_factor

class EquationTests(unittest.TestCase):
    def test_heat_rejection_tracks_load(self):
        self.assertAlmostEqual(heat_rejection_required_MW(100, 0.98, 2), 100)

    def test_entropy_nonnegative(self):
        self.assertGreaterEqual(heat_transfer_entropy_generation_MW_per_K(100, 320, 300), 0)

    def test_exergy_destroyed(self):
        self.assertGreater(exergy_destroyed_MW(298.15, 0.1), 0)

    def test_water_permit_margin(self):
        self.assertAlmostEqual(permit_margin_m3_per_day(3650, 20), 10)

    def test_yield_and_good_die(self):
        y = effective_yield(0.8, 0.1, 0.9, 0.9)
        self.assertTrue(0 < y <= 1)
        self.assertGreater(good_die_output(100, 500, y), 0)

    def test_crf_positive(self):
        self.assertGreater(capital_recovery_factor(0.08, 20), 0)

if __name__ == "__main__":
    unittest.main()
