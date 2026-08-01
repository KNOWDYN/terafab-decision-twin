from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "studies" / "ecm_terafab_energy_security" / "notebooks" / "terafab_energy_security_ecm.ipynb"


class EnergySecurityNotebookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
        cls.text = NOTEBOOK.read_text(encoding="utf-8")
        cls.source_text = "\n".join("".join(cell.get("source", [])) for cell in cls.payload["cells"])

    def test_notebook_is_valid_and_packaged(self) -> None:
        self.assertEqual(4, self.payload["nbformat"])
        manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
        self.assertIn("studies/ecm_terafab_energy_security *.json *.md *.py *.ipynb", manifest)

    def test_all_code_cells_compile(self) -> None:
        code_cells = [cell for cell in self.payload["cells"] if cell["cell_type"] == "code"]
        self.assertTrue(code_cells)
        for index, cell in enumerate(code_cells):
            compile("".join(cell["source"]), f"energy-security-notebook-cell-{index}", "exec")

    def test_notebook_uses_shared_calculation_apis(self) -> None:
        for phrase in (
            "run_scenario_matrix",
            "write_scenario_outputs",
            "correlation_stress_test",
            "independent_sobol_sensitivity",
            "dependence_aware_sensitivity",
            "build_publication_bundle",
            'mode=MODE',
            'publication_manifest["output_integrity"]',
        ):
            self.assertIn(phrase, self.source_text)

    def test_notebook_preserves_nonclaims_and_indeterminate_results(self) -> None:
        for phrase in (
            "never treated as a 1 TW facility electrical load",
            "no live web retrieval",
            "Feasibility probability is reported as unavailable",
            '"H1": "indeterminate',
            '"H4": sobol_report["H4_status"]',
        ):
            self.assertIn(phrase, self.source_text)


if __name__ == "__main__":
    unittest.main()
