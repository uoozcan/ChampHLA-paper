"""Round 4 run-stability rows (decisions/20261106_posthoc_round4_amendment.json, C1) on synthetic data."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _row(subject, caller, a1, a2, status="callable"):
    return {"cohort": "c", "subject": subject, "superpopulation": "", "modality": "rnaseq",
            "gene": "A", "caller": caller, "allele1": a1, "allele2": a2, "call_status": status}


def test_run_calls_votes_over_the_panel_and_treats_non_calls_as_none():
    module = load("score_run_stability_posthoc")
    rows = [_row("s1", "HLA-HD", "A*01:01", "A*02:01"),
            _row("s1", "OptiType", "A*01:01", "A*02:01"),
            _row("s1", "T1K", "A*03:01", "A*02:01"),
            _row("s1", "ArcasHLA", "A*01:01", "", status="partial"),
            _row("s1", "SpecHLA", "A*03:01", "A*03:01")]  # not on the RNA-seq panel
    loci = {("s1", "rnaseq", "A"), ("s2", "rnaseq", "A")}
    calls = module.run_calls(rows, loci)
    assert calls[(module.VOTE, ("s1", "rnaseq", "A"))] == ("A*01:01", "A*02:01")
    assert calls[("ArcasHLA", ("s1", "rnaseq", "A"))] is None
    assert ("SpecHLA", ("s1", "rnaseq", "A")) not in calls
    assert (module.VOTE, ("s2", "rnaseq", "A")) not in calls  # no rows: scored as wrong


def test_score_reports_largest_change_leaders_and_changed_vote_calls():
    module = load("score_run_stability_posthoc")
    right, wrong = ("A*01:01", "A*02:01"), ("A*01:01", "A*03:01")
    loci = [("s1", "rnaseq", "A"), ("s2", "rnaseq", "A"), ("s3", "rnaseq", "A")]
    truth = {key: right for key in loci}
    archived = {(module.VOTE, key): right for key in loci}
    archived.update({("ArcasHLA", key): right for key in loci})
    archived.update({("HLA-HD", loci[0]): right})
    study = {(module.VOTE, loci[0]): right, (module.VOTE, loci[1]): right,
             (module.VOTE, loci[2]): wrong}
    study.update({("HLA-HD", key): right for key in loci})
    rows, summary = module.score(truth, archived, study)
    by_method = {row["method"]: row for row in rows}
    assert (by_method["ArcasHLA"]["archived_correct"], by_method["ArcasHLA"]["change"]) == (3, -3)
    assert by_method[module.VOTE]["change"] == -1
    (only,) = summary
    assert (only["largest_change_caller"], only["largest_caller_change"]) == ("ArcasHLA", 3)
    assert only["leading_caller_archived"] == "ArcasHLA"
    assert only["leading_caller_study_run"] == "HLA-HD"
    assert only["vote_calls_changed"] == 1
