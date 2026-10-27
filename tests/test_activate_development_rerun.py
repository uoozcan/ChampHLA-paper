"""Fail-closed tests for v3.5.0 development-rerun activation."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil

import pytest

from champhla_confirmation.development import CALLER_INPUT_FIELDS
from champhla_confirmation.io import read_tsv, sha256, write_json, write_tsv
from champhla_confirmation.panels import GENES, PANELS


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "activate_development_rerun", ROOT / "scripts/activate_development_rerun.py"
)
assert SPEC and SPEC.loader
ACTIVATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ACTIVATE)


def _caller_row(subject: str, modality: str, gene: str, caller: str) -> dict[str, str]:
    row = {field: "" for field in CALLER_INPUT_FIELDS}
    row.update({
        "cohort": "1000G-development-rerun-v3.5.0",
        "subject": subject,
        "modality": modality,
        "gene": gene,
        "caller": caller,
        "allele1": f"{gene}*01:01",
        "allele2": f"{gene}*02:01",
        "call_status": "callable",
        "homozygosity_basis": "two_alleles",
    })
    return row


def _write_destination(path: Path) -> None:
    path.mkdir(parents=True)
    historical = _caller_row("OLD", "wes", "A", "OptiType")
    write_tsv(path / "normalized_caller_calls.tsv", [historical], CALLER_INPUT_FIELDS)
    write_tsv(path / "excluded_caller_calls.tsv", [historical], CALLER_INPUT_FIELDS)
    secondary = [{
        "cohort": "old", "subject": "OLD", "modality": "wes", "gene": "A",
        "method": "BestSingleTool_nestedCV", "outer_fold": "1",
    }]
    write_tsv(path / "normalized_secondary_calls.tsv", secondary)
    write_json(path / "input_manifest.json", {"schema_version": "old"})
    write_json(path / "frozen_raw_cc_policy.json", {"frozen": True})
    sensitivity = path / "sensitivity_abstain"
    sensitivity.mkdir()
    write_tsv(sensitivity / "normalized_caller_calls.tsv", [historical], CALLER_INPUT_FIELDS)
    write_tsv(sensitivity / "excluded_caller_calls.tsv", [historical], CALLER_INPUT_FIELDS)
    shutil.copy2(path / "normalized_secondary_calls.tsv",
                 sensitivity / "normalized_secondary_calls.tsv")
    write_json(sensitivity / "input_manifest.json", {"schema_version": "old"})


def _write_collection(path: Path) -> None:
    path.mkdir(parents=True)
    roster_source = ROOT / "cohorts/development_rerun_manifest.tsv"
    roster_path = path / "selected_input_manifest.tsv"
    shutil.copy2(roster_source, roster_path)
    roster = read_tsv(roster_path)
    write_json(path / "rerun_gate.json", {
        "schema_version": "champhla-development-rerun-gate-1",
        "status": "PASS",
        "validator_counts": {
            "checked": 236, "complete_valid": 236, "incomplete_or_invalid": 0,
        },
        "running_jobs": {
            "champhla_ctl": 0, "champhla_dev": 0, "champhla_prefetch": 0,
        },
        "controller_finished_normally": True,
        "execution_manager_sha256": sha256(ROOT / "provenance/development_rerun_v350/operational_gate/manage_development_batches.deployed.py"),
        "roster_sha256": sha256(roster_source),
    })
    calls = [
        _caller_row(row["sample_id"], row["modality"], gene, caller)
        for row in roster
        for caller in PANELS[row["modality"]]
        for gene in GENES
    ]
    calls[0]["allele2"] = calls[0]["allele1"]
    calls[0]["homozygosity_basis"] = "caller_native_declaration"
    write_tsv(path / "normalized_caller_calls.tsv", calls, CALLER_INPUT_FIELDS)
    sensitivity = [dict(row) for row in calls]
    sensitivity[0].update({
        "allele1": "", "allele2": "", "call_status": "partial",
        "no_call_reason": "sensitivity_abstain_native_homozygous_declaration",
    })
    sensitivity_dir = path / "sensitivity_abstain"
    sensitivity_dir.mkdir()
    write_tsv(sensitivity_dir / "normalized_caller_calls.tsv", sensitivity, CALLER_INPUT_FIELDS)
    (path / "t1k_parser_provenance.tsv").write_text(
        "subject\tmodality\tgene\n", encoding="utf-8"
    )
    runs = [{
        "subject": row["sample_id"], "modality": row["modality"],
        "release_commit": ACTIVATE.DEFAULT_RELEASE_COMMIT, "sample_complete": "1",
    } for row in roster]
    write_tsv(path / "sample_run_provenance.tsv", runs)
    tasks = [{
        "subject": row["sample_id"], "modality": row["modality"],
        "caller": caller, "disposition": "outputs_present",
    } for row in roster for caller in PANELS[row["modality"]]]
    write_tsv(path / "caller_run_state.tsv", tasks)
    comparison = [{
        "subject": row["subject"], "modality": row["modality"],
        "gene": row["gene"], "caller": row["caller"],
        "difference_class": "identical", "same_state_and_pair": "1",
    } for row in calls]
    write_tsv(path / "stored_vs_rerun_cells.tsv", comparison)
    source = {"collected_calls": sha256(path / "normalized_caller_calls.tsv")}
    write_json(path / "input_manifest.json", {
        "schema_version": ACTIVATE.INPUT_SCHEMA, "truth_free": True,
        "singleton_policy": "native_declaration", "source_sha256": source,
        "output_sha256": {
            "normalized_caller_calls": sha256(path / "normalized_caller_calls.tsv")
        },
    })
    write_json(sensitivity_dir / "input_manifest.json", {
        "schema_version": ACTIVATE.INPUT_SCHEMA, "truth_free": True,
        "singleton_policy": "abstain", "source_sha256": source,
        "output_sha256": {
            "normalized_caller_calls": sha256(
                sensitivity_dir / "normalized_caller_calls.tsv"
            )
        },
    })
    output_paths = {
        relative: path / relative for relative in ACTIVATE.REQUIRED_COLLECTION_FILES
    }
    write_json(path / "collection_manifest.json", {
        "schema_version": ACTIVATE.COLLECTION_SCHEMA,
        "truth_free": True,
        "release_commit": ACTIVATE.DEFAULT_RELEASE_COMMIT,
        "source_manifest_sha256": sha256(roster_source),
        "selected_input_manifest_sha256": sha256(roster_path),
        "sample_assays": 236,
        "caller_rows": ACTIVATE.EXPECTED_CALLER_CELLS,
        "caller_run_state_rows": ACTIVATE.EXPECTED_CALLER_TASKS,
        "output_sha256": {
            relative: sha256(output) for relative, output in output_paths.items()
        },
    })


@pytest.fixture
def valid_collection(tmp_path: Path) -> Path:
    collection = tmp_path / "collection"
    _write_collection(collection)
    return collection


def _manifest(path: Path) -> dict:
    return json.loads((path / "collection_manifest.json").read_text(encoding="utf-8"))


def _rewrite_manifest(path: Path, payload: dict) -> None:
    write_json(path / "collection_manifest.json", payload)


def test_complete_collection_activates_and_preserves_secondary_rows(
    valid_collection: Path, tmp_path: Path
):
    destination, provenance = tmp_path / "development", tmp_path / "provenance"
    _write_destination(destination)
    secondary_before = sha256(destination / "normalized_secondary_calls.tsv")
    report = ACTIVATE.activate(valid_collection, destination, provenance)
    assert report["sample_assays"] == 236
    assert report["caller_cells"] == 3222
    assert report["caller_tasks"] == 1074
    assert sha256(destination / "normalized_secondary_calls.tsv") == secondary_before
    assert len(read_tsv(destination / "normalized_caller_calls.tsv")) == 3222
    assert read_tsv(destination / "excluded_caller_calls.tsv") == []
    assert (provenance / "truth_free_collection/collection_manifest.json").is_file()
    assert (provenance / "historical_inputs_pre_v350/normalized_caller_calls.tsv").is_file()
    assert (provenance / "historical_result_registry_pre_v350.tsv").is_file()


def test_active_tables_carry_the_analysis_cohort_and_the_archive_keeps_provenance(
    valid_collection: Path, tmp_path: Path
):
    destination, provenance = tmp_path / "development", tmp_path / "provenance"
    _write_destination(destination)
    ACTIVATE.activate(valid_collection, destination, provenance)
    for relative in ("normalized_caller_calls.tsv",
                     "sensitivity_abstain/normalized_caller_calls.tsv"):
        active = read_tsv(destination / relative)
        archived = read_tsv(provenance / "truth_free_collection" / relative)
        # the truth builder labels its rows "1000G-development"; a provenance label on
        # the predictions would leave every locus unjoined
        assert {row["cohort"] for row in active} == {ACTIVATE.ANALYSIS_COHORT}
        assert {row["cohort"] for row in archived} == {ACTIVATE.COLLECTION_COHORT}
        strip = [{k: v for k, v in row.items() if k != "cohort"} for row in archived]
        assert [{k: v for k, v in row.items() if k != "cohort"} for row in active] == strip
    manifest = json.loads((destination / "input_manifest.json").read_text(encoding="utf-8"))
    assert manifest["cohort_labels"] == {"collection": ACTIVATE.COLLECTION_COHORT,
                                         "analysis": ACTIVATE.ANALYSIS_COHORT}


def test_partial_roster_is_refused(valid_collection: Path):
    payload = _manifest(valid_collection)
    payload["sample_assays"] = 235
    _rewrite_manifest(valid_collection, payload)
    with pytest.raises(ValueError, match="exactly 236"):
        ACTIVATE.validate_collection(valid_collection)


def test_wrong_release_is_refused(valid_collection: Path):
    payload = _manifest(valid_collection)
    payload["release_commit"] = "0" * 40
    _rewrite_manifest(valid_collection, payload)
    with pytest.raises(ValueError, match="wrong release commit"):
        ACTIVATE.validate_collection(valid_collection)


def test_checksum_mismatch_is_refused(valid_collection: Path):
    with (valid_collection / "caller_run_state.tsv").open("a", encoding="utf-8") as handle:
        handle.write("tampered\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        ACTIVATE.validate_collection(valid_collection)


def test_duplicate_or_missing_caller_cell_is_refused(valid_collection: Path):
    calls = read_tsv(valid_collection / "normalized_caller_calls.tsv")
    write_tsv(valid_collection / "normalized_caller_calls.tsv", calls[:-1], CALLER_INPUT_FIELDS)
    payload = _manifest(valid_collection)
    payload["output_sha256"]["normalized_caller_calls.tsv"] = sha256(
        valid_collection / "normalized_caller_calls.tsv"
    )
    _rewrite_manifest(valid_collection, payload)
    primary = json.loads((valid_collection / "input_manifest.json").read_text(encoding="utf-8"))
    primary["output_sha256"]["normalized_caller_calls"] = sha256(
        valid_collection / "normalized_caller_calls.tsv"
    )
    primary["source_sha256"]["collected_calls"] = sha256(
        valid_collection / "normalized_caller_calls.tsv"
    )
    write_json(valid_collection / "input_manifest.json", primary)
    sensitivity = json.loads(
        (valid_collection / "sensitivity_abstain/input_manifest.json").read_text(encoding="utf-8")
    )
    sensitivity["source_sha256"] = primary["source_sha256"]
    write_json(valid_collection / "sensitivity_abstain/input_manifest.json", sensitivity)
    with pytest.raises(ValueError, match="caller grid mismatch"):
        ACTIVATE.validate_collection(valid_collection)


def test_truth_bearing_column_is_refused(valid_collection: Path):
    path = valid_collection / "t1k_parser_provenance.tsv"
    path.write_text("subject\ttruth\n", encoding="utf-8")
    payload = _manifest(valid_collection)
    payload["output_sha256"]["t1k_parser_provenance.tsv"] = sha256(path)
    _rewrite_manifest(valid_collection, payload)
    with pytest.raises(ValueError, match="truth-bearing"):
        ACTIVATE.validate_collection(valid_collection)


def test_mismatched_singleton_policy_is_refused(valid_collection: Path):
    path = valid_collection / "sensitivity_abstain/input_manifest.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["singleton_policy"] = "native_declaration"
    write_json(path, payload)
    with pytest.raises(ValueError, match="wrong singleton policy"):
        ACTIVATE.validate_collection(valid_collection)
