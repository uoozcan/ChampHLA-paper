"""The active paper must report the superseding scientific correction."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "decisions" / "20260924_publication_remediation.json"
PERFORMANCE = ROOT / "artifacts" / "development_corrected" / "method_performance.tsv"
SINGLETON_DECISION = ROOT / "decisions" / "20261008_singleton_native_homozygosity.json"
SENSITIVITY = ROOT / "artifacts" / "development_sensitivity_abstain" / "method_performance.tsv"
MANUSCRIPT = ROOT / "manuscripts" / "benchmark" / "manuscript.md"
SUPPLEMENT = ROOT / "manuscripts" / "benchmark" / "supplementary.md"


def _rerun_inputs() -> bool:
    manifest = ROOT / "data" / "development" / "input_manifest.json"
    return json.loads(manifest.read_text(encoding="utf-8")).get(
        "schema_version") == "champhla-development-rerun-inputs-1"


def performance() -> dict[tuple[str, str], dict[str, str]]:
    with PERFORMANCE.open(newline="", encoding="utf-8") as handle:
        return {(row["modality"], row["method"]): row
                for row in csv.DictReader(handle, delimiter="\t")}


def test_superseding_decision_locks_development_scope():
    decision = json.loads(DECISION.read_text(encoding="utf-8"))
    assert decision["status"] == "AUTHORIZED"
    assert decision["publication_scope"]["study_type"].startswith("retrospective development")
    assert not decision["publication_scope"]["external_validation_complete"]
    assert not decision["publication_scope"]["wgs_accuracy_evidence_allowed"]


def test_singleton_rule_is_the_signed_native_declaration_policy():
    decision = json.loads(SINGLETON_DECISION.read_text(encoding="utf-8"))
    assert decision["status"] == "SIGNED" and decision["authorization"]["signed"]
    assert decision["rule"]["primary_singleton_policy"] == "native_declaration"
    primary = json.loads((ROOT / "data" / "development" / "input_manifest.json")
                         .read_text(encoding="utf-8"))
    sensitivity = json.loads((ROOT / "data" / "development" / "sensitivity_abstain" /
                              "input_manifest.json").read_text(encoding="utf-8"))
    assert primary["singleton_policy"] == "native_declaration"
    assert sensitivity["singleton_policy"] == "abstain"
    assert primary["source_sha256"] == sensitivity["source_sha256"]


def test_abstain_sensitivity_reproduces_the_scoring_before_the_decision():
    with SENSITIVITY.open(newline="", encoding="utf-8") as handle:
        rows = {(row["modality"], row["method"]): row
                for row in csv.DictReader(handle, delimiter="\t")}
    # Historical stored outputs gave 143 and 110; the v3.5.0 rerun inputs give 143 and 112.
    expected = (("wes", "143"), ("rnaseq", "112")) if _rerun_inputs() else (("wes", "143"), ("rnaseq", "110"))
    for modality, correct in expected:
        assert rows[(modality, "SimplePluralityLex")]["genotypes_correct"] == correct
    assert "**Singleton sensitivity.**" in SUPPLEMENT.read_text(encoding="utf-8")


def test_active_headlines_are_the_audited_results():
    rows = performance()
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    expected = {
        "wes": ("143", "153"),
        "rnaseq": ("113", "118"),
    }
    for modality, (correct, loci) in expected.items():
        row = rows[(modality, "SimplePluralityLex")]
        assert (row["genotypes_correct"], row["loci"]) == (correct, loci)
        assert f"{correct}/{loci}" in manuscript


def test_invalid_historical_headlines_are_absent_from_active_documents():
    active = MANUSCRIPT.read_text(encoding="utf-8") + SUPPLEMENT.read_text(encoding="utf-8")
    for value in ("365/390", "306/321", "364/390", "303/321"):
        assert value not in active


def test_truth_audit_exclusions_are_disclosed():
    manuscript = MANUSCRIPT.read_text(encoding="utf-8")
    for value in ("237/390", "200/318", "153 WES", "118 RNA-seq"):
        assert value in manuscript


def test_fitted_scores_never_reselect_the_primary():
    rows = performance()
    for method in ("MVFlooredCC", "MetaConsensus", "BestSingleTool_nestedCV"):
        assert rows[("rnaseq", method)]["analysis_scope"] == "exploratory_fitted"
    assert rows[("rnaseq", "MVFlooredCC")]["analysis_scope"] == "exploratory_fitted"
    assert rows[("rnaseq", "SimplePluralityLex")]["analysis_scope"] == "primary"
    assert "The refitted policies did not change the primary rule" in SUPPLEMENT.read_text(encoding="utf-8")


def test_adjusted_interval_and_holm_decision_are_coherent():
    """A Bonferroni cluster-t interval excluding zero must agree with Holm."""
    with (ROOT / "artifacts" / "development_corrected" /
          "secondary_method_results.tsv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        low = float(row["simultaneous_ci_lo_points"])
        high = float(row["simultaneous_ci_hi_points"])
        excludes_zero = low > 0 or high < 0
        if excludes_zero:
            assert float(row["holm_adjusted_p"]) < 0.05, row


def test_signflip_assignment_count_and_seed_are_auditable():
    with (ROOT / "artifacts" / "development_corrected" /
          "secondary_method_results.tsv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        discordant = int(row["discordant_subjects"])
        expected = 2 ** discordant if discordant <= 25 else 1_000_000
        assert int(row["signflip_assignments"]) == expected
        assert int(row["signflip_seed"]) >= 0
        expected_method = "exact_enumeration" if discordant <= 25 else "monte_carlo_plus_one"
        assert row["signflip_method"] == expected_method
