import unittest
from terafab_decision_twin.models.first_law import heat_rejection_required_MW
from terafab_decision_twin.models.entropy import heat_transfer_entropy_generation_MW_per_K
from terafab_decision_twin.models.exergy import exergy_destroyed_MW
from terafab_decision_twin.models.water import permit_margin_m3_per_day, permit_margin_with_reserve_m3_per_day
from terafab_decision_twin.models.cooling import heat_rejection_margin_with_reserve_MW
from terafab_decision_twin.models.power import firm_capacity_margin_MW
from terafab_decision_twin.models.manufacturing import effective_yield, good_die_output
from terafab_decision_twin.models.economics import capital_recovery_factor
from terafab_decision_twin.cleanroom import CleanroomState, cleanroom_readiness
from terafab_decision_twin.contamination import ContaminationState, contamination_readiness
from terafab_decision_twin.packaging import PackagingState, packaging_readiness
from terafab_decision_twin.qualification import QualificationState, qualification_readiness, qualification_gate
from terafab_decision_twin.evidence_bayes import bayes_update, posterior_to_status

class EquationTests(unittest.TestCase):
    def test_heat_rejection_tracks_load(self):
        self.assertAlmostEqual(heat_rejection_required_MW(100, 0.98, 2), 100)

    def test_entropy_nonnegative(self):
        self.assertGreaterEqual(heat_transfer_entropy_generation_MW_per_K(100, 320, 300), 0)

    def test_exergy_destroyed(self):
        self.assertGreater(exergy_destroyed_MW(298.15, 0.1), 0)

    def test_water_permit_margin(self):
        self.assertAlmostEqual(permit_margin_m3_per_day(3650, 20), 10)

    def test_reserve_margin_conventions_are_distinct(self):
        self.assertAlmostEqual(firm_capacity_margin_MW(115, 100, 0.15), 0)
        self.assertAlmostEqual(heat_rejection_margin_with_reserve_MW(100, 90, 0.10), 0)
        self.assertAlmostEqual(permit_margin_with_reserve_m3_per_day(90, 100, 0.10, 1), 0)

    def test_yield_and_good_die(self):
        y = effective_yield(0.8, 0.1, 0.9, 0.9)
        self.assertTrue(0 < y <= 1)
        self.assertGreater(good_die_output(100, 500, y), 0)

    def test_crf_positive(self):
        self.assertGreater(capital_recovery_factor(0.08, 20), 0)

    def test_formal_modules_bounds(self):
        self.assertTrue(0 <= cleanroom_readiness(CleanroomState(80, 0.99, 0.1, 0.95)) <= 1)
        self.assertTrue(0 <= contamination_readiness(ContaminationState(0.9, 0.9, 0.1)) <= 1)
        self.assertTrue(0 <= packaging_readiness(PackagingState(0.8, 0.8, 0.8)) <= 1)
        q = qualification_readiness(QualificationState(0.8, 0.85, 0.9, 0.95))
        self.assertTrue(qualification_gate(q, 0.75))

    def test_bayesian_evidence_does_not_auto_verify(self):
        update = bayes_update(0.99, 0.99, 0.01)
        self.assertEqual(posterior_to_status(update.posterior_probability), "reported")

if __name__ == "__main__":
    unittest.main()
