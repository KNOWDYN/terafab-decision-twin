import json
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path

from terafab_energy_security import (
    EnergySecurityCase,
    ErcotInputs,
    FacilityInputs,
    ManufacturingInputs,
    NationalInputs,
    SupplyInputs,
    TargetInputs,
    run_case,
)
from terafab_energy_security.equations import gross_dies_per_wafer
from terafab_energy_security.evidence import FrozenEvidence


ROOT = Path(__file__).resolve().parents[1]
STUDY_ROOT = ROOT / "studies" / "ecm_terafab_energy_security"
SYNTHETIC_CASE = STUDY_ROOT / "verification" / "synthetic_complete_case.json"


def complete_case(**overrides):
    payload = {
        "case_id": "synthetic-verification-case",
        "year": 2026,
        "facility_operation_year": 2026,
        "target": TargetInputs(
            rated_output_W_per_year=1e12,
            target_fraction=0.001,
            interpretation="aggregate_rated_power_of_good_devices_manufactured_per_year",
            interpretation_admitted=True,
        ),
        "manufacturing": ManufacturingInputs(
            module_rated_power_W=750.0,
            die_area_mm2=500.0,
            wafer_diameter_mm=300.0,
            effective_yield=0.70,
            logic_dies_per_module=4.0,
            capacity_wafers_per_month=1_000_000.0,
        ),
        "facility": FacilityInputs(
            electricity_kWh_per_wafer=2000.0,
            load_factor=0.93,
            cooling_cop=6.0,
            total_water_m3_per_wafer=8.327906,
            total_water_intensity_basis="external_withdrawal_after_reuse",
            upw_m3_per_wafer=5.678118,
            water_recycling_fraction=0.881,
            recycling_displacement_fraction=0.80,
            consumptive_fraction=0.20,
            heat_rejection_capacity_MW=100.0,
            withdrawal_capacity_m3_per_day=10_000.0,
            wastewater_capacity_m3_per_day=10_000.0,
        ),
        "supply": SupplyInputs(
            grid_interconnection_capacity_MW=200.0,
            grid_interconnection_year=2026,
            grid_accredited_addition_MW=100.0,
        ),
        "ercot": ErcotInputs(
            year=2026,
            baseline_peak_load_MW=94_159.0,
            baseline_reserve_margin_fraction=0.183,
            lole_events_per_year=0.05,
            maximum_event_duration_hours=8.0,
            highest_hourly_average_load_shed_MW=5_000.0,
            magnitude_limit_MW=13_988.0,
        ),
        "national": NationalInputs(
            annual_electricity_TWh=4422.875977,
            peak_load_MW=800_000.0,
        ),
    }
    payload.update(overrides)
    return EnergySecurityCase(**payload)


