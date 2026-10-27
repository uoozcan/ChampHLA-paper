"""Guard rails of the confirmatory extension driver (scripts/run_extension.py)."""
from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_extension", ROOT / "scripts" / "run_extension.py")
run_extension = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(run_extension)


def _tsv(path: Path, rows: list[dict]) -> Path:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_frozen_roster_run_cannot_be_redirected():
    with pytest.raises(SystemExit, match="extension locations"):
        run_extension.main(["predict", "--work-dir", "elsewhere"])


def test_dry_run_requires_its_own_work_dir(tmp_path):
    roster = _tsv(tmp_path / "roster.tsv", [{"subject": "S1", "modality": "wes", "population": "X"}])
    with pytest.raises(SystemExit, match="requires --work-dir"):
        run_extension.main(["predict", "--roster", str(roster)])


def test_input_outside_the_roster_fails(tmp_path):
    roster = _tsv(tmp_path / "roster.tsv", [{"subject": "S1", "modality": "wes", "population": "X"}])
    calls = _tsv(tmp_path / "aggregated.tsv", [{"sample": "S9", "tool": "optitype",
                                                 "modality": "wes", "gene": "A",
                                                 "allele1": "A*01:01", "allele2": "A*02:01"}])
    with pytest.raises(ValueError, match="not in the extension roster"):
        run_extension.prepare([calls], roster, run_extension._paths(tmp_path / "work"))


def test_every_panel_caller_keeps_a_row_when_its_output_is_missing(tmp_path):
    roster = _tsv(tmp_path / "roster.tsv", [{"subject": "S1", "modality": "rnaseq", "population": "X"}])
    calls = _tsv(tmp_path / "aggregated.tsv", [{"sample": "S1", "tool": "hlahd", "modality": "rnaseq",
                                                 "gene": "A", "allele1": "HLA-A*02:01:01",
                                                 "allele2": "-"}])
    paths = run_extension._paths(tmp_path / "work")
    manifest = run_extension.prepare([calls], roster, paths)
    with paths["calls"].open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert manifest["caller_rows"] == 3 * 4  # three genes x four RNA-seq panel callers
    hlahd_a = next(r for r in rows if r["caller"] == "HLA-HD" and r["gene"] == "A")
    assert (hlahd_a["allele1"], hlahd_a["homozygosity_basis"]) == ("A*02:01", "caller_native_declaration")
    assert sum(r["no_call_reason"] == "no_caller_output" for r in rows) == 11


def test_unblinding_the_frozen_roster_requires_the_preregistration(tmp_path):
    with pytest.raises(SystemExit, match="truth join not permitted"):
        run_extension.unblind(run_extension._paths(tmp_path), None, dry_run=False)


def _collector_dir(path: Path, subject: str = "S1", modality: str = "rnaseq") -> Path:
    path.mkdir()
    rows = []
    for gene in run_extension.GENES:
        for caller in run_extension.PANELS[modality]:
            callable_t1k = caller == "T1K" and gene == "A"
            rows.append({
                "cohort": "truth-free-rerun",
                "subject": subject,
                "superpopulation": "X",
                "modality": modality,
                "gene": gene,
                "caller": caller,
                "allele1_raw": "A*01:01" if callable_t1k else "",
                "allele2_raw": "A*01:01" if callable_t1k else "",
                "allele1": "A*01:01" if callable_t1k else "",
                "allele2": "A*01:01" if callable_t1k else "",
                "call_status": "callable" if callable_t1k else "missing",
                "no_call_reason": "" if callable_t1k else "caller_task_failed_or_explicit_non_call",
                "homozygosity_basis": "caller_native_declaration" if callable_t1k else "",
                "allele1_suffix": "",
                "allele2_suffix": "",
                "normalization_database_version": "3.65.0",
                "source_path": "samples/rnaseq/S1/results/S1/t1k/S1_t1k.txt" if callable_t1k else "",
                "source_sha256": "a" * 64 if callable_t1k else "",
            })
    calls = _tsv(path / "normalized_caller_calls.tsv", rows)
    t1k = _tsv(path / "t1k_parser_provenance.tsv", [{
        "subject": subject,
        "modality": modality,
        "gene": "A",
        "parser_audit_sha256": "b" * 64,
        "raw_genotype_sha256": "c" * 64,
    }])
    runs = _tsv(path / "sample_run_provenance.tsv", [{
        "subject": subject,
        "modality": modality,
        "release_commit": run_extension.PINNED_RELEASE_COMMIT,
        "sample_complete": "1",
    }])
    selected = _tsv(path / "selected_input_manifest.tsv", [{
        "sample_id": subject,
        "modality": modality,
        "batch_id": "extension-001",
    }])
    outputs = {
        file.name: run_extension.sha256(file)
        for file in (calls, t1k, runs, selected)
    }
    (path / "collection_manifest.json").write_text(json.dumps({
        "schema_version": run_extension.COLLECTION_SCHEMA,
        "truth_free": True,
        "release_commit": run_extension.PINNED_RELEASE_COMMIT,
        "sample_assays": 1,
        "caller_rows": len(rows),
        "t1k_audit_rows": 1,
        "selected_input_manifest_sha256": outputs["selected_input_manifest.tsv"],
        "output_sha256": outputs,
    }), encoding="utf-8")
    return path


