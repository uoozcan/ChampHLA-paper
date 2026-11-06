"""The post hoc substitution table keeps fixed denominators and never moves the primary."""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_scorer():
    spec = importlib.util.spec_from_file_location(
        "score_reference_substitution_posthoc",
        ROOT / "scripts" / "score_reference_substitution_posthoc.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _locus(subject, method, first, second, status="callable"):
    return {
        "modality": "wes", "subject": subject, "gene": "A", "method": method,
        "call_status": status, "allele1": first, "allele2": second,
        "truth_allele1": "A*01:01", "truth_allele2": "A*02:01",
    }


def test_flagged_loci_use_the_corrected_value_and_other_loci_the_reference():
    scorer = load_scorer()
    rows = [
        _locus("S1", "vote", "A*01:01", "A*03:01"),
        _locus("S2", "vote", "A*02:01", "A*01:01"),
        _locus("S1", "caller", "A*01:01", "A*02:01"),
        _locus("S2", "caller", "", "", status="no_call"),
    ]
    flagged = [{"modality": "wes", "subject": "S1", "gene": "A",
                "flagged_second_typing": "A*01:01+A*03:01"}]
    results = {row["method"]: row for row in scorer.score(rows, flagged)}
    assert results["vote"]["exact_correct"] == 1
    assert results["vote"]["substituted_correct"] == 2
    assert results["caller"]["exact_correct"] == 1
    assert results["caller"]["substituted_correct"] == 0
    assert results["caller"]["loci"] == 2
    assert results["vote"]["flagged_loci"] == 1


def test_flagged_locus_outside_the_exact_endpoint_stops():
    scorer = load_scorer()
    flagged = [{"modality": "wes", "subject": "S9", "gene": "A",
                "flagged_second_typing": "A*01:01+A*03:01"}]
    try:
        scorer.score([_locus("S1", "vote", "A*01:01", "A*02:01")], flagged)
    except SystemExit as stop:
        assert "outside the exact endpoint" in str(stop)
    else:
        raise AssertionError("expected a stop")


def test_committed_artifact_is_reproducible_and_exact_counts_match_the_primary():
    scorer = load_scorer()
    expected = scorer.score(scorer.read_rows(scorer.PER_LOCUS), scorer.read_rows(scorer.FLAGGED))
    with scorer.OUTPUT.open(newline="", encoding="utf-8") as handle:
        committed = list(csv.DictReader(handle, delimiter="\t"))
    assert committed == [{key: str(value) for key, value in row.items()} for row in expected]
    with (ROOT / "artifacts" / "development_corrected" / "method_performance.tsv").open(
            newline="", encoding="utf-8") as handle:
        primary = {(row["modality"], row["method"]): row
                   for row in csv.DictReader(handle, delimiter="\t")}
    for row in committed:
        assert row["exact_correct"] == primary[(row["modality"], row["method"])]["genotypes_correct"]
