import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "terafab_ecm_publication_analysis_colab.ipynb"


def _notebook_text():
    return NOTEBOOK.read_text(encoding="utf-8")


def _notebook_json():
    return json.loads(_notebook_text())


def test_ecm_colab_notebook_exists_at_project_root_and_is_packaged():
    assert NOTEBOOK.is_file()
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    assert "include terafab_ecm_publication_analysis_colab.ipynb" in manifest


def test_ecm_colab_notebook_is_forecast_first_not_summary_only():
    text = _notebook_text()
    required_phrases = [
        "Time-resolution design",
        "High-resolution",
        "quarterly_forecast_df",
        "monthly_native_forecast_df",
        "declared_seasonal_stress_forecast_df",
        "mc_period_quantiles_df",
        "mc_margin_failure_probability_by_period_df",
        "stress_window_df",
        "Time resolution is not seasonal calibration",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_ecm_colab_notebook_uses_terafab_decision_twin_kernel():
    text = _notebook_text()
    required_phrases = [
        "from terafab_decision_twin.engine import MODEL_VERSION, run_scenario",
        "from terafab_decision_twin.schema import load_scenario, validate_scenario",
        "run_scenario",
        "validate_scenario",
        "sample_distribution",
    ]
    for phrase in required_phrases:
        assert phrase in text


def test_ecm_colab_notebook_code_cells_compile():
    notebook = _notebook_json()
    code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    assert code_cells, "Notebook must contain executable code cells."
    for index, cell in enumerate(code_cells):
        source = "".join(cell.get("source", []))
        compile(source, f"terafab_ecm_publication_analysis_colab.ipynb:cell{index}", "exec")


def test_ecm_colab_notebook_has_forecast_grade_figures_and_exports():
    text = _notebook_text()
    required_figures = [
        "fig_01_time_resolution_map",
        "fig_02_quarterly_thermodynamic_forecast",
        "fig_03_quarterly_feasibility_margin_heatmap",
        "fig_04_constraint_calendar",
        "fig_05_water_forecast_fan",
        "fig_06_thermoeconomic_trajectory",
        "fig_07_monthly_native_forecast",
        "fig_08_declared_seasonal_stress_comparison",
        "fig_09_forecast_uncertainty_envelope",
        "fig_10_period_failure_probability",
        "fig_11_worst_period_decomposition",
        "fig_12_validation_evidence_forecast_boundary",
    ]
    for figure_id in required_figures:
        assert figure_id in text
    required_exports = [
        "quarterly_forecast_all_metrics.csv",
        "quarterly_margin_calendar.csv",
        "quarterly_stress_window_ranking.csv",
        "monthly_native_forecast_all_metrics.csv",
        "declared_seasonal_stress_forecast.csv",
        "temporal_monte_carlo_quantiles.csv",
        "period_failure_probability.csv",
        "figure_manifest.csv",
    ]
    for export_name in required_exports:
        assert export_name in text
