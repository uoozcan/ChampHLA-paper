from __future__ import annotations

import csv
import importlib.util
import json
import re
from pathlib import Path

from champhla_recovery.exploratory import (
    FIMM_AGGREGATES,
    VENEX_AGGREGATES,
    privacy_failures,
    sha256,
    validate_aggregate_estimates,
)


ROOT = Path(__file__).resolve().parents[1]


def _cross_module():
    script = ROOT / "scripts/compare_cross_modality.py"
    spec = importlib.util.spec_from_file_location("compare_cross_modality", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_dataset_roles_are_exploratory_and_never_abstract_or_accuracy_eligible():
    roles = json.loads((ROOT / "configs/dataset_roles.json").read_text(encoding="utf-8"))
    assert set(roles["datasets"]) == {"FIMM_AML_MDS", "VENEX_WES"}
    for item in roles["datasets"].values():
        assert item["role"] == "exploratory"
        assert item["accuracy_eligible"] is False
        assert item["abstract_eligible"] is False
        assert item["external_validation_eligible"] is False


def test_fimm_panel_deviation_is_approved_only_within_requested_boundary():
    decision = json.loads(
        (ROOT / "decisions/20260929_fimm_panel_deviation.json").read_text(encoding="utf-8"))
    assert decision["status"] == "APPROVED_EXPLORATORY"
    scope = decision["approval_scope"]
    assert scope["cohort"] == "FIMM_AML_MDS"
    assert set(scope["panel"]) == {"ArcasHLA", "OptiType", "SpecHLA"}
    assert "two coequal definitions" in scope["eligibility_rules"]["cross_modality"]
    assert "at least two valid caller genotypes" in scope["eligibility_rules"]["caller_dissent"]
    assert scope["accuracy_claims_permitted"] is False
    assert scope["abstract_claims_permitted"] is False


def test_every_frozen_aggregate_estimate_and_interval_recounts():
    assert validate_aggregate_estimates(ROOT) == []


def test_contested_eligibility_requires_two_callers_in_both_assays():
    module = _cross_module()
    panels = {"left": {"c1", "c2"}, "right": {"c1", "c2"}}
    pair = ("A*01:01", "A*02:01")
    left = {
        ("left", "S1", "A"): {
            "call_status": "callable", "callable_tools": "2",
            "allele1": pair[0], "allele2": pair[1],
        },
        ("left", "S2", "A"): {
            "call_status": "callable", "callable_tools": "1",
            "allele1": pair[0], "allele2": pair[1],
        },
    }
    right = {
        ("right", "S1", "A"): {
            "call_status": "callable", "callable_tools": "2",
            "allele1": pair[0], "allele2": pair[1],
        },
        ("right", "S2", "A"): {
            "call_status": "callable", "callable_tools": "2",
            "allele1": pair[0], "allele2": pair[1],
        },
    }
    all_row = module._compare(
        left, right, "left", "right", panels, "specimen", "all_callable")[3]
    contested = module._compare(
        left, right, "left", "right", panels, "specimen", "contested_both")[3]
    assert (all_row["agreement"], all_row["overlap"]) == (2, 2)
    assert (contested["agreement"], contested["overlap"]) == (1, 1)


def test_checksum_manifests_cover_every_published_aggregate():
    for relative, expected_paths in (
        ("artifacts/fimm_consensus/aggregate_checksums.tsv", FIMM_AGGREGATES),
        ("artifacts/venex/aggregate_checksums.tsv", VENEX_AGGREGATES),
    ):
        rows = _rows(ROOT / relative)
        assert {row["artifact"] for row in rows} == set(expected_paths)
        for row in rows:
            assert row["sha256"] == sha256(ROOT / row["artifact"])


def test_exported_aggregate_bundle_passes_privacy_scan():
    assert privacy_failures(ROOT) == []


def test_registry_boundaries_and_non_estimable_rows_are_explicit():
    rows = _rows(ROOT / "result_registry.tsv")
    active = [row for row in rows if row["cohort"] in {"FIMM_AML_MDS", "VENEX_WES"}]
    assert active
    assert all(row["abstract_allowed"] == "0" for row in active)
    assert all(row["result_kind"] in {
        "performance", "concordance", "categorical-summary", "survival-effect"
    } for row in active)
    disjoint = [row for row in active if row["result_id"].startswith("FIMM_PANEL_DISJOINT_")]
    assert len(disjoint) == 3
    assert all(row["loci"] == "0" and row["estimate"] == "" for row in disjoint)
    assert all("zero overlap" in row["claim_boundary"] for row in disjoint)
    assert not any("tierA" in row["artifact_path"] or "tierB" in row["artifact_path"]
                   for row in active)
    assert not any("imbalance" in row["endpoint"].lower() for row in active)


def test_fimm_specimen_definitions_are_coequal_and_donor_rows_are_sensitivity_only():
    rows = {row["result_id"]: row for row in _rows(ROOT / "result_registry.tsv")}
    for pair in ("BULKRNA_WES", "SCRNA_WES", "BULKRNA_SCRNA"):
        all_callable = rows[f"FIMM_PANEL_SPECIMEN_{pair}_EXACT_PAIR"]
        contested = rows[f"FIMM_PANEL_SPECIMEN_CONTESTED_{pair}_EXACT_PAIR"]
        donor = rows[f"FIMM_PANEL_DONOR_{pair}_EXACT_PAIR_SENSITIVITY"]
        assert all_callable["analysis_status"] == "exploratory_coequal"
        assert contested["analysis_status"] == "exploratory_coequal"
        assert all_callable["endpoint"].startswith("all_callable_")
        assert contested["endpoint"].startswith("contested_both_")
        assert donor["analysis_status"] == "exploratory_sensitivity"
        assert "donor collapse is sensitivity-only" in donor["claim_boundary"]


def test_contested_specimen_counts_match_the_secure_recounted_aggregate():
    rows = {row["result_id"]: row for row in _rows(ROOT / "result_registry.tsv")}
    expected = {
        "BULKRNA_WES": (62, 70),
        "SCRNA_WES": (21, 24),
        "BULKRNA_SCRNA": (18, 21),
    }
    for pair, (agreement, overlap) in expected.items():
        row = rows[f"FIMM_PANEL_SPECIMEN_CONTESTED_{pair}_EXACT_PAIR"]
        assert (int(row["correct"]), int(row["loci"])) == (agreement, overlap)


def test_contested_donor_sensitivity_is_conservative_and_explicitly_estimable_or_not():
    rows = {row["result_id"]: row for row in _rows(ROOT / "result_registry.tsv")}
    bulk_wes = rows[
        "FIMM_PANEL_DONOR_CONTESTED_BULKRNA_WES_EXACT_PAIR_SENSITIVITY"]
    assert (bulk_wes["correct"], bulk_wes["loci"], bulk_wes["estimate"]) == (
        "2", "2", "1.0")
    for pair in ("SCRNA_WES", "BULKRNA_SCRNA"):
        row = rows[f"FIMM_PANEL_DONOR_CONTESTED_{pair}_EXACT_PAIR_SENSITIVITY"]
        assert row["loci"] == "0" and row["estimate"] == ""
        assert row["analysis_status"].endswith("non_estimable")


def test_submission_gate_contains_only_author_and_secure_source_blockers():
    gate = json.loads((ROOT / "configs/fimm_submission_gate.json").read_text())
    assert gate["status"] == "BLOCKED_AUTHOR_AND_SECURE_PROVENANCE"
    assert len(gate["blocking_items"]) == 6
    assert all("denominator" not in item.lower() for item in gate["blocking_items"])
    assert any("source manifest" in item for item in gate["blocking_items"])
    assert gate["completed_technical_items"]


def test_withdrawn_legacy_numbers_do_not_reenter_active_text_or_figures():
    main = (ROOT / "manuscripts/benchmark/manuscript.md").read_text(encoding="utf-8")
    supplement = (ROOT / "manuscripts/benchmark/supplementary.md").read_text(encoding="utf-8")
    manifest = (ROOT / "figures/figure_manifest.json").read_text(encoding="utf-8")
    active = main + supplement + manifest
    for withdrawn in (r"(?<!\d)35/35(?!\d)", r"(?<!\d)0/33(?!\d)", r"\b0 of 33\b"):
        assert not re.search(withdrawn, active)
    abstract = main.split("## Abstract", 1)[1].split("## Keywords", 1)[0]
    assert "FIMM" not in abstract and "VenEx" not in abstract
    assert "wes_allele_imbalance" not in active


def test_retained_aggregate_only_patient_claims_use_stable_registry_tags():
    main = (ROOT / "manuscripts/benchmark/manuscript.md").read_text(encoding="utf-8")
    supplement = (ROOT / "manuscripts/benchmark/supplementary.md").read_text(encoding="utf-8")
    assert "62/70" in main
    assert "[RESULT:FIMM_PANEL_SPECIMEN_CONTESTED_BULKRNA_WES_EXACT_PAIR]" in main
    retained = (
        "FIMM_PANEL_SPECIMEN_CONTESTED_BULKRNA_WES_EXACT_PAIR",
        "FIMM_PANEL_DISJOINT_BULKRNA_WES_NON_ESTIMABLE",
        "VENEX_WES_HLA_HD_CONTESTED_DISSENT",
        "VENEX_WES_OPTITYPE_CONTESTED_DISSENT",
        "VENEX_WES_SPECHLA_CONTESTED_DISSENT",
        "VENEX_WES_T1K_CONTESTED_DISSENT",
        "VENEX_WES_POLYSOLVER_CONTESTED_DISSENT",
        "VENEX_WES_POLYSOLVER_MISSING",
        "VENEX_WES_POLYSOLVER_EMPTY",
    )
    for result_id in retained:
        assert f"[RESULT:{result_id}]" in supplement
    # decisions/20261026_fimm_venex_s9_restored.json restores the registered S9 detail:
    # coequal specimen pairs, donor sensitivity and BB7.2 (always with its linkage).
    for restored in (
        "FIMM_PANEL_SPECIMEN_BULKRNA_WES_EXACT_PAIR",
        "FIMM_PANEL_SPECIMEN_SCRNA_WES_EXACT_PAIR",
        "FIMM_PANEL_SPECIMEN_BULKRNA_SCRNA_EXACT_PAIR",
        "FIMM_PANEL_WES_ARCASHLA_CONTESTED_DISSENT",
    ):
        assert f"[RESULT:{restored}]" in supplement
    assert "FIMM_BB72_WES_A02_" in supplement
    assert "Only 16 of 53 flow records linked" in " ".join(supplement.split())
    # Withdrawn analyses never return.
    assert "fingerprint" in supplement and "is withdrawn" in supplement
    assert "no LOH claim is made" in " ".join(supplement.split())
