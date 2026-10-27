#!/usr/bin/env python3
"""Validate and atomically activate a complete truth-free v3.5.0 rerun collection.

This command is intentionally stricter than the collector.  It accepts only the
signed 236-run roster and release commit, rejects truth-bearing tabular inputs,
archives the complete collection and the pre-activation caller inputs, and then
replaces only the primary and abstain-sensitivity caller tables.  Historical
secondary rows and the frozen policy remain in place solely to provide fixed
outer-fold assignments and the predeclared fitted-policy specification.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from champhla_confirmation.development import CALLER_INPUT_FIELDS  # noqa: E402
from champhla_confirmation.io import (  # noqa: E402
    TRUTH_TOKENS,
    read_tsv,
    sha256,
    write_json,
    write_tsv,
)
from champhla_confirmation.panels import GENES, PANELS  # noqa: E402
from manage_development_batches import DEFAULT_RELEASE_COMMIT  # noqa: E402

DEPLOYED_MANAGER = Path(
    "provenance/development_rerun_v350/operational_gate/manage_development_batches.deployed.py"
)


COLLECTION_SCHEMA = "champhla-development-rerun-collection-2"
INPUT_SCHEMA = "champhla-development-rerun-inputs-1"
# The collector labels its rows with the rerun's provenance; the analysis (truth
# builder, registry, claim audit) keys the development cohort by its canonical label.
# The archived collection keeps the provenance label, and the input manifest records
# both, so the active tables carry the canonical one (decisions/20261025_rerun_cohort_label.json).
COLLECTION_COHORT = "1000G-development-rerun-v3.5.0"
ANALYSIS_COHORT = "1000G-development"
EXPECTED_ASSAYS = {"wes": 130, "rnaseq": 106}
EXPECTED_CALLER_CELLS = sum(
    EXPECTED_ASSAYS[assay] * len(PANELS[assay]) * len(GENES)
    for assay in EXPECTED_ASSAYS
)
EXPECTED_CALLER_TASKS = sum(
    EXPECTED_ASSAYS[assay] * len(PANELS[assay]) for assay in EXPECTED_ASSAYS
)
REQUIRED_COLLECTION_FILES = (
    "normalized_caller_calls.tsv",
    "t1k_parser_provenance.tsv",
    "sample_run_provenance.tsv",
    "caller_run_state.tsv",
    "stored_vs_rerun_cells.tsv",
    "selected_input_manifest.tsv",
    "sensitivity_abstain/normalized_caller_calls.tsv",
)


def _load_json(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"missing required JSON file: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return payload


def _safe_member(root: Path, relative: str) -> Path:
    member = (root / relative).resolve()
    try:
        member.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"collection manifest contains an unsafe path: {relative}") from exc
    return member


def _reject_truth_headers(collection: Path) -> None:
    forbidden = {token.lower() for token in TRUTH_TOKENS}
    for path in sorted(collection.rglob("*.tsv")):
        with path.open(newline="", encoding="utf-8", errors="replace") as handle:
            header = next(csv.reader(handle, delimiter="\t"), [])
        found = sorted({column.strip().lower() for column in header} & forbidden)
        if found:
            raise ValueError(
                f"{path.relative_to(collection)} contains forbidden truth-bearing "
                f"columns: {found}"
            )


def _validate_selected_roster(collection: Path, manifest: dict) -> list[dict[str, str]]:
    canonical_path = ROOT / "cohorts" / "development_rerun_manifest.tsv"
    selected_path = collection / "selected_input_manifest.tsv"
    canonical = read_tsv(canonical_path)
    selected = read_tsv(selected_path)
    if selected != canonical:
        raise ValueError("selected_input_manifest.tsv does not exactly match the canonical roster")
    if manifest.get("source_manifest_sha256") != sha256(canonical_path):
        raise ValueError("collection source-manifest checksum does not match the canonical roster")
    if manifest.get("selected_input_manifest_sha256") != sha256(selected_path):
        raise ValueError("selected-input-manifest checksum mismatch")
    if manifest.get("sample_assays") != sum(EXPECTED_ASSAYS.values()):
        raise ValueError("collection does not account for exactly 236 sample-assay runs")
    keys = [(row.get("sample_id", ""), row.get("modality", "")) for row in selected]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate sample-assay row in selected roster")
    observed = {
        assay: sum(row.get("modality") == assay for row in selected)
        for assay in EXPECTED_ASSAYS
    }
    if observed != EXPECTED_ASSAYS:
        raise ValueError(f"selected roster assay counts differ: {observed}")
    return selected


def _validate_output_hashes(collection: Path, manifest: dict) -> None:
    hashes = manifest.get("output_sha256")
    if not isinstance(hashes, dict):
        raise ValueError("collection manifest lacks output_sha256")
    if set(hashes) != set(REQUIRED_COLLECTION_FILES):
        raise ValueError(
            "collection manifest output set differs from the required truth-free artifacts"
        )
    for relative, expected in hashes.items():
        path = _safe_member(collection, relative)
        if not path.is_file():
            raise ValueError(f"collection output is missing: {relative}")
        observed = sha256(path)
        if observed != expected:
            raise ValueError(
                f"collection output checksum mismatch for {relative}: "
                f"expected {expected}, observed {observed}"
            )


def _validate_input_manifests(collection: Path) -> tuple[dict, dict]:
    primary = _load_json(collection / "input_manifest.json")
    sensitivity = _load_json(collection / "sensitivity_abstain" / "input_manifest.json")
    for name, payload, policy, calls_path in (
        ("primary", primary, "native_declaration", collection / "normalized_caller_calls.tsv"),
        ("sensitivity", sensitivity, "abstain",
         collection / "sensitivity_abstain" / "normalized_caller_calls.tsv"),
    ):
        if payload.get("schema_version") != INPUT_SCHEMA:
            raise ValueError(f"{name} input manifest has the wrong schema")
        if payload.get("truth_free") is not True:
            raise ValueError(f"{name} input manifest is not truth-free")
        if payload.get("singleton_policy") != policy:
            raise ValueError(f"{name} input manifest has the wrong singleton policy")
        expected = payload.get("output_sha256", {}).get("normalized_caller_calls")
        if expected != sha256(calls_path):
            raise ValueError(f"{name} caller-input checksum mismatch")
    if primary.get("source_sha256") != sensitivity.get("source_sha256"):
        raise ValueError("primary and abstain input manifests do not share one source")
    source_hash = primary.get("source_sha256", {}).get("collected_calls")
    if source_hash != sha256(collection / "normalized_caller_calls.tsv"):
        raise ValueError("input-manifest source checksum does not identify collected calls")
    return primary, sensitivity


def _expected_cell_keys(roster: list[dict[str, str]]) -> set[tuple[str, str, str, str]]:
    return {
        (row["sample_id"], row["modality"], gene, caller)
        for row in roster
        for caller in PANELS[row["modality"]]
        for gene in GENES
    }


def _validate_caller_grid(
    collection: Path, roster: list[dict[str, str]]
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    primary = read_tsv(collection / "normalized_caller_calls.tsv")
    sensitivity = read_tsv(collection / "sensitivity_abstain" / "normalized_caller_calls.tsv")
    expected = _expected_cell_keys(roster)
    if len(expected) != EXPECTED_CALLER_CELLS:
        raise AssertionError("internal caller-cell accounting error")

    def keyed(rows: list[dict[str, str]], name: str) -> dict[tuple[str, str, str, str], dict]:
        keys = [
            (row.get("subject", ""), row.get("modality", ""),
             row.get("gene", ""), row.get("caller", ""))
            for row in rows
        ]
        if len(keys) != len(set(keys)):
            raise ValueError(f"duplicate caller-gene cells in {name}")
        if set(keys) != expected:
            missing = len(expected - set(keys))
            extra = len(set(keys) - expected)
            raise ValueError(f"{name} caller grid mismatch: {missing} missing, {extra} extra")
        return dict(zip(keys, rows))

    before = keyed(primary, "primary")
    after = keyed(sensitivity, "abstain sensitivity")
    if set(before) != set(after):
        raise ValueError("primary and abstain sensitivity caller grids differ")
    allowed_changes = {"allele1", "allele2", "call_status", "no_call_reason"}
    for key in sorted(before):
        first, second = before[key], after[key]
        changed = {field for field in first if first.get(field, "") != second.get(field, "")}
        if first.get("homozygosity_basis") == "caller_native_declaration":
            if changed - allowed_changes:
                raise ValueError(f"abstain sensitivity changes non-policy fields at {key}")
            if second.get("call_status") != "partial" or second.get("allele1") or second.get("allele2"):
                raise ValueError(f"abstain sensitivity does not abstain at {key}")
        elif changed:
            raise ValueError(f"abstain sensitivity changes a non-native cell at {key}")
    return primary, sensitivity


def _validate_provenance(collection: Path, roster: list[dict[str, str]]) -> None:
    runs = read_tsv(collection / "sample_run_provenance.tsv")
    run_keys = [(row.get("subject", ""), row.get("modality", "")) for row in runs]
    expected_runs = {(row["sample_id"], row["modality"]) for row in roster}
    if len(run_keys) != len(set(run_keys)) or set(run_keys) != expected_runs:
        raise ValueError("sample-run provenance does not account for the exact 236-run roster")
    if any(row.get("sample_complete") != "1" for row in runs):
        raise ValueError("sample-run provenance contains an incomplete run")
    if any(row.get("release_commit") != DEFAULT_RELEASE_COMMIT for row in runs):
        raise ValueError("sample-run provenance contains the wrong release commit")

    tasks = read_tsv(collection / "caller_run_state.tsv")
    task_keys = [
        (row.get("subject", ""), row.get("modality", ""), row.get("caller", ""))
        for row in tasks
    ]
    expected_tasks = {
        (row["sample_id"], row["modality"], caller)
        for row in roster for caller in PANELS[row["modality"]]
    }
    if len(task_keys) != len(set(task_keys)) or set(task_keys) != expected_tasks:
        raise ValueError(
            f"caller-task ledger does not contain exactly {EXPECTED_CALLER_TASKS} expected tasks"
        )

    comparisons = read_tsv(collection / "stored_vs_rerun_cells.tsv")
    comparison_keys = [
        (row.get("subject", ""), row.get("modality", ""),
         row.get("gene", ""), row.get("caller", ""))
        for row in comparisons
    ]
    if len(comparison_keys) != len(set(comparison_keys)):
        raise ValueError("stored-versus-rerun ledger contains duplicate caller cells")
    if set(comparison_keys) != _expected_cell_keys(roster):
        raise ValueError("stored-versus-rerun ledger does not cover the complete rerun grid")


def validate_collection(collection: Path) -> dict:
    collection = collection.resolve()
    gate = _load_json(collection / "rerun_gate.json")
    if gate.get("schema_version") != "champhla-development-rerun-gate-1":
        raise ValueError("rerun gate has the wrong schema")
    if gate.get("status") != "PASS":
        raise ValueError("rerun gate did not pass")
    if gate.get("validator_counts") != {
        "checked": 236, "complete_valid": 236, "incomplete_or_invalid": 0,
    }:
        raise ValueError("rerun gate does not record complete 236-run validation")
    if gate.get("running_jobs") != {
        "champhla_ctl": 0, "champhla_dev": 0, "champhla_prefetch": 0,
    } or gate.get("controller_finished_normally") is not True:
        raise ValueError("rerun gate does not record a quiescent, normally finished controller")
    # The manager that ran the 236 jobs is archived byte for byte; the live script has
    # since gained extension options (run root, job name, amendment guard).
    if gate.get("execution_manager_sha256") != sha256(ROOT / DEPLOYED_MANAGER):
        raise ValueError("rerun gate execution-manager hash does not match the deployed manager")
    if gate.get("roster_sha256") != sha256(
        ROOT / "cohorts/development_rerun_manifest.tsv"
    ):
        raise ValueError("rerun gate roster hash does not match this source tree")
    manifest = _load_json(collection / "collection_manifest.json")
    if manifest.get("schema_version") != COLLECTION_SCHEMA:
        raise ValueError("collection manifest has the wrong schema")
    if manifest.get("truth_free") is not True:
        raise ValueError("collection manifest is not truth-free")
    if manifest.get("release_commit") != DEFAULT_RELEASE_COMMIT:
        raise ValueError(
            f"wrong release commit: expected {DEFAULT_RELEASE_COMMIT}, "
            f"observed {manifest.get('release_commit')}"
        )
    _validate_output_hashes(collection, manifest)
    roster = _validate_selected_roster(collection, manifest)
    _reject_truth_headers(collection)
    _validate_input_manifests(collection)
    primary, sensitivity = _validate_caller_grid(collection, roster)
    _validate_provenance(collection, roster)
    if manifest.get("caller_rows") != EXPECTED_CALLER_CELLS:
        raise ValueError("collection manifest caller-row count is not 3,222")
    if manifest.get("caller_run_state_rows") != EXPECTED_CALLER_TASKS:
        raise ValueError("collection manifest caller-task count is not 1,074")
    return {
        "manifest": manifest,
        "primary": primary,
        "sensitivity": sensitivity,
        "roster": roster,
    }


def _manifest_for_activation(
    source: dict, caller_path: Path, secondary_path: Path, caller_rows: list[dict[str, str]],
    policy: str, collection_manifest_hash: str,
) -> dict:
    return {
        **source,
        "schema_version": INPUT_SCHEMA,
        "truth_free": True,
        "singleton_policy": policy,
        "source_identifiers": {
            "caller_rows": "complete checksum-valid ChampHLA v3.5.0 development rerun",
            "method_rows": "historical secondary rows retained only for fixed outer folds",
        },
        "source_sha256": source["source_sha256"],
        "collection_manifest_sha256": collection_manifest_hash,
        "cohort_labels": {"collection": COLLECTION_COHORT, "analysis": ANALYSIS_COHORT},
        "output_sha256": {
            "normalized_caller_calls": sha256(caller_path),
            "normalized_secondary_calls": sha256(secondary_path),
        },
        "rows": {
            "caller": len(caller_rows),
            "secondary": len(read_tsv(secondary_path)),
        },
        "partial_rows": sum(row.get("call_status") == "partial" for row in caller_rows),
        "native_homozygous_rows": sum(
            row.get("homozygosity_basis") == "caller_native_declaration"
            for row in caller_rows
        ),
        "modalities": ["wes", "rnaseq"],
        "identity_controls": {
            "rerun_manifest_enforced": True,
            "rerun_manifest_sha256": sha256(ROOT / "cohorts/development_rerun_manifest.tsv"),
            "excluded_subject_assays": [],
            "excluded_caller_rows": 0,
        },
    }


def _archive(collection: Path, destination: Path, provenance: Path) -> dict:
    if provenance.exists() and any(provenance.iterdir()):
        raise ValueError(f"provenance directory must be new or empty: {provenance}")
    provenance.mkdir(parents=True, exist_ok=True)
    collection_archive = provenance / "truth_free_collection"
    if collection_archive.exists():
        raise ValueError(f"collection archive already exists: {collection_archive}")
    shutil.copytree(collection, collection_archive, symlinks=False)
    historical = provenance / "historical_inputs_pre_v350"
    historical.mkdir()
    archived = {}
    for relative in (
        "normalized_caller_calls.tsv",
        "input_manifest.json",
        "excluded_caller_calls.tsv",
        "sensitivity_abstain/normalized_caller_calls.tsv",
        "sensitivity_abstain/input_manifest.json",
        "sensitivity_abstain/excluded_caller_calls.tsv",
    ):
        source = destination / relative
        if source.is_file():
            target = historical / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            archived[relative] = sha256(target)
    if "normalized_caller_calls.tsv" not in archived:
        raise ValueError("destination lacks the historical normalized caller table")
    registry = ROOT / "result_registry.tsv"
    if not registry.is_file():
        raise ValueError("source tree lacks the historical result registry")
    registry_target = provenance / "historical_result_registry_pre_v350.tsv"
    shutil.copy2(registry, registry_target)
    archived["result_registry.tsv"] = sha256(registry_target)
    return archived


def _install_transaction(staged: Path, destination: Path, relatives: tuple[str, ...]) -> None:
    rollback = staged / "rollback"
    rollback.mkdir()
    installed: list[str] = []
    try:
        for relative in relatives:
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            backup = rollback / relative
            if target.exists():
                backup.parent.mkdir(parents=True, exist_ok=True)
                os.replace(target, backup)
            os.replace(staged / relative, target)
            installed.append(relative)
    except Exception:
        for relative in reversed(installed):
            target = destination / relative
            target.unlink(missing_ok=True)
            backup = rollback / relative
            if backup.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                os.replace(backup, target)
        raise


def activate(collection: Path, destination: Path, provenance: Path) -> dict:
    collection, destination, provenance = (
        collection.resolve(), destination.resolve(), provenance.resolve()
    )
    if collection == destination or collection == provenance or destination == provenance:
        raise ValueError("collection, destination and provenance directories must differ")
    validated = validate_collection(collection)
    secondary = destination / "normalized_secondary_calls.tsv"
    sensitivity_secondary = destination / "sensitivity_abstain" / "normalized_secondary_calls.tsv"
    policy = destination / "frozen_raw_cc_policy.json"
    for path in (secondary, sensitivity_secondary, policy):
        if not path.is_file():
            raise ValueError(f"required historical fold/policy input is missing: {path}")
    if sha256(secondary) != sha256(sensitivity_secondary):
        raise ValueError("primary and sensitivity secondary rows differ")

    archived = _archive(collection, destination, provenance)
    with tempfile.TemporaryDirectory(prefix="champhla-rerun-activation-",
                                     dir=destination.parent) as temporary:
        staged = Path(temporary)
        primary_source = collection / "normalized_caller_calls.tsv"
        sensitivity_source = collection / "sensitivity_abstain" / "normalized_caller_calls.tsv"
        for source, relative in (
            (primary_source, "normalized_caller_calls.tsv"),
            (sensitivity_source, "sensitivity_abstain/normalized_caller_calls.tsv"),
        ):
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            rows = read_tsv(source)
            labels = {row.get("cohort", "") for row in rows}
            if labels != {COLLECTION_COHORT}:
                raise ValueError(f"unexpected collection cohort labels in {relative}: {sorted(labels)}")
            write_tsv(target, [{**row, "cohort": ANALYSIS_COHORT} for row in rows],
                      CALLER_INPUT_FIELDS)
        write_tsv(staged / "excluded_caller_calls.tsv", [], CALLER_INPUT_FIELDS)
        write_tsv(staged / "sensitivity_abstain/excluded_caller_calls.tsv", [], CALLER_INPUT_FIELDS)
        collection_hash = sha256(collection / "collection_manifest.json")
        write_json(
            staged / "input_manifest.json",
            _manifest_for_activation(
                _load_json(collection / "input_manifest.json"),
                staged / "normalized_caller_calls.tsv", secondary,
                validated["primary"], "native_declaration", collection_hash,
            ),
        )
        write_json(
            staged / "sensitivity_abstain/input_manifest.json",
            _manifest_for_activation(
                _load_json(collection / "sensitivity_abstain/input_manifest.json"),
                staged / "sensitivity_abstain/normalized_caller_calls.tsv", secondary,
                validated["sensitivity"], "abstain", collection_hash,
            ),
        )
        relatives = (
            "normalized_caller_calls.tsv",
            "input_manifest.json",
            "excluded_caller_calls.tsv",
            "sensitivity_abstain/normalized_caller_calls.tsv",
            "sensitivity_abstain/input_manifest.json",
            "sensitivity_abstain/excluded_caller_calls.tsv",
        )
        _install_transaction(staged, destination, relatives)

    report = {
        "schema_version": "champhla-development-rerun-activation-1",
        "status": "activated",
        "truth_free": True,
        "release_commit": DEFAULT_RELEASE_COMMIT,
        "sample_assays": sum(EXPECTED_ASSAYS.values()),
        "assay_counts": EXPECTED_ASSAYS,
        "caller_cells": EXPECTED_CALLER_CELLS,
        "caller_tasks": EXPECTED_CALLER_TASKS,
        "collection_manifest_sha256": sha256(collection / "collection_manifest.json"),
        "historical_archived_sha256": archived,
        "active_sha256": {
            relative: sha256(destination / relative)
            for relative in (
                "normalized_caller_calls.tsv",
                "input_manifest.json",
                "sensitivity_abstain/normalized_caller_calls.tsv",
                "sensitivity_abstain/input_manifest.json",
                "normalized_secondary_calls.tsv",
                "frozen_raw_cc_policy.json",
            )
        },
        "secondary_use": "fixed outer-fold assignments only; fitted predictions must be regenerated",
    }
    write_json(provenance / "activation_report.json", report)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection-dir", type=Path, required=True)
    parser.add_argument("--destination", type=Path, default=ROOT / "data/development")
    parser.add_argument("--provenance-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = activate(args.collection_dir, args.destination, args.provenance_dir)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        raise SystemExit(f"activation refused: {exc}") from exc
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
