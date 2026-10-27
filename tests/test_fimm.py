from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from champhla_recovery.fimm import (
    caller_panels,
    classify_imbalance,
    collapse_donor_calls,
    cross_modality_concordance,
    flow_validation,
    normalize_allele,
    run_fimm_analysis,
    simple_plurality_lex,
)
from champhla_recovery.io import read_tsv

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/fimm"


def _call(caller: str, allele1: str, allele2: str) -> dict[str, str]:
    return {"caller": caller, "allele1": allele1, "allele2": allele2}


def test_plurality_complete_partial_missing_and_lexicographic_tie():
    complete = simple_plurality_lex(
        [_call("c1", "A*02:01", "A*03:01"), _call("c2", "A*03:01", "A*02:01")], "A"
    )
    assert complete["call_state"] == "complete"
    assert (complete["allele1"], complete["allele2"]) == ("A*02:01", "A*03:01")
    assert complete["support"] == 2

    tie = simple_plurality_lex(
        [_call("c1", "A*01:01", "A*02:01"), _call("c2", "A*02:01", "A*03:01")], "A"
    )
    assert tie["call_state"] == "tie"
    # Lexicographic tie-break, exactly as the frozen SimplePluralityLex rule specifies.
    assert (tie["allele1"], tie["allele2"]) == ("A*01:01", "A*02:01")
    assert tie["tie_count"] == 2

    assert simple_plurality_lex([_call("c1", "A*02:01", "")], "A")["call_state"] == "partial"
    assert simple_plurality_lex([_call("c1", "", "")], "A")["call_state"] == "missing"


def test_plurality_records_the_contributing_caller_panel():
    call = simple_plurality_lex(
        [_call("c2", "A*02:01", "A*03:01"), _call("c1", "A*02:01", "A*03:01")], "A"
    )
    assert call["panel"] == "c1,c2"
    assert call["panel_size"] == 2


def test_plurality_restricted_to_allowed_callers_excludes_the_others():
    rows = [_call("c1", "A*01:01", "A*02:01"), _call("c2", "A*02:01", "A*03:01")]
    restricted = simple_plurality_lex(rows, "A", allowed_callers={"c2"})
    assert (restricted["allele1"], restricted["allele2"]) == ("A*02:01", "A*03:01")
    assert restricted["call_state"] == "complete"
    assert restricted["panel"] == "c2"


def test_normalize_allele_truncates_to_two_fields_and_rejects_cross_locus():
    assert normalize_allele("HLA-A*02:01:01:02N", "A") == "A*02:01"
    assert normalize_allele("NA", "A") == ""
    with pytest.raises(ValueError):
        normalize_allele("B*07:02", "A")


def test_donor_collapse_requires_longitudinal_agreement():
    rows = [
        {"export_id": "FIMM-001", "modality": "wes", "locus": "A", "allele1": "A*01:01",
         "allele2": "A*02:01", "call_state": "complete", "panel": "c1"},
        {"export_id": "FIMM-001", "modality": "wes", "locus": "A", "allele1": "A*02:01",
         "allele2": "A*03:01", "call_state": "complete", "panel": "c1"},
    ]
    assert collapse_donor_calls(rows)[0]["call_state"] == "longitudinal_conflict"

    agreeing = [dict(rows[0]), dict(rows[0])]
    collapsed = collapse_donor_calls(agreeing)[0]
    assert collapsed["call_state"] == "complete"
    assert collapsed["samples"] == 2


@pytest.mark.parametrize(
    "fraction,sites,expected",
    [
        (0.80, 20, "threshold_positive_review"),
        (0.65, 20, "balanced"),
        (0.35, 20, "balanced"),
        (0.79, 20, "observed_imbalance_review"),
        (0.90, 19, "insufficient"),
        (None, 20, "insufficient"),
    ],
)
def test_imbalance_threshold_boundaries(fraction, sites, expected):
    assert classify_imbalance(fraction, sites) == expected


def test_caller_panels_are_derived_per_modality():
    panels = caller_panels(read_tsv(FIXTURE / "calls.tsv"))
    assert panels["scrna"] == {"c1", "c2"}
    assert panels["bulk_rna"] == {"c1", "c3"}
    assert panels["wes"] == {"c1", "c3"}


