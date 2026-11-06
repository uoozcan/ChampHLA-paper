from __future__ import annotations

import csv
import importlib.util
import json
import re
from pathlib import Path

import pytest

from champhla_recovery.exploratory import (
    FIMM_AGGREGATES,
    VENEX_AGGREGATES,
    privacy_failures,
    sha256,
    validate_aggregate_estimates,
)


ROOT = Path(__file__).resolve().parents[1]
needs_held_back_aggregates = pytest.mark.skipif(
    not (ROOT / "artifacts" / "fimm_consensus").is_dir(),
    reason="controlled aggregates are held back from the public snapshot",
)


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


@needs_held_back_aggregates
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


@needs_held_back_aggregates
def test_checksum_manifests_cover_every_published_aggregate():
    for relative, expected_paths in (
        ("artifacts/fimm_consensus/aggregate_checksums.tsv", FIMM_AGGREGATES),
        ("artifacts/venex/aggregate_checksums.tsv", VENEX_AGGREGATES),
    ):
        rows = _rows(ROOT / relative)
        assert {row["artifact"] for row in rows} == set(expected_paths)
        for row in rows:
            assert row["sha256"] == sha256(ROOT / row["artifact"])


@needs_held_back_aggregates
def test_exported_aggregate_bundle_passes_privacy_scan():
    assert privacy_failures(ROOT) == []


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


def test_patient_cohorts_are_out_of_the_paper_and_the_registry():
    """decisions/20261105_patient_cohorts_removed.json keeps the S8 row and the ledger row;
    decisions/20261106_public_snapshot_scope.json adds the ledger row withholding their
    aggregate rows from the published provenance."""
    main = (ROOT / "manuscripts/benchmark/manuscript.md").read_text(encoding="utf-8")
    supplement = (ROOT / "manuscripts/benchmark/supplementary.md").read_text(encoding="utf-8")
    assert "FIMM" not in main and "VenEx" not in main and "BB7.2" not in main
    assert "RESULT:FIMM" not in supplement and "RESULT:VENEX" not in supplement
    disclosures = [line for line in supplement.splitlines()
                   if "FIMM" in line or "VenEx" in line]
    assert len(disclosures) == 3
    assert any("Analysed, not reported" in line for line in disclosures)
    assert any("Remove the FIMM and VenEx patient cohorts" in line for line in disclosures)
    assert any("Withhold the FIMM and VenEx aggregate rows" in line for line in disclosures)
    rows = _rows(ROOT / "result_registry.tsv")
    assert not [row for row in rows if row["result_id"].startswith(("FIMM_", "VENEX_"))]
