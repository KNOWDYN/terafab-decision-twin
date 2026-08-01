from __future__ import annotations

import unittest
from pathlib import Path

from terafab_energy_security.engine import run_case
from terafab_energy_security.models import (
    EnergySecurityCase,
    ErcotInputs,
    FacilityInputs,
    ManufacturingInputs,
    NationalInputs,
    SupplyInputs,
    TargetInputs,
)
from terafab_energy_security.uncertainty import (
    convergence_diagnostic,
    dependence_aware_sensitivity,
    evaluate_resource_samples,
    generate_samples,
    independent_sobol_sensitivity,
    load_uncertainty_contract,
    summarize_resource_samples,
)


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "studies" / "ecm_terafab_energy_security" / "evidence" / "uncertainty_dependencies.json"


class UncertaintyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = load_uncertainty_contract(CONTRACT)

    def test_scrambled_sobol_design_is_reproducible(self) -> None:
        first = generate_samples(self.contract, 64)
        second = generate_samples(self.contract, 64)
        self.assertEqual(first["values"].tolist(), second["values"].tolist())

    def test_sample_count_must_be_power_of_two(self) -> None:
        with self.assertRaisesRegex(ValueError, "power of two"):
            generate_samples(self.contract, 63)

    def test_latent_correlation_is_positive_semidefinite(self) -> None:
        import numpy as np

        design = generate_samples(self.contract, 64)
        self.assertGreaterEqual(float(np.linalg.eigvalsh(design["latent_correlation"]).min()), -1e-10)

    def test_plus_and_minus_correlation_stresses_are_distinct(self) -> None:
        low = generate_samples(self.contract, 64, correlation_shift=-0.20)
        high = generate_samples(self.contract, 64, correlation_shift=0.20)
        self.assertNotEqual(low["latent_correlation"].tolist(), high["latent_correlation"].tolist())
        self.assertNotEqual(low["values"].tolist(), high["values"].tolist())

    def test_vectorized_resource_equations_match_kernel(self) -> None:
        design = generate_samples(self.contract, 2, dependence="independent")
        output = evaluate_resource_samples(design)
        values = design["values"][0]
        case = EnergySecurityCase(
            case_id="uncertainty_parity",
            year=2037,
            facility_operation_year=2037,
            target=TargetInputs(1e12, 1.0, "aggregate_rated_power", True),
            manufacturing=ManufacturingInputs(values[0], values[1], 300.0, values[2], values[3]),
            facility=FacilityInputs(values[4], values[5], values[6], values[7], "external_withdrawal_after_reuse", values[8], values[9], consumptive_fraction=0.2),
            supply=SupplyInputs(1e12, 2037),
            ercot=ErcotInputs(2037, None, None),
            national=NationalInputs(5000.0),
        )
        kernel = run_case(case)
        self.assertAlmostEqual(kernel["manufacturing"]["wafer_starts_per_year"], output["wafer_starts_per_year"][0], places=8)
        self.assertAlmostEqual(kernel["facility"]["annual_electricity_MWh"], output["facility_electricity_MWh"][0], places=8)
        self.assertAlmostEqual(kernel["facility"]["coincident_peak_load_MW"], output["facility_peak_MW"][0], places=8)
        self.assertAlmostEqual(kernel["facility"]["external_water_withdrawal_m3"], output["water_withdrawal_m3"][0], places=8)

    def test_feasibility_probability_is_not_fabricated(self) -> None:
        summary = summarize_resource_samples(evaluate_resource_samples(generate_samples(self.contract, 64)))
        self.assertIsNone(summary["feasibility_probability"])
        self.assertIn("indeterminate", summary["feasibility_probability_status"])

    def test_doubling_diagnostic_reports_only_estimable_convergence(self) -> None:
        report = convergence_diagnostic(self.contract, preliminary_count=32, confirmation_count=64)
        self.assertEqual("not_evaluable", report["feasibility_probability_convergence"])
        self.assertEqual(4, len(report["relative_changes"]))

    def test_sobol_diagnostic_does_not_substitute_for_h4_outcome(self) -> None:
        result = independent_sobol_sensitivity(self.contract, base_sample_count=128, bootstrap_replicates=20)
        self.assertEqual("indeterminate", result["H4_status"])
        self.assertEqual(10, len(result["indices"]))

    def test_dependence_aware_shapley_effects_close(self) -> None:
        result = dependence_aware_sensitivity(self.contract, sample_count=128, bootstrap_replicates=4)
        self.assertAlmostEqual(1.0, sum(row["shapley_effect"] for row in result["effects"]), places=10)
        self.assertGreater(result["surrogate_R2"], 0.5)


if __name__ == "__main__":
    unittest.main()
