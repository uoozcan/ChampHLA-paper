"""Leave-one-caller-out, P-group and flagged-locus tables: rules and committed artifacts."""
from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CHARACTERISED = ROOT / "artifacts" / "development_characterisation"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_vote_uses_the_lexicographic_tie_break_and_a_strict_majority():
    vote = load("score_leave_one_caller_out_posthoc").vote
    first, second = ("A*01:01", "A*02:01"), ("A*01:01", "A*03:01")
    assert vote({"a": second, "b": first}) == (first, False)
    assert vote({"a": first, "b": first, "c": second}) == (first, True)
    assert vote({}) == (None, False)


def test_full_panel_row_reproduces_the_registered_votes():
    results = {(r["modality"], r["left_out"]): r
               for r in rows(CHARACTERISED / "leave_one_caller_out_posthoc.tsv")}
    performance = {(r["modality"], r["method"]): r for r in rows(
        ROOT / "artifacts" / "development_corrected" / "method_performance.tsv")}
    for modality in ("wes", "rnaseq"):
        full = results[(modality, "none")]
        plurality = performance[(modality, "SimplePluralityLex")]
        strict = performance[(modality, "SimpleStrictMajority")]
        assert full["plurality_correct"] == plurality["genotypes_correct"]
        assert full["strict_majority_correct"] == strict["genotypes_correct"]
        assert full["strict_majority_callable"] == strict["callable"]


def test_p_group_agreement_never_falls_below_exact_and_matches_the_adjudication():
    results = rows(CHARACTERISED / "exact_locus_p_group_agreement_posthoc.tsv")
    for row in results:
        assert int(row["p_group_agreement"]) >= int(row["exact_correct"])
    adjudication = rows(CHARACTERISED / "reference_adjudication.tsv")
    for row in results:
        if row["method"] != "SimplePluralityLex":
            continue
        gained = sum(item["modality"] == row["modality"]
                     and item["p_group_equivalent_to_reference"] == "1" for item in adjudication)
        assert int(row["p_group_agreement"]) == int(row["exact_correct"]) + gained


def test_evidence_table_must_cover_exactly_the_wes_vote_error_loci():
    build = load("build_flagged_loci_evidence").build
    source = {"subject": "S1", "gene": "A", "erlich_2011": "vote",
              "trusight_buchkovich_2017": "no row", "assembly": "none",
              "abi_rached_confirmation": "undetermined"}
    adjudication = {"modality": "wes", "subject": "S1", "gene": "A", "superpopulation": "CEU",
                    "reference": "A*01:01+A*02:01", "consensus": "A*01:01+A*03:01",
                    "p_group_equivalent_to_reference": "0"}
    assert build([source], [adjudication])[0]["vote_error_assays"] == "WES"
    with pytest.raises(SystemExit):
        build([], [adjudication])


def test_committed_evidence_artifact_is_reproducible():
    module = load("build_flagged_loci_evidence")
    expected = module.build(module.read_rows(module.CURATED), module.read_rows(module.ADJUDICATION))
    assert rows(module.OUTPUT) == expected
    assert len(expected) == 10
    assert sum(row["erlich_2011"] == "vote" for row in expected) == 9
    assert sum(row["trusight_buchkovich_2017"] == "vote" for row in expected) == 5
