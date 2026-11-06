"""Round 3 post hoc tables (decisions/20261106_posthoc_round3_amendment.json): rules on synthetic data."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


A1, A2, B1 = ("A*01:01", "A*01:01"), ("A*01:01", "A*02:01"), ("A*02:01", "A*03:01")


def test_error_counts_mark_undefined_phi_and_count_same_wrong_genotypes():
    module = load("score_error_dependence_counts_posthoc")
    loci = ["l1", "l2", "l3", "l4"]
    truth = {"l1": A1, "l2": A1, "l3": A2, "l4": A2}
    calls = {("x", "l1"): A2, ("y", "l1"): A2,      # both wrong, same genotype
             ("x", "l2"): None, ("y", "l2"): B1,    # both wrong, a no-call counts as wrong
             ("x", "l3"): A2, ("y", "l3"): A2,
             ("x", "l4"): A2, ("y", "l4"): B1}      # only y wrong
    counts = module.pair_counts(loci, calls, truth, "x", "y")
    assert (counts["caller1_errors"], counts["caller2_errors"], counts["both_wrong"]) == (2, 3, 2)
    assert counts["both_wrong_same_genotype"] == 1
    assert counts["expected_both_wrong_if_independent"] == "1.50"
    # y has no correct call outside l3, x errs twice: phi is defined here...
    assert counts["error_phi"] != ""
    # ...but not when one caller makes no error at all.
    perfect = {key: truth[key[1]] if key[0] == "x" else value for key, value in calls.items()}
    assert module.pair_counts(loci, perfect, truth, "x", "y")["error_phi"] == ""
    assert module.phi(3, 1, 0, 0) is None


def test_intersection_ignores_unparsed_rows_and_empty_intersections_are_not_scored():
    module = load("score_duplicate_rows_and_group_gap_posthoc")
    assert module.intersect_rows([{A1, A2}, {A2, B1}]) == {A2}
    assert module.intersect_rows([{A1, A2}, None]) == {A1, A2}
    assert module.intersect_rows([{A1}, {B1}]) == set()
    assert module.intersect_rows([None]) == set()
    pred = {("s1", "wes", "A"): {"allele1": "A*02:01", "allele2": "A*01:01",
                                 "call_status": "callable"}}
    loci = [("s1", "wes", "A"), ("s2", "wes", "A")]
    candidates = {("s1", "wes", "A"): {A2}, ("s2", "wes", "A"): set()}
    assert module.score(pred, loci, candidates) == (1, 1)


def test_naive_baselines_break_ties_alphabetically_and_pair_the_top_two_alleles():
    module = load("score_naive_baselines_posthoc")
    pool = [A2, B1, A2, B1, A1]
    assert module.predict(pool, "most_common_genotype") == A2   # A2 and B1 tie at 2
    # Allele copies: A*01:01 x4, A*02:01 x4, A*03:01 x2.
    assert module.predict(pool, "two_most_common_alleles") == ("A*01:01", "A*02:01")
    assert module.predict([A1], "two_most_common_alleles") == A1
    assert module.predict([], "most_common_genotype") is None


def test_pedigree_relations_and_family_clusters():
    module = load("score_relatedness_posthoc")
    blank = {"Siblings": "0", "Second Order": "0", "Third Order": "0"}
    rows = [
        {"Family ID": "F1", "Individual ID": "NA00001", "Paternal ID": "0", "Maternal ID": "0", **blank},
        {"Family ID": "F1", "Individual ID": "NA00002", "Paternal ID": "NA00001",
         "Maternal ID": "0", **blank},
        {"Family ID": "F1", "Individual ID": "NA00003", "Paternal ID": "NA00001",
         "Maternal ID": "0", **blank},
        {"Family ID": "F2", "Individual ID": "NA00004", "Paternal ID": "0", "Maternal ID": "0",
         "Siblings": "0", "Second Order": "NA00005", "Third Order": "0"},
        {"Family ID": "F3", "Individual ID": "NA00005", "Paternal ID": "0", "Maternal ID": "0", **blank},
    ]
    family, pairs = module.load_pedigree(rows)
    counts = module.related_pairs({"NA00001", "NA00002", "NA00003", "NA00004", "NA00005"}, pairs)
    assert counts == {"parent_offspring": 2, "siblings": 1, "second_order": 1, "third_order": 0}
    assert module.related_pairs({"NA00002", "NA00004"}, pairs) == dict.fromkeys(module.RELATIONS, 0)
    deltas = {("NA00002", "A"): 1, ("NA00003", "B"): -1, ("HG99999", "A"): 1}
    clusters = module.cluster_deltas(deltas, lambda s: family.get(s) or s)
    assert clusters == {"F1": 0, "HG99999": 1}


def test_allele_vote_calls_homozygotes_only_when_the_surplus_beats_the_next_allele():
    vote = load("score_allele_vote_and_abstention_posthoc").allele_vote
    assert vote([]) is None
    assert vote([A1, A1]) == A1
    # Copies: A*01:01 x3, A*02:01 x1 with n=2: surplus 1 >= 1, so homozygous.
    assert vote([A1, A2]) == A1
    # Copies: A*01:01 x3, A*02:01 x3 with n=3: tie on top goes to A*01:01, surplus 0 < 3.
    assert vote([A1, A2, ("A*02:01", "A*02:01")]) == A2
    # Copies: A*01:01 x2, A*02:01 x3, A*03:01 x1 with n=3.
    assert vote([A2, A2, B1]) == ("A*01:01", "A*02:01")