def test_concordance_reports_shared_callers_and_flags_thin_panels():
    calls = [
        {"export_id": "FIMM-001", "modality": "scrna", "locus": locus,
         "allele1": f"{locus}*01:01", "allele2": f"{locus}*02:01", "call_state": "complete"}
        for locus in ("A", "B", "C")
    ] + [
        {"export_id": "FIMM-001", "modality": "wes", "locus": locus,
         "allele1": f"{locus}*01:01", "allele2": f"{locus}*02:01", "call_state": "complete"}
        for locus in ("A", "B", "C")
    ]
    panels = {"scrna": {"c1", "c2"}, "wes": {"c1", "c3"}}
    rows = cross_modality_concordance(
        calls, pairs=[("scrna", "wes")], panels=panels
    )
    pooled = [row for row in rows if row["locus"] == "ALL"][0]
    assert pooled["shared_callers"] == "c1"
    assert pooled["shared_caller_count"] == 1
    # Two callers per panel is below the three-caller threshold at which a plurality
    # is more than a tie-break, so every such cell is flagged.
    assert pooled["thin_panel_flag"] == 1
    assert pooled["panel_policy"] == "full_panel"
    assert pooled["overlap"] == 3 and pooled["agreement"] == 3


def test_flow_validation_propagates_unlinked_records_onto_every_row():
    calls = [
        {"export_id": "FIMM-001", "modality": "wes", "locus": "A",
         "allele1": "A*02:01", "allele2": "A*03:01", "call_state": "complete"},
    ]
    rows = flow_validation(
        calls, [{"export_id": "FIMM-001", "flow_positive": "positive"}],
        unlinked_positive=31, unlinked_negative=27,
    )
    wes = [row for row in rows if row["modality"] == "wes" and row["mapping"] == "A*02"]
    assert wes, "expected WES rows"
    for row in wes:
        assert row["unlinked_flow_positive"] == 31
        assert row["unlinked_flow_negative"] == 27
        assert row["flow_records_total"] == row["informative"] + row["excluded"] + 58


def test_bb72_primary_and_cross_reactivity_mappings_are_distinct():
    calls = [
        {"export_id": "FIMM-001", "modality": "wes", "locus": "A",
         "allele1": "A*68:01", "allele2": "A*69:01", "call_state": "complete"},
    ]
    rows = flow_validation(calls, [{"export_id": "FIMM-001", "flow_positive": "positive"}])
    strict = {row["metric"]: row for row in rows
              if row["modality"] == "wes" and row["mapping"] == "A*02"}
    broad = {row["metric"]: row for row in rows
             if row["modality"] == "wes" and row["mapping"] == "A*02/A*68/A*69"}
    # A*68/A*69 are BB7.2 cross-reactive but are not A2: strict must call this a miss.
    assert strict["sensitivity"]["fn"] == 1
    assert broad["sensitivity"]["tp"] == 1


def test_end_to_end_fixture_emits_endpoints_without_identifiers_or_dates(tmp_path):
    status = run_fimm_analysis(FIXTURE / "manifest.json", tmp_path)
    assert status["status"] == "COMPLETE"
    assert status["numeric_outputs_emitted"] is True
    assert status["accuracy_endpoint_present"] is False
    assert status["donors"] == 4

    for name in (
        "cohort_flow.tsv", "caller_panels.tsv", "sample_plurality.tsv",
        "donor_plurality.tsv", "cross_modality_concordance.tsv", "bb72_metrics.tsv",
        "wes_allele_imbalance.tsv", "fimm_result_registry.tsv",
        "provenance.json", "privacy_audit.json", "artifact_checksums.tsv",
    ):
        assert (tmp_path / name).is_file(), name

    blob = "\n".join(
        path.read_text(encoding="utf-8")
        for path in tmp_path.rglob("*") if path.suffix in {".tsv", ".json"}
    )
    for forbidden in ("REAL-", "SEC-S", "2020-", "2021-", "/scratch/", str(FIXTURE)):
        assert forbidden not in blob, forbidden

    # No emitted result may describe itself as accuracy or external validation.
    registry = read_tsv(tmp_path / "fimm_result_registry.tsv")
    assert registry
    for row in registry:
        assert row["abstract_allowed"] == "0"
        assert row["evidence_role"] == "exploratory"
    assert all(row["result_kind"] != "performance" for row in registry)


def test_end_to_end_reports_both_panel_policies(tmp_path):
    run_fimm_analysis(FIXTURE / "manifest.json", tmp_path)
    rows = read_tsv(tmp_path / "cross_modality_concordance.tsv")
    policies = {row["panel_policy"] for row in rows}
    assert policies == {"full_panel", "disjoint_callers"}
    # c1 is shared by every pair in the fixture, so every pair gets a disjoint run.
    disjoint = {row["endpoint"] for row in rows if row["panel_policy"] == "disjoint_callers"}
    assert disjoint == {"scrna_vs_bulk_rna", "scrna_vs_wes", "bulk_rna_vs_wes"}
    expected_shared = {
        "scrna_vs_bulk_rna": "c1", "scrna_vs_wes": "c1", "bulk_rna_vs_wes": "c1,c3",
    }
    for row in rows:
        if row["panel_policy"] == "full_panel":
            assert row["shared_callers"] == expected_shared[row["endpoint"]]
        else:
            assert row["shared_callers"] == ""

    # bulk_rna and wes share their whole panel, so removing the shared callers leaves
    # nothing to compare. The pair must report zero overlap rather than silently
    # reusing the full-panel estimate.
    exhausted = [
        row for row in rows
        if row["panel_policy"] == "disjoint_callers"
        and row["endpoint"] == "bulk_rna_vs_wes" and row["locus"] == "ALL"
    ]
    assert exhausted and int(exhausted[0]["overlap"]) == 0
    assert exhausted[0]["estimate"] == ""


