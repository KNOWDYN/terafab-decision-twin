from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from terafab_energy_security.publication import build_publication_bundle


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "studies" / "ecm_terafab_energy_security"


def _csv_rows(path: Path):
    with path.open(encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


class PublicationBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name)
        cls.result = build_publication_bundle(STUDY, cls.output, mode="test")
        cls.manifest = json.loads((cls.output / "publication_manifest.json").read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_all_prespecified_figures_and_tables_exist(self) -> None:
        integrity = self.manifest["output_integrity"]
        self.assertEqual(10, integrity["generated_figure_count"])
        self.assertEqual(10, integrity["figure_data_file_count"])
        self.assertEqual(6, integrity["generated_table_count"])
        self.assertTrue(integrity["every_figure_has_machine_readable_data"])
        for record in self.manifest["figures"]:
            self.assertGreater((self.output / record["artifacts"]["png"]["path"]).stat().st_size, 5000)
            self.assertGreater((self.output / record["artifacts"]["pdf"]["path"]).stat().st_size, 1000)
            self.assertGreater((self.output / record["artifacts"]["data"]["path"]).stat().st_size, 20)

    def test_every_limited_replacement_is_declared(self) -> None:
        status = {record["figure_id"]: record["status"] for record in self.manifest["figures"]}
        self.assertEqual("replacement_limited_diagnostic", status["figure_03"])
        self.assertEqual("replacement_screening_only", status["figure_07"])
        self.assertEqual("replacement_context_only", status["figure_08"])
        self.assertTrue(self.manifest["output_integrity"]["figure_replacements_are_declared"])

    def test_claim_and_classification_boundaries_are_preserved(self) -> None:
        self.assertEqual("prospective_conditional_constraint_analysis", self.manifest["claim_level"])
        self.assertEqual("validated_digital_twin_of_Terafab", self.manifest["prohibited_claim"])
        self.assertEqual({"counterfactual": 1, "indeterminate": 336}, self.manifest["scenario_manifest"]["classification_counts"])
        self.assertEqual({"H1": "indeterminate", "H2": "indeterminate", "H3": "indeterminate", "H4": "indeterminate"}, self.manifest["hypothesis_disposition"])

    def test_public_claim_table_prohibits_factory_load_equivalence(self) -> None:
        rows = _csv_rows(self.output / "tables" / "table_01_public_claims_and_interpretations.csv")
        self.assertEqual(2, len(rows))
        self.assertIn("facility electrical load", rows[0]["excluded_interpretations"])
        self.assertEqual("indeterminate", rows[1]["numerical_status"])

    def test_validation_table_does_not_invent_empirical_accuracy(self) -> None:
        rows = _csv_rows(self.output / "tables" / "table_06_verification_and_validation.csv")
        validation = next(row for row in rows if row["check_id"] == "independent_validation")
        self.assertEqual("insufficient", validation["status"])
        self.assertEqual("False", validation["empirical_metric_available"])

    def test_principal_results_are_conditional_and_indeterminate(self) -> None:
        rows = _csv_rows(self.output / "tables" / "table_05_principal_results_by_pathway.csv")
        self.assertEqual(16, len(rows))
        self.assertEqual({"indeterminate"}, {row["classification"] for row in rows})
        self.assertEqual({"rated_device_output"}, {row["target_semantics"] for row in rows})

    def test_limited_figure_data_contains_null_not_fabricated_metrics(self) -> None:
        adequacy = _csv_rows(self.output / "figures" / "figure_07_data.csv")
        self.assertTrue(all(row["lole_events_per_year"] == "" for row in adequacy))
        self.assertTrue(all(row["expected_unserved_energy_MWh"] == "" for row in adequacy))
        national = _csv_rows(self.output / "figures" / "figure_08_data.csv")
        self.assertTrue(all(row["fuel_demand"] == "" and row["operational_emissions"] == "" for row in national))

    def test_ercot_figure_stops_at_official_horizon(self) -> None:
        rows = _csv_rows(self.output / "figures" / "figure_06_data.csv")
        self.assertEqual({"2029", "2030"}, {row["year"] for row in rows})
        self.assertEqual({"indeterminate"}, {row["adequacy_status"] for row in rows})

    def test_manifest_artifact_hashes_are_current(self) -> None:
        import hashlib

        for figure in self.manifest["figures"]:
            for artifact in figure["artifacts"].values():
                path = self.output / artifact["path"]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), artifact["sha256"])

    def test_reproduction_command_is_portable_and_sources_are_hashed(self) -> None:
        command = self.manifest["reproduction"]["cli"]
        self.assertIn("studies/ecm_terafab_energy_security", command)
        self.assertNotIn(str(ROOT), command)
        self.assertEqual(
            64,
            len(self.manifest["input_hashes"]["source_registry_sha256"]),
        )


if __name__ == "__main__":
    unittest.main()
