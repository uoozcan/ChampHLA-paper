from __future__ import annotations

import csv
import hashlib
from pathlib import Path

import pytest

from champhla_recovery.compute_provenance import (
    RECORD_TYPE,
    SCHEMA_VERSION,
    _read_sacct,
    build_compute_smoke_registry,
    parse_duration,
    parse_memory,
)


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "provenance" / "compute_smoke" / "raw"
OUTPUT = ROOT / "artifacts" / "compute_smoke_benchmark.tsv"


def test_duration_and_memory_units():
    assert parse_duration("6h 13m 26s") == 22406
    assert parse_duration("268ms") == pytest.approx(0.268)
    assert parse_duration("09:50.210") == pytest.approx(590.210)
    assert parse_memory("10.8 GB") == 10_800_000_000
    assert parse_memory("11070236K") == 11070236 * 1024
    assert parse_memory("") == 0


def test_sacct_combines_parent_and_batch_measurements(tmp_path):
    path = tmp_path / "sacct.psv"
    path.write_text(
        "10|nf-X|COMPLETED|0:0|8|32G|5|00:20.718|||n1|start|end\n"
        "10.batch|batch|COMPLETED|0:0|8||5|00:20.718|1296856K|0|n1|start|end\n"
        "10.extern|extern|COMPLETED|0:0|8||5|00:00:00|||n1|start|end\n",
        encoding="utf-8",
    )
    rows = _read_sacct(path)
    assert rows["10"]["requested_memory"] == "32G"
    assert rows["10"]["max_rss"] == "1296856K"


def test_sacct_rejects_duplicate_parent_jobs(tmp_path):
    row = "10|nf-X|COMPLETED|0:0|8|32G|5|00:20.718|||n1|start|end\n"
    path = tmp_path / "sacct.psv"
    path.write_text(row + row, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate Slurm job"):
        _read_sacct(path)


@pytest.mark.skipif(not RAW.is_dir(), reason="Roihu provenance export is not present")
def test_repository_compute_registry_reconciles_to_raw_sources(tmp_path):
    output = tmp_path / "compute.tsv"
    manifest = tmp_path / "manifest.json"
    rows = build_compute_smoke_registry(RAW, output, manifest)
    assert len(rows) == 14
    assert sum(row["workflow_role"] == "caller" for row in rows) == 11
    assert {row["schema_version"] for row in rows} == {SCHEMA_VERSION}
    assert {row["record_type"] for row in rows} == {RECORD_TYPE}
    assert len({row["native_job_id"] for row in rows}) == 14
    assert all(row["nextflow_status"] == "COMPLETED" for row in rows)
    assert all(row["slurm_state"] == "COMPLETED" for row in rows)
    spec = next(row for row in rows if row["tool"] == "SpecHLA")
    assert spec["execution_mode"] == "native_local_install"
    assert not spec["container_sha256"]
    container_rows = [row for row in rows if row["execution_mode"] == "apptainer_sif"]
    assert container_rows and all(len(str(row["container_sha256"])) == 64
                                  for row in container_rows)

    with output.open(newline="", encoding="utf-8") as handle:
        written = list(csv.DictReader(handle, delimiter="\t"))
    assert len(written) == 14


@pytest.mark.skipif(not OUTPUT.is_file(), reason="compute-smoke registry not generated")
def test_committed_compute_registry_hashes_are_well_formed():
    with OUTPUT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 14
    for row in rows:
        for field in ("command_sha256", "launch_wrapper_sha256", "raw_trace_sha256",
                      "raw_sacct_sha256", "source_manifest_sha256"):
            assert len(row[field]) == 64
            int(row[field], 16)
    assert hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
