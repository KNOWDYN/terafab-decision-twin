"""Prespecified, data-backed figures for the ECM study bundle."""

from __future__ import annotations

import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping

from .equations import gross_dies_per_wafer
from .exports import write_csv


FIGURE_TITLES = {
    "figure_01": "Claim-to-consequence architecture",
    "figure_02": "Target-translation requirement surface",
    "figure_03": "Benchmark diagnostic and validation boundary",
    "figure_04": "Terafab realization pathways, 2026–2050",
    "figure_05": "Facility thermodynamic and water decomposition",
    "figure_06": "ERCOT incremental burden",
    "figure_07": "Supply-portfolio accredited-capacity screening",
    "figure_08": "National annual-electricity context",
    "figure_09": "Feasibility classification and gate map",
    "figure_10": "Global sensitivity and convergence",
}


def _plot_stack() -> tuple[Any, Any]:
    try:
        cache = Path(tempfile.gettempdir()) / "terafab-matplotlib-cache"
        cache.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(cache))
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("publication figures require the optional 'study' dependencies") from exc
    plt.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": 220,
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "legend.fontsize": 8,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })
    return plt, np


def _save(figure: Any, output: Path, figure_id: str) -> dict[str, Path]:
    png = output / f"{figure_id}.png"
    pdf = output / f"{figure_id}.pdf"
    figure.savefig(png, bbox_inches="tight")
    figure.savefig(pdf, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(figure)
    return {"png": png, "pdf": pdf}


def _figure_01(output: Path, *_: Any) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, _np = _plot_stack()
    nodes = [
        ("public_claim", "Public wording\n1 TW/year output", 0.08, 0.68, "reported"),
        ("interpretation", "Conditional meaning\nrated device output", 0.28, 0.68, "model identity"),
        ("throughput", "Device and wafer\nthroughput", 0.48, 0.68, "derived"),
        ("facility", "Facility electricity,\nheat and water", 0.68, 0.68, "derived"),
        ("supply", "Deployment and\nsupply portfolio", 0.48, 0.28, "scenario"),
        ("consequences", "ERCOT screening and\nUS annual context", 0.78, 0.28, "conditional"),
    ]
    edges = [
        ("public_claim", "interpretation"), ("interpretation", "throughput"),
        ("throughput", "facility"), ("facility", "supply"),
        ("supply", "consequences"), ("facility", "consequences"),
    ]
    rows = [
        {"record_type": "node", "node_id": node, "label": label.replace("\n", " "), "x": x, "y": y, "evidence_class": status}
        for node, label, x, y, status in nodes
    ] + [
        {"record_type": "edge", "source": source, "target": target}
        for source, target in edges
    ]
    positions = {node: (x, y) for node, _label, x, y, _status in nodes}
    figure, axis = plt.subplots(figsize=(10, 4.8))
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    for source, target in edges:
        start = positions[source]
        end = positions[target]
        axis.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle": "->", "lw": 1.2, "color": "#566573", "shrinkA": 45, "shrinkB": 45})
    colors = {"reported": "#d6eaf8", "model identity": "#fcf3cf", "derived": "#d5f5e3", "scenario": "#f5cba7", "conditional": "#e8daef"}
    for node, label, x, y, status in nodes:
        axis.text(x, y, label, ha="center", va="center", bbox={"boxstyle": "round,pad=0.55", "facecolor": colors[status], "edgecolor": "#34495e"})
        axis.text(x, y - 0.115, status, ha="center", va="center", fontsize=7, color="#555555")
    axis.text(0.5, 0.94, "Product output is translated into factory requirements; it is not factory electrical load", ha="center", weight="bold")
    axis.text(0.18, 0.47, "PROHIBITED: 1 TW/year → 1 TW site load", ha="center", color="#922b21", weight="bold")
    return rows, _save(figure, output, "figure_01")


def _figure_02(output: Path, config: Mapping[str, Any], *_: Any) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, np = _plot_stack()
    yields = np.linspace(0.20, 0.99, 45)
    powers = np.linspace(250.0, 1250.0, 45)
    rows = []
    values = np.empty((len(yields), len(powers)))
    dpw = gross_dies_per_wafer(300.0, float(config["central_manufacturing"]["die_area_mm2"]))
    dies_per_module = float(config["central_manufacturing"]["logic_dies_per_module"])
    for yi, effective_yield in enumerate(yields):
        for pi, module_power in enumerate(powers):
            monthly = (float(config["public_target_W_rated_per_year"]) / module_power) * dies_per_module / (dpw * effective_yield) / 12.0
            values[yi, pi] = monthly
            rows.append({
                "effective_yield_fraction": float(effective_yield),
                "module_rated_power_W": float(module_power),
                "required_wafer_starts_per_month": float(monthly),
                "region": "evidence_supported_parameter_envelope" if 0.30 <= effective_yield <= 0.95 and 350 <= module_power <= 1000 else "extrapolated_display_region",
            })
    figure, axis = plt.subplots(figsize=(7.4, 5.4))
    contour = axis.contourf(powers, yields, values / 1e6, levels=15, cmap="viridis")
    bar = figure.colorbar(contour, ax=axis)
    bar.set_label("Required wafer starts (million/month)")
    axis.add_patch(plt.Rectangle((350, 0.30), 650, 0.65, fill=False, lw=2.2, ls="--", color="white", label="Admitted parameter envelope"))
    axis.scatter([750], [0.70], marker="x", s=70, color="red", label="Central conditional case")
    axis.set(xlabel="Rated module power (W/module)", ylabel="Effective good-output yield (fraction)", title=FIGURE_TITLES["figure_02"])
    axis.legend(loc="upper right")
    return rows, _save(figure, output, "figure_02")


def _figure_03(output: Path, config: Mapping[str, Any], evidence: Any, *_: Any) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, _np = _plot_stack()
    contract = evidence.validation_contract
    central = config["central_facility"]
    rows = [
        {"quantity": "Electricity", "unit": "kWh/300-mm wafer", "assumption_min": 1000.0, "central_value": central["electricity_kWh_per_wafer"], "assumption_max": 6000.0, "comparator_value": 1979.386, "numeric_holdouts": 1, "validation_status": "insufficient_for_validated_claim", "comparator_role": "central-value source; not independent holdout"},
        {"quantity": "Water withdrawal", "unit": "m3/300-mm wafer", "assumption_min": 5.0, "central_value": central["total_water_m3_per_wafer"], "assumption_max": 10.0, "comparator_value": 8.327906, "numeric_holdouts": 1, "validation_status": "definitions_not_harmonized", "comparator_role": "central-value source; not independent holdout"},
        {"quantity": "Cooling COP", "unit": "dimensionless", "assumption_min": 4.0, "central_value": central["cooling_cop"], "assumption_max": 8.0, "comparator_value": 8.0, "numeric_holdouts": 0, "validation_status": "structural_comparison_only", "comparator_role": "calibration comparator"},
    ]
    figure, axes = plt.subplots(1, 3, figsize=(10.5, 3.6))
    for axis, row in zip(axes, rows):
        axis.hlines(0, row["assumption_min"], row["assumption_max"], color="#5d6d7e", lw=6, label="Admitted range")
        axis.scatter(row["central_value"], 0, s=70, marker="o", label="Central assumption", zorder=3)
        axis.scatter(row["comparator_value"], 0, s=75, marker="x", label="Public comparator", zorder=4)
        axis.set(yticks=[], xlabel=row["unit"], title=row["quantity"])
        axis.text(0.5, -0.32, f"Holdouts: {row['numeric_holdouts']}\n{row['validation_status']}", transform=axis.transAxes, ha="center", va="top", fontsize=8)
    axes[0].legend(loc="upper left", bbox_to_anchor=(0, 1.32), ncol=3)
    figure.suptitle("Benchmark diagnostic only — independent empirical validation threshold is not met", y=1.05, weight="bold")
    figure.text(0.5, -0.04, contract["empirical_validation_thresholds"]["insufficient_holdout_rule"], ha="center", fontsize=8)
    return rows, _save(figure, output, "figure_03")


def _figure_04(output: Path, _config: Mapping[str, Any], _evidence: Any, scenario_result: Mapping[str, Any], *_: Any) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, _np = _plot_stack()
    rows = [
        {key: row[key] for key in ("realization_pathway", "year", "target_fraction_of_public_claim", "wafer_starts_per_year", "coincident_peak_load_MW", "annual_electricity_MWh")}
        for row in scenario_result["annual_results"]
        if row["target_scale"] == "full_announced_target" and row["supply_portfolio"] == "grid_dominant" and row["stress_condition"] == "normal"
    ]
    figure, axes = plt.subplots(2, 2, figsize=(10, 7), sharex=True)
    metrics = [
        ("target_fraction_of_public_claim", "Target fraction", 1.0),
        ("wafer_starts_per_year", "Wafer starts (million/year)", 1e6),
        ("coincident_peak_load_MW", "Facility peak (GW)", 1000.0),
        ("annual_electricity_MWh", "Facility electricity (TWh/year)", 1e6),
    ]
    for pathway in ("accelerated", "reference", "delayed", "not_realized_by_2050"):
        subset = [row for row in rows if row["realization_pathway"] == pathway]
        for axis, (metric, label, scale) in zip(axes.flat, metrics):
            axis.plot([row["year"] for row in subset], [row[metric] / scale for row in subset], label=pathway.replace("_", " "))
            axis.set_ylabel(label)
            axis.grid(alpha=0.22)
    axes[0, 0].legend(ncol=2)
    axes[1, 0].set_xlabel("Year")
    axes[1, 1].set_xlabel("Year")
    figure.suptitle(FIGURE_TITLES["figure_04"], weight="bold")
    return rows, _save(figure, output, "figure_04")


def _figure_05(output: Path, config: Mapping[str, Any], _evidence: Any, scenario_result: Mapping[str, Any], *_: Any) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, _np = _plot_stack()
    row = next(item for item in scenario_result["annual_results"] if item["scenario_id"] == "full_announced_target__accelerated__grid_dominant__normal" and item["year"] == 2037)
    cop = float(config["central_facility"]["cooling_cop"])
    recycle = float(config["central_facility"]["water_recycling_fraction"])
    electricity = row["annual_electricity_MWh"]
    peak = row["coincident_peak_load_MW"]
    water = row["external_water_withdrawal_m3"]
    rows = [
        {"domain": "electricity", "component": "unallocated core facility", "value": electricity * cop / (cop + 1.0), "unit": "MWh/year", "evidence_status": "derived allocation"},
        {"domain": "electricity", "component": "cooling auxiliary", "value": electricity / (cop + 1.0), "unit": "MWh/year", "evidence_status": "derived allocation"},
        {"domain": "heat", "component": "thermal process", "value": peak * cop / (cop + 1.0), "unit": "MW_peak", "evidence_status": "derived first-law allocation"},
        {"domain": "heat", "component": "cooling auxiliary", "value": peak / (cop + 1.0), "unit": "MW_peak", "evidence_status": "derived first-law allocation"},
        {"domain": "water", "component": "consumption", "value": row["water_consumption_m3"], "unit": "m3/year", "evidence_status": "scenario-derived"},
        {"domain": "water", "component": "wastewater", "value": row["wastewater_m3"], "unit": "m3/year", "evidence_status": "scenario-derived"},
        {"domain": "water", "component": "internal recycled flow", "value": water * recycle, "unit": "m3/year", "evidence_status": "internal circulation; not credited as withdrawal avoidance"},
        {"domain": "heat", "component": "recoverable heat", "value": None, "unit": "MW_peak", "evidence_status": "not estimated; no useful-temperature or sink evidence"},
    ]
    figure, axes = plt.subplots(1, 3, figsize=(11, 4))
    for axis, domain, divisor, ylabel in zip(axes, ("electricity", "heat", "water"), (1e6, 1000.0, 1e6), ("TWh/year", "GW peak", "million m3/year")):
        subset = [item for item in rows if item["domain"] == domain and item["value"] is not None]
        axis.bar([item["component"] for item in subset], [item["value"] / divisor for item in subset])
        axis.set(ylabel=ylabel, title="Water flows (not additive)" if domain == "water" else domain.capitalize())
        axis.tick_params(axis="x", rotation=28)
    figure.suptitle("Full-target central conditional case at 2037 — not a disclosed project design", weight="bold")
    return rows, _save(figure, output, "figure_05")


def _figure_06(output: Path, _config: Mapping[str, Any], _evidence: Any, scenario_result: Mapping[str, Any], *_: Any) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, _np = _plot_stack()
    rows = []
    for row in scenario_result["annual_results"]:
        if row["scenario_id"] == "full_announced_target__accelerated__grid_dominant__normal" and row["year"] in (2029, 2030):
            rows.append({
                "year": row["year"], "incremental_peak_MW": row["net_grid_coincident_peak_MW"],
                "annual_electricity_MWh": row["annual_electricity_MWh"],
                "protocol_delta_PRM_fraction": row["protocol_delta_PRM_fraction"],
                "sb6_delta_PRM_fraction": row["sb6_delta_PRM_fraction"],
                "protocol_counterfactual_PRM_fraction": row["protocol_counterfactual_PRM_fraction"],
                "sb6_counterfactual_PRM_fraction": row["sb6_counterfactual_PRM_fraction"],
                "adequacy_status": row["regional_adequacy_status"],
            })
    years = [str(row["year"]) for row in rows]
    figure, axes = plt.subplots(1, 3, figsize=(11, 3.8))
    axes[0].bar(years, [row["incremental_peak_MW"] / 1000 for row in rows])
    axes[0].set(ylabel="Incremental grid peak (GW)", title="Coincident burden")
    axes[1].bar(years, [row["annual_electricity_MWh"] / 1e6 for row in rows])
    axes[1].set(ylabel="Electricity (TWh/year)", title="Annual energy")
    x = range(len(rows))
    axes[2].plot(x, [100 * row["protocol_delta_PRM_fraction"] for row in rows], marker="o", label="Protocol prescribed")
    axes[2].plot(x, [100 * row["sb6_delta_PRM_fraction"] for row in rows], marker="s", label="SB6 base")
    axes[2].axhline(0, color="black", lw=0.8)
    axes[2].set(xticks=list(x), xticklabels=years, ylabel="Reserve-margin change (percentage points)", title="Screening change")
    axes[2].legend()
    figure.suptitle("Official 2026–2030 counterfactuals only; reserve margin is not a regulatory adequacy pass", weight="bold")
    return rows, _save(figure, output, "figure_06")


def _figure_07(output: Path, _config: Mapping[str, Any], _evidence: Any, scenario_result: Mapping[str, Any], *_: Any) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, np = _plot_stack()
    rows = []
    for row in scenario_result["annual_results"]:
        if row["target_scale"] == "full_announced_target" and row["realization_pathway"] == "accelerated" and row["stress_condition"] == "normal" and row["year"] == 2030:
            rows.append({
                "supply_portfolio": row["supply_portfolio"],
                "facility_peak_MW": row["coincident_peak_load_MW"],
                "onsite_accredited_capacity_MW": row["onsite_accredited_capacity_MW"],
                "net_grid_peak_MW": row["net_grid_coincident_peak_MW"],
                "protocol_delta_PRM_fraction": row["protocol_delta_PRM_fraction"],
                "lole_events_per_year": None,
                "expected_unserved_energy_MWh": None,
                "adequacy_interpretation": "accredited-capacity and reserve-margin screening only",
            })
    rows.sort(key=lambda item: item["supply_portfolio"])
    labels = [row["supply_portfolio"].replace("_", "\n") for row in rows]
    x = np.arange(len(rows))
    figure, axes = plt.subplots(1, 2, figsize=(10.5, 4.3))
    axes[0].bar(x - 0.18, [row["onsite_accredited_capacity_MW"] / 1000 for row in rows], 0.36, label="Onsite accredited")
    axes[0].bar(x + 0.18, [row["net_grid_peak_MW"] / 1000 for row in rows], 0.36, label="Net grid peak")
    axes[0].set(xticks=x, xticklabels=labels, ylabel="GW", title="Capacity screening")
    axes[0].legend()
    axes[1].bar(x, [100 * row["protocol_delta_PRM_fraction"] for row in rows])
    axes[1].set(xticks=x, xticklabels=labels, ylabel="Reserve-margin change (percentage points)", title="Protocol-counterfactual screening")
    figure.suptitle("LOLE and expected unserved energy unavailable — no reliability probability is inferred", weight="bold")
    return rows, _save(figure, output, "figure_07")


def _figure_08(output: Path, _config: Mapping[str, Any], _evidence: Any, scenario_result: Mapping[str, Any], *_: Any) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, _np = _plot_stack()
    rows = []
    for row in scenario_result["annual_results"]:
        if row["target_scale"] == "full_announced_target" and row["supply_portfolio"] == "grid_dominant" and row["stress_condition"] == "normal":
            rows.append({
                "realization_pathway": row["realization_pathway"], "year": row["year"],
                "baseline_annual_electricity_share_fraction": row["national_baseline_energy_share"],
                "high_demand_annual_electricity_share_fraction": row["national_high_demand_energy_share"],
                "national_peak_share": None, "fuel_demand": None, "operational_emissions": None,
                "scope_note": "annual electricity context only; national peak, fuel, and emissions are not identified",
            })
    figure, axes = plt.subplots(1, 2, figsize=(10, 4))
    for pathway in ("accelerated", "reference", "delayed", "not_realized_by_2050"):
        subset = [row for row in rows if row["realization_pathway"] == pathway]
        axes[0].plot([row["year"] for row in subset], [100 * row["baseline_annual_electricity_share_fraction"] for row in subset], label=pathway.replace("_", " "))
        axes[1].plot([row["year"] for row in subset], [100 * row["high_demand_annual_electricity_share_fraction"] for row in subset], label=pathway.replace("_", " "))
    axes[0].set(title="AEO counterfactual baseline", ylabel="Share of US annual electricity (%)", xlabel="Year")
    axes[1].set(title="AEO high electricity demand", ylabel="Share of US annual electricity (%)", xlabel="Year")
    axes[0].legend(ncol=2)
    figure.suptitle("National annual-energy context only — not a national adequacy or fuel assessment", weight="bold")
    return rows, _save(figure, output, "figure_08")


def _figure_09(output: Path, _config: Mapping[str, Any], _evidence: Any, scenario_result: Mapping[str, Any], *_: Any) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, np = _plot_stack()
    summaries = scenario_result["trajectory_summary"]
    counts = Counter(row["classification"] for row in summaries)
    gate_rows = [row for row in scenario_result["gate_results"] if row["year"] == 2050 and row["scenario_id"].startswith("full_announced_target__")]
    scenario_ids = sorted({row["scenario_id"] for row in gate_rows})
    gate_ids = sorted({row["gate_id"] for row in gate_rows})
    status_value = {"fail": -1, "indeterminate": 0, "pass": 1}
    lookup = {(row["scenario_id"], row["gate_id"]): row["status"] for row in gate_rows}
    matrix = np.asarray([[status_value[lookup[(scenario, gate)]] for gate in gate_ids] for scenario in scenario_ids])
    rows = [
        {"record_type": "classification_count", "classification": name, "trajectory_count": count}
        for name, count in sorted(counts.items())
    ] + [
        {"record_type": "gate_status", "scenario_id": scenario, "year": 2050, "gate_id": gate, "status": lookup[(scenario, gate)], "status_code": status_value[lookup[(scenario, gate)]]}
        for scenario in scenario_ids for gate in gate_ids
    ]
    figure, axes = plt.subplots(1, 2, figsize=(13.5, 5.8), gridspec_kw={"width_ratios": [0.8, 2.0]})
    categories = ["counterfactual", "conditionally_feasible", "not_demonstrated", "indeterminate"]
    display_categories = ["Counterfactual", "Conditionally feasible", "Not demonstrated", "Indeterminate"]
    axes[0].barh(display_categories, [counts.get(category, 0) for category in categories])
    axes[0].set(xlabel="Trajectories", title="Overall classification (337 trajectories)")
    axes[0].invert_yaxis()
    from matplotlib.colors import BoundaryNorm, ListedColormap
    cmap = ListedColormap(["#c0392b", "#f4d03f", "#239b56"])
    norm = BoundaryNorm([-1.5, -0.5, 0.5, 1.5], cmap.N)
    image = axes[1].imshow(matrix, aspect="auto", cmap=cmap, norm=norm, interpolation="nearest")
    gate_labels = {
        "evidence_sufficiency": "Evidence sufficiency", "facility_energy": "Facility energy",
        "manufacturing_throughput": "Manufacturing", "national_context": "National context",
        "regional_adequacy": "Regional adequacy", "schedule_precedence": "Schedule",
        "supply_deliverability": "Supply", "target_semantics": "Target semantics",
        "thermal_capacity": "Thermal", "water_capacity": "Water",
    }
    axes[1].set(xticks=range(len(gate_ids)), xticklabels=[gate_labels[name] for name in gate_ids], yticks=[], title="Full-target gate status at 2050")
    axes[1].tick_params(axis="x", rotation=38, labelsize=8)
    for label in axes[1].get_xticklabels():
        label.set_ha("right")
    bar = figure.colorbar(image, ax=axes[1], ticks=[-1, 0, 1])
    bar.ax.set_yticklabels(["fail", "indeterminate", "pass"])
    figure.suptitle("Indeterminate is distinct from failure; no joint-pass year is identified", weight="bold")
    return rows, _save(figure, output, "figure_09")


def _figure_10(output: Path, _config: Mapping[str, Any], _evidence: Any, _scenario_result: Mapping[str, Any], uncertainty_report: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    plt, np = _plot_stack()
    sobol = {row["parameter_id"]: row for row in uncertainty_report["independent_sobol"]["indices"]}
    shapley = {row["parameter_id"]: row for row in uncertainty_report["dependence_aware"]["effects"]}
    order = [row["parameter_id"] for row in sorted(sobol.values(), key=lambda row: row["rank"])]
    rows = []
    for parameter in order:
        rows.append({
            "record_type": "sensitivity", "parameter_id": parameter,
            "sobol_first_order": sobol[parameter]["first_order"], "sobol_total_order": sobol[parameter]["total_order"],
            "sobol_total_ci95_low": sobol[parameter]["total_order_ci95_low"], "sobol_total_ci95_high": sobol[parameter]["total_order_ci95_high"],
            "dependence_aware_shapley": shapley[parameter]["shapley_effect"],
            "shapley_ci95_low": shapley[parameter]["shapley_ci95_low"], "shapley_ci95_high": shapley[parameter]["shapley_ci95_high"],
            "outcome": "log10 facility peak MW; diagnostic only",
        })
    for report in uncertainty_report["correlation_stress"]:
        for metric, change in report["relative_changes"].items():
            rows.append({
                "record_type": "convergence", "dependence": report["dependence"], "correlation_shift": report["correlation_shift"],
                "metric": metric, "relative_change": change, "limit": report["convergence_limit"],
                "preliminary_sample_count": report["preliminary_sample_count"], "confirmation_sample_count": report["confirmation_sample_count"],
            })
    figure, axes = plt.subplots(1, 2, figsize=(12, 6))
    y = np.arange(len(order))
    total = np.asarray([sobol[item]["total_order"] for item in order])
    shap = np.asarray([shapley[item]["shapley_effect"] for item in order])
    axes[0].barh(y - 0.2, total, 0.4, label="Independent Sobol total")
    axes[0].barh(y + 0.2, shap, 0.4, label="Correlated Shapley")
    axes[0].set(yticks=y, yticklabels=[item.replace("P_", "").replace("_", " ").lower() for item in order], xlabel="Normalized sensitivity allocation", title="Conditional facility-peak diagnostic")
    axes[0].invert_yaxis()
    axes[0].legend()
    convergence = [row for row in rows if row["record_type"] == "convergence"]
    convergence_cases = []
    for dependence, shift in (("independent", 0.0), ("correlated", -0.2), ("correlated", 0.0), ("correlated", 0.2)):
        case = [row for row in convergence if row["dependence"] == dependence and row["correlation_shift"] == shift]
        convergence_cases.append({"label": "Independent" if dependence == "independent" else f"Correlated {shift:+.1f}", "maximum": max(row["relative_change"] for row in case)})
    labels = [row["label"] for row in convergence_cases]
    axes[1].bar(range(len(convergence_cases)), [100 * row["maximum"] for row in convergence_cases])
    axes[1].axhline(1.0, color="#c0392b", ls="--", label="1% limit")
    axes[1].set(xticks=range(len(labels)), xticklabels=labels, ylabel="Maximum doubling relative change (%)", title="Sobol sample convergence")
    axes[1].tick_params(axis="x", rotation=25)
    axes[1].legend()
    figure.suptitle("Resource sensitivity does not substitute for the indeterminate joint-feasibility H4 outcome", weight="bold")
    return rows, _save(figure, output, "figure_10")


FIGURE_BUILDERS: dict[str, Callable[..., tuple[list[dict[str, Any]], dict[str, Path]]]] = {
    "figure_01": _figure_01,
    "figure_02": _figure_02,
    "figure_03": _figure_03,
    "figure_04": _figure_04,
    "figure_05": _figure_05,
    "figure_06": _figure_06,
    "figure_07": _figure_07,
    "figure_08": _figure_08,
    "figure_09": _figure_09,
    "figure_10": _figure_10,
}


def build_publication_figures(
    output_directory: str | Path,
    config: Mapping[str, Any],
    evidence: Any,
    scenario_result: Mapping[str, Any],
    uncertainty_report: Mapping[str, Any],
) -> dict[str, dict[str, Path]]:
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    artifacts: dict[str, dict[str, Path]] = {}
    for figure_id, builder in FIGURE_BUILDERS.items():
        rows, images = builder(output, config, evidence, scenario_result, uncertainty_report)
        data_path = write_csv(output / f"{figure_id}_data.csv", rows)
        artifacts[figure_id] = {"data": data_path, **images}
    return artifacts