class EnergySecurityKernelTests(unittest.TestCase):
    def test_frozen_step2_evidence_loads_and_hashes(self):
        evidence = FrozenEvidence.load(STUDY_ROOT)
        self.assertEqual(len(evidence.sources), 26)
        self.assertEqual(len(evidence.parameters), 22)
        self.assertEqual(len(evidence.snapshot_hashes), 5)
        self.assertIn("regulatory_standard", evidence.snapshot("ercot_adequacy.json"))

    def test_dies_per_wafer_has_edge_loss_and_is_positive(self):
        result = gross_dies_per_wafer(300.0, 500.0)
        area_only = 3.141592653589793 * 150.0**2 / 500.0
        self.assertGreater(result, 0.0)
        self.assertLess(result, area_only)

    def test_five_stage_complete_case_is_conditionally_feasible(self):
        result = run_case(complete_case())
        self.assertEqual(result["decision"]["classification"], "conditionally_feasible")
        self.assertEqual(
            {gate["status"] for gate in result["gates"] if gate["required"]},
            {"pass"},
        )
        for stage in (
            "target_interpreter",
            "manufacturing",
            "facility",
            "deployment_and_supply",
            "ercot",
        ):
            self.assertIn(stage, result)

    def test_target_identity_and_balances_close(self):
        result = run_case(complete_case())
        self.assertLessEqual(result["manufacturing"]["rated_output_identity_residual"], 1e-8)
        self.assertLessEqual(result["facility"]["energy_balance_relative_residual"], 1e-8)
        self.assertLessEqual(result["facility"]["heat_balance_relative_residual"], 1e-8)
        self.assertLessEqual(result["facility"]["water_balance_relative_residual"], 1e-8)

    def test_total_electricity_is_not_double_counted_when_cooling_is_split(self):
        result = run_case(complete_case())
        components = result["facility"]["component_electricity_MWh"]
        self.assertAlmostEqual(sum(components.values()), result["facility"]["annual_electricity_MWh"])

    def test_external_withdrawal_basis_does_not_credit_recycling_twice(self):
        result = run_case(complete_case())
        facility = result["facility"]
        self.assertEqual(facility["total_water_intensity_basis"], "external_withdrawal_after_reuse")
        self.assertAlmostEqual(
            facility["external_water_withdrawal_m3"],
            facility["gross_water_demand_m3"],
        )

    def test_one_tw_output_is_never_assigned_as_facility_load(self):
        case = complete_case(target=TargetInputs(
            rated_output_W_per_year=1e12,
            target_fraction=1.0,
            interpretation="aggregate_rated_power_of_good_devices_manufactured_per_year",
            interpretation_admitted=True,
        ))
        result = run_case(case)
        self.assertTrue(result["target_interpreter"]["facility_load_equivalence_prohibited"])
        self.assertNotEqual(result["facility"]["coincident_peak_load_MW"], 1_000_000.0)

    def test_missing_public_capacities_produce_indeterminate_not_favorable_defaults(self):
        case = complete_case(
            manufacturing=ManufacturingInputs(
                module_rated_power_W=750.0,
                die_area_mm2=500.0,
                wafer_diameter_mm=300.0,
                effective_yield=0.70,
                logic_dies_per_module=4.0,
                capacity_wafers_per_month=None,
            ),
            facility=FacilityInputs(
                electricity_kWh_per_wafer=2000.0,
                load_factor=0.93,
                cooling_cop=6.0,
                total_water_m3_per_wafer=8.327906,
                total_water_intensity_basis="external_withdrawal_after_reuse",
                upw_m3_per_wafer=5.678118,
                water_recycling_fraction=0.881,
            ),
            supply=SupplyInputs(None, None),
            ercot=ErcotInputs(2026, 94_159.0, 0.183),
        )
        result = run_case(case)
        self.assertEqual(result["decision"]["classification"], "indeterminate")
        statuses = {gate["gate_id"]: gate["status"] for gate in result["gates"]}
        self.assertEqual(statuses["manufacturing_throughput"], "indeterminate")
        self.assertEqual(statuses["regional_adequacy"], "indeterminate")
        self.assertEqual(statuses["evidence_sufficiency"], "indeterminate")

    def test_known_throughput_shortfall_is_not_demonstrated(self):
        manufacturing = complete_case().manufacturing
        case = complete_case(manufacturing=ManufacturingInputs(
            module_rated_power_W=manufacturing.module_rated_power_W,
            die_area_mm2=manufacturing.die_area_mm2,
            wafer_diameter_mm=manufacturing.wafer_diameter_mm,
            effective_yield=manufacturing.effective_yield,
            logic_dies_per_module=manufacturing.logic_dies_per_module,
            capacity_wafers_per_month=1.0,
        ))
        result = run_case(case)
        self.assertEqual(result["decision"]["classification"], "not_demonstrated")
        gate = next(item for item in result["gates"] if item["gate_id"] == "manufacturing_throughput")
        self.assertEqual(gate["status"], "fail")
        self.assertLess(gate["margin"], 0.0)

    def test_late_interconnection_fails_schedule_and_supply(self):
        case = complete_case(supply=SupplyInputs(
            grid_interconnection_capacity_MW=200.0,
            grid_interconnection_year=2028,
            grid_accredited_addition_MW=100.0,
        ))
        result = run_case(case)
        statuses = {gate["gate_id"]: gate["status"] for gate in result["gates"]}
        self.assertEqual(statuses["schedule_precedence"], "fail")
        self.assertEqual(statuses["supply_deliverability"], "fail")

    def test_reserve_margin_is_screening_only(self):
        result = run_case(complete_case())
        self.assertTrue(result["ercot"]["screening_only"])
        self.assertFalse(result["ercot"]["reserve_margin_is_regulatory_pass"])
        expected_capacity = 94_159.0 * 1.183 + 100.0
        expected_peak = 94_159.0 + result["ercot"]["incremental_grid_coincident_peak_MW"]
        self.assertAlmostEqual(
            result["ercot"]["with_project_reserve_margin_fraction"],
            (expected_capacity - expected_peak) / expected_peak,
        )

    def test_unknown_post_2030_ercot_baseline_is_preserved(self):
        case = complete_case(
            year=2031,
            facility_operation_year=2026,
            ercot=ErcotInputs(2031, None, None),
        )
        result = run_case(case)
        self.assertFalse(result["ercot"]["official_baseline_available"])
        self.assertIsNone(result["ercot"]["with_project_reserve_margin_fraction"])
        gate = next(item for item in result["gates"] if item["gate_id"] == "regional_adequacy")
        self.assertEqual(gate["status"], "indeterminate")

    def test_peak_stress_multiplier_does_not_change_annual_energy(self):
        base = run_case(complete_case())
        stressed = run_case(complete_case(facility=replace(
            complete_case().facility,
            coincident_peak_multiplier=1.12,
        )))
        self.assertEqual(base["facility"]["annual_electricity_MWh"], stressed["facility"]["annual_electricity_MWh"])
        self.assertAlmostEqual(
            stressed["facility"]["coincident_peak_load_MW"],
            1.12 * base["facility"]["coincident_peak_load_MW"],
        )

    def test_puct_boundaries_use_correct_strictness(self):
        exact_lole = complete_case(ercot=ErcotInputs(
            2026, 94_159.0, 0.183, 0.1, 11.999, 13_987.999, magnitude_limit_MW=13_988.0
        ))
        gate = next(item for item in run_case(exact_lole)["gates"] if item["gate_id"] == "regional_adequacy")
        self.assertEqual(gate["status"], "pass")

        exact_duration = complete_case(ercot=ErcotInputs(
            2026, 94_159.0, 0.183, 0.1, 12.0, 13_000.0, magnitude_limit_MW=13_988.0
        ))
        gate = next(item for item in run_case(exact_duration)["gates"] if item["gate_id"] == "regional_adequacy")
        self.assertEqual(gate["status"], "fail")

        exact_magnitude = complete_case(ercot=ErcotInputs(
            2026, 94_159.0, 0.183, 0.1, 11.0, 13_988.0, magnitude_limit_MW=13_988.0
        ))
        gate = next(item for item in run_case(exact_magnitude)["gates"] if item["gate_id"] == "regional_adequacy")
        self.assertEqual(gate["status"], "fail")

    def test_invalid_water_intensity_fails_physical_gate(self):
        facility = complete_case().facility
        case = complete_case(facility=FacilityInputs(
            electricity_kWh_per_wafer=facility.electricity_kWh_per_wafer,
            load_factor=facility.load_factor,
            cooling_cop=facility.cooling_cop,
            total_water_m3_per_wafer=5.0,
            total_water_intensity_basis="external_withdrawal_after_reuse",
            upw_m3_per_wafer=6.0,
            water_recycling_fraction=facility.water_recycling_fraction,
            recycling_displacement_fraction=facility.recycling_displacement_fraction,
            consumptive_fraction=facility.consumptive_fraction,
            heat_rejection_capacity_MW=facility.heat_rejection_capacity_MW,
            withdrawal_capacity_m3_per_day=facility.withdrawal_capacity_m3_per_day,
            wastewater_capacity_m3_per_day=facility.wastewater_capacity_m3_per_day,
        ))
        result = run_case(case)
        gate = next(item for item in result["gates"] if item["gate_id"] == "water_capacity")
        self.assertEqual(gate["status"], "fail")

    def test_repeat_is_bitwise_json_stable(self):
        first = run_case(complete_case())
        second = run_case(complete_case())
        self.assertEqual(first["reproducibility_hash"], second["reproducibility_hash"])
        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )

    def test_dictionary_api_has_same_result(self):
        case = complete_case()
        object_result = run_case(case)
        mapping_result = run_case(json.loads(json.dumps(object_result["input"])))
        self.assertEqual(object_result, mapping_result)

    def test_cli_and_python_api_are_identical(self):
        completed = subprocess.run(
            [sys.executable, "-m", "terafab_energy_security", "run", str(SYNTHETIC_CASE), "--compact"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        cli_result = json.loads(completed.stdout)
        api_result = run_case(json.loads(SYNTHETIC_CASE.read_text(encoding="utf-8")))
        self.assertEqual(cli_result, api_result)

    def test_cli_validates_frozen_evidence(self):
        completed = subprocess.run(
            [sys.executable, "-m", "terafab_energy_security", "validate-evidence", str(STUDY_ROOT)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            json.loads(completed.stdout),
            {"status": "pass", "sources": 26, "parameters": 22, "snapshots": 5},
        )

    def test_invalid_fraction_is_rejected(self):
        case = complete_case(target=TargetInputs(1e12, 1.1, "invalid", True))
        with self.assertRaises(ValueError):
            run_case(case)

    def test_no_economic_or_policy_outputs_are_introduced(self):
        result = run_case(complete_case())
        def keys(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    yield str(key).lower()
                    yield from keys(item)
            elif isinstance(value, list):
                for item in value:
                    yield from keys(item)

        output_keys = set(keys(result))
        self.assertNotIn("electricity_cost_usd", output_keys)
        self.assertNotIn("investment_value", output_keys)
        self.assertNotIn("governance_index", output_keys)


if __name__ == "__main__":
    unittest.main()
