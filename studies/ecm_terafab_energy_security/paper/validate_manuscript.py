#!/usr/bin/env python3
"""Validate ECM structure, disclosure boundaries, and quantitative traceability."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from pathlib import Path


PAPER = Path(__file__).resolve().parent
STUDY = PAPER.parent
DEFAULT_PUBLICATION = STUDY / "outputs" / "final" / "publication"


class ManuscriptValidationError(RuntimeError):
    """Raised when a submission or traceability contract is violated."""


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise ManuscriptValidationError(message)


def _read(path: Path) -> str:
    _assert(path.is_file(), f"required file is missing: {path}")
    return path.read_text(encoding="utf-8")


def _latex_to_words(value: str) -> list[str]:
    value = re.sub(r"%.*", " ", value)
    value = re.sub(r"\\(?:cite|ref|eqref|label|url|code)\{[^}]*\}", " ", value)
    value = re.sub(r"\\[A-Za-z*]+(?:\[[^]]*\])?", " ", value)
    value = re.sub(r"[{}$^_\\]", " ", value)
    return re.findall(r"[A-Za-z0-9]+(?:[\u2010-\u2015'-][A-Za-z0-9]+)*", value)


def validate_structure() -> dict[str, object]:
    main = _read(PAPER / "main.tex")
    tables = _read(PAPER / "tables_main.tex")
    supplement = _read(PAPER / "supplement.tex")
    highlights = [
        re.sub(r"^\d+\.\s*", "", line.strip())
        for line in _read(PAPER / "highlights.txt").splitlines()
        if line.strip()
    ]
    bib = _read(PAPER / "references.bib")

    abstract_match = re.search(
        r"\\begin\{abstract\}(.*?)\\end\{abstract\}", main, re.DOTALL
    )
    _assert(abstract_match is not None, "abstract is missing")
    abstract_words = len(_latex_to_words(abstract_match.group(1)))
    _assert(abstract_words <= 250, f"abstract has {abstract_words} words; maximum is 250")

    keyword_match = re.search(
        r"\\textbf\{Keywords:\}\s*(.*?)\\section", main, re.DOTALL
    )
    _assert(keyword_match is not None, "keyword line is missing")
    keyword_text = re.sub(r"\s+", " ", keyword_match.group(1)).strip()
    keywords = [item.strip() for item in keyword_text.split(";") if item.strip()]
    _assert(1 <= len(keywords) <= 7, f"found {len(keywords)} keywords; expected 1--7")

    _assert(3 <= len(highlights) <= 5, "ECM requires 3--5 highlights")
    highlight_lengths = [len(item) for item in highlights]
    _assert(
        all(length <= 85 for length in highlight_lengths),
        f"highlight lengths exceed 85 characters: {highlight_lengths}",
    )

    combined = main + "\n" + tables
    citation_keys: set[str] = set()
    for group in re.findall(r"\\cite[a-zA-Z*]*\{([^}]+)\}", combined):
        citation_keys.update(key.strip() for key in group.split(","))
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    missing_citations = citation_keys - bib_keys
    _assert(not missing_citations, f"missing bibliography keys: {sorted(missing_citations)}")
    _assert(not bib_keys - citation_keys, f"uncited bibliography keys: {sorted(bib_keys - citation_keys)}")

    for number in range(1, 11):
        token = f"figure_{number:02d}.pdf"
        _assert(token in main, f"manuscript does not include {token}")
    for label in ("claims", "equations", "evidence", "matrix", "principal", "verification"):
        _assert(f"\\label{{tab:{label}}}" in tables, f"Table label tab:{label} is missing")

    required_boundaries = (
        "prospective conditional constraint analysis",
        "not proof of infeasibility",
        "not a validated digital twin",
        "not verified Terafab operating facts",
        "source-available, not open source",
        "no live web retrieval",
        "LOLE and expected unserved energy",
        "All 336 nonzero trajectories remain indeterminate",
    )
    searchable = (main + supplement + _read(PAPER / "README.md")).lower()
    for phrase in required_boundaries:
        _assert(phrase.lower() in searchable, f"required scientific boundary is missing: {phrase}")

    disclosure = main.find("Declaration of generative AI and AI-assisted technologies")
    bibliography = main.find("\\bibliographystyle")
    _assert(0 <= disclosure < bibliography, "AI declaration must precede references")
    prohibited_assertions = (
        "Terafab is infeasible",
        "Terafab is feasible",
        "validated digital twin of Terafab",
        "official Terafab facility load",
    )
    for assertion in prohibited_assertions:
        _assert(assertion.lower() not in main.lower(), f"prohibited assertion found: {assertion}")

    return {
        "abstract_words": abstract_words,
        "keyword_count": len(keywords),
        "highlight_count": len(highlights),
        "highlight_lengths": highlight_lengths,
        "citation_count": len(citation_keys),
        "figure_count": 10,
        "table_count": 6,
    }


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _close(actual: float, expected: float) -> bool:
    return math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12)


def validate_claims(publication: Path) -> dict[str, object]:
    _assert(publication.is_dir(), f"publication bundle is missing: {publication}")
    trace_rows = _csv_rows(PAPER / "claim_traceability.csv")
    expected = {row["claim_id"]: float(row["locked_value"]) for row in trace_rows}
    for row in trace_rows:
        _assert((publication / row["artifact"]).is_file(), f"claim artifact missing: {row['artifact']}")

    figure4 = _csv_rows(publication / "figures" / "figure_04_data.csv")
    central_2037 = next(
        row for row in figure4 if row["realization_pathway"] == "accelerated" and row["year"] == "2037"
    )
    actual: dict[str, float] = {"C01": float(central_2037["wafer_starts_per_year"])}

    table5 = _csv_rows(publication / "tables" / "table_05_principal_results_by_pathway.csv")
    central = next(
        row
        for row in table5
        if row["realization_pathway"] == "accelerated"
        and row["supply_portfolio"] == "grid_dominant"
        and row["year"] == "2050"
    )
    actual.update(
        {
            "C02": float(central["annual_electricity_MWh"]),
            "C03": float(central["coincident_peak_load_MW"]),
            "C04": float(central["external_water_withdrawal_m3"]),
        }
    )

    figure8 = _csv_rows(publication / "figures" / "figure_08_data.csv")
    national = next(
        row for row in figure8 if row["realization_pathway"] == "accelerated" and row["year"] == "2037"
    )
    actual["C05"] = float(national["baseline_annual_electricity_share_fraction"])

    uncertainty = json.loads(_read(publication / "raw" / "uncertainty_report.json"))
    baseline = next(
        entry
        for entry in uncertainty["correlation_stress"]
        if entry["dependence"] == "correlated" and float(entry["correlation_shift"]) == 0.0
    )["confirmation"]
    actual.update(
        {
            "C06": float(baseline["wafer_starts_per_year_median"]),
            "C07": float(baseline["facility_electricity_MWh_median"]),
            "C08": float(baseline["facility_peak_MW_p95"]),
            "C09": float(baseline["water_withdrawal_m3_p95"]),
        }
    )

    manifest = json.loads(_read(publication / "publication_manifest.json"))
    actual["C10"] = float(manifest["scenario_manifest"]["classification_counts"]["indeterminate"])

    gate_rows = _csv_rows(publication / "raw" / "scenarios" / "gate_results.csv")
    actual.update(
        {
            "C11": float(sum(row["status"] == "pass" for row in gate_rows)),
            "C12": float(sum(row["status"] == "fail" for row in gate_rows)),
            "C13": float(sum(row["status"] == "indeterminate" for row in gate_rows)),
        }
    )

    table6 = _csv_rows(publication / "tables" / "table_06_verification_and_validation.csv")
    convergence = next(row for row in table6 if row["check_id"] == "uncertainty_convergence")
    actual["C14"] = float(convergence["value"])

    figure10 = _csv_rows(publication / "figures" / "figure_10_data.csv")
    sensitivity = [row for row in figure10 if row["record_type"] == "sensitivity"]
    total_order = sorted((float(row["sobol_total_order"]) for row in sensitivity), reverse=True)
    actual["C15"] = sum(total_order[:2]) / sum(total_order)

    for claim_id, locked in expected.items():
        _assert(
            claim_id in actual and _close(actual[claim_id], locked),
            f"traceability mismatch for {claim_id}: expected {locked}, got {actual.get(claim_id)}",
        )

    _assert(manifest["claim_level"] == "prospective_conditional_constraint_analysis", "manifest claim level changed")
    _assert(manifest["output_integrity"]["live_web_retrieval"] is False, "final reproduction uses live web")
    _assert(manifest["hypothesis_disposition"] == {key: "indeterminate" for key in ("H1", "H2", "H3", "H4")}, "hypothesis disposition changed")

    return {"traceable_claims": len(actual), "gate_rows": len(gate_rows)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publication-dir", type=Path, default=DEFAULT_PUBLICATION)
    parser.add_argument("--structure-only", action="store_true")
    args = parser.parse_args(argv)

    try:
        report = {"structure": validate_structure()}
        if not args.structure_only:
            report["claims"] = validate_claims(args.publication_dir.resolve())
    except ManuscriptValidationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(json.dumps({"status": "pass", **report}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