def test_unlinked_flow_records_reach_the_cohort_flow_and_claim_boundary(tmp_path):
    run_fimm_analysis(FIXTURE / "manifest.json", tmp_path)
    flow_stage = {
        row["stage"]: int(row["count"]) for row in read_tsv(tmp_path / "cohort_flow.tsv")
        if row["stage"].startswith("bb72")
    }
    assert flow_stage["bb72_linked"] == 4
    assert flow_stage["bb72_unlinked"] == 2
    boundaries = [
        row["claim_boundary"] for row in read_tsv(tmp_path / "fimm_result_registry.tsv")
        if row["result_id"].startswith("FIMM_FLOW_")
    ]
    assert boundaries and all("never linked" in text for text in boundaries)


def test_checksum_drift_blocks_numeric_outputs(tmp_path):
    staged = tmp_path / "inputs"
    shutil.copytree(FIXTURE, staged)
    calls = staged / "calls.tsv"
    calls.write_text(calls.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    output = tmp_path / "out"
    status = run_fimm_analysis(staged / "manifest.json", output)
    assert status["status"] == "BLOCKED_EVIDENCE"
    assert status["numeric_outputs_emitted"] is False
    assert any("checksum mismatch" in failure for failure in status["failures"])
    assert not (output / "cross_modality_concordance.tsv").exists()


def test_unfrozen_checksum_placeholder_blocks(tmp_path):
    staged = tmp_path / "inputs"
    shutil.copytree(FIXTURE, staged)
    manifest_path = staged / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["inputs"]["calls"]["sha256"] = "REPLACE_ON_ROIHU"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    status = run_fimm_analysis(manifest_path, tmp_path / "out")
    assert status["status"] == "BLOCKED_EVIDENCE"
    assert any("checksum is not frozen" in failure for failure in status["failures"])


def test_wrong_ipd_release_blocks(tmp_path):
    staged = tmp_path / "inputs"
    shutil.copytree(FIXTURE, staged)
    manifest_path = staged / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["ipd_imgt_hla_release"] = "3.59.0"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    status = run_fimm_analysis(manifest_path, tmp_path / "out")
    assert status["status"] == "BLOCKED_EVIDENCE"
    assert any("3.65.0" in failure for failure in status["failures"])


def test_export_id_namespace_is_enforced(tmp_path):
    staged = tmp_path / "inputs"
    shutil.copytree(FIXTURE, staged)
    crosswalk = staged / "crosswalk.tsv"
    crosswalk.write_text(
        crosswalk.read_text(encoding="utf-8").replace("FIMM-001", "OTHER-001"),
        encoding="utf-8",
    )
    manifest_path = staged / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    import hashlib
    manifest["inputs"]["crosswalk"]["sha256"] = hashlib.sha256(
        crosswalk.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    with pytest.raises(ValueError, match="FIMM- pseudonym namespace"):
        run_fimm_analysis(manifest_path, tmp_path / "out")


def test_submission_gate_config_is_blocked_and_excludes_survival():
    gate = json.loads(
        (ROOT / "configs/fimm_submission_gate.json").read_text(encoding="utf-8"))
    assert gate["submission_allowed"] is False
    assert gate["status"] == "BLOCKED_AUTHOR_AND_SECURE_PROVENANCE"
    assert "bb72_serogroup_agreement" in gate["scope"]
    assert any("Cox" in item for item in gate["out_of_scope"])
    assert gate["blocking_items"]
    assert gate["completed_technical_items"]


def test_manifest_template_ships_unfrozen_checksums():
    template = json.loads(
        (ROOT / "configs/fimm_analysis_manifest.template.json").read_text(encoding="utf-8"))
    assert template["ipd_imgt_hla_release"] == "3.65.0"
    assert template["accuracy_eligible"] is False
    assert template["external_validation_eligible"] is False
    for descriptor in template["inputs"].values():
        assert descriptor["sha256"] == "REPLACE_ON_ROIHU"