def test_collected_prepare_preserves_native_homozygosity_and_exact_grid(tmp_path):
    roster = _tsv(tmp_path / "roster.tsv", [
        {"subject": "S1", "modality": "rnaseq", "population": "X"}
    ])
    collection = _collector_dir(tmp_path / "collection")
    paths = run_extension._paths(tmp_path / "work")

    manifest = run_extension.prepare_collected([collection], roster, paths)

    with paths["calls"].open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    t1k_a = next(row for row in rows if row["caller"] == "T1K" and row["gene"] == "A")
    assert manifest["input_boundary"] == "checksummed_truth_free_collector_outputs"
    assert manifest["caller_rows"] == 12
    assert manifest["explicit_noncall_rows"] == 11
    assert t1k_a["homozygosity_basis"] == "caller_native_declaration"
    assert (t1k_a["allele1"], t1k_a["allele2"]) == ("A*01:01", "A*01:01")


def test_collected_prepare_rejects_tampered_output(tmp_path):
    roster = _tsv(tmp_path / "roster.tsv", [
        {"subject": "S1", "modality": "rnaseq", "population": "X"}
    ])
    collection = _collector_dir(tmp_path / "collection")
    with (collection / "normalized_caller_calls.tsv").open("a", encoding="utf-8") as handle:
        handle.write("tampered\n")

    with pytest.raises(ValueError, match="collection output hash mismatch"):
        run_extension.prepare_collected(
            [collection], roster, run_extension._paths(tmp_path / "work")
        )


def test_frozen_prepare_forbids_aggregate_only_input():
    with pytest.raises(SystemExit, match="aggregate-only input is forbidden"):
        run_extension.main(["prepare", "--aggregated", "historical.tsv"])


def test_collected_prepare_rejects_checksum_valid_incomplete_grid(tmp_path):
    roster = _tsv(tmp_path / "roster.tsv", [
        {"subject": "S1", "modality": "rnaseq", "population": "X"}
    ])
    collection = _collector_dir(tmp_path / "collection")
    calls = collection / "normalized_caller_calls.tsv"
    lines = calls.read_text(encoding="utf-8").splitlines()
    calls.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")
    manifest_path = collection / "collection_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["caller_rows"] -= 1
    manifest["output_sha256"][calls.name] = run_extension.sha256(calls)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="collection bundle caller grid mismatch"):
        run_extension.prepare_collected(
            [collection], roster, run_extension._paths(tmp_path / "work")
        )


def test_collected_prepare_rejects_selected_manifest_run_mismatch(tmp_path):
    roster = _tsv(tmp_path / "roster.tsv", [
        {"subject": "S1", "modality": "rnaseq", "population": "X"}
    ])
    collection = _collector_dir(tmp_path / "collection")
    selected = collection / "selected_input_manifest.tsv"
    selected.write_text(
        "sample_id\tmodality\tbatch_id\nS9\trnaseq\textension-001\n",
        encoding="utf-8",
    )
    manifest_path = collection / "collection_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    digest = run_extension.sha256(selected)
    manifest["output_sha256"][selected.name] = digest
    manifest["selected_input_manifest_sha256"] = digest
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="does not match run provenance"):
        run_extension.prepare_collected(
            [collection], roster, run_extension._paths(tmp_path / "work")
        )


def test_roster_rejects_duplicate_subject_assay(tmp_path):
    roster = _tsv(tmp_path / "roster.tsv", [
        {"subject": "S1", "modality": "rnaseq", "population": "X"},
        {"subject": "S1", "modality": "rnaseq", "population": "X"},
    ])
    with pytest.raises(ValueError, match="duplicate subject-assay"):
        run_extension._roster(roster)
