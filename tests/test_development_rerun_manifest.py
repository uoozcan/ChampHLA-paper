import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_development_rerun_manifest",
    ROOT / "scripts/build_development_rerun_manifest.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_real_development_roster_has_exact_unique_matches():
    rows = MODULE.build_rows(
        MODULE.read_tsv(MODULE.DEFAULT_CALLS),
        MODULE.read_tsv(MODULE.DEFAULT_ASSAYS),
    )
    pairs = {(row["sample_id"], row["modality"]) for row in rows}

    assert len(rows) == len(pairs) == 236
    assert sum(row["modality"] == "wes" for row in rows) == 130
    assert sum(row["modality"] == "rnaseq" for row in rows) == 106
    assert all(row["source_input_md5"] for row in rows if row["modality"] == "wes")
    assert all(not row["source_input_md5"] for row in rows if row["modality"] == "rnaseq")
    assert all("allele" not in field for field in MODULE.OUTPUT_FIELDS)


def test_batch_assignment_is_stable_and_bounded():
    rows = MODULE.build_rows(
        MODULE.read_tsv(MODULE.DEFAULT_CALLS),
        MODULE.read_tsv(MODULE.DEFAULT_ASSAYS),
        batch_size=5,
    )
    batches = {}
    for row in rows:
        batches.setdefault(row["batch_id"], []).append(row["sample_id"])

    assert len(batches) == 48
    assert max(map(len, batches.values())) == 5
    assert rows == sorted(rows, key=lambda row: (row["sample_id"], row["modality"]))


def test_missing_or_ambiguous_assay_match_fails_closed():
    caller = [{"subject": "HG1", "modality": "wes"}]
    assay = [
        {
            "sample_id": "HG1",
            "modality": "wes",
            "population": "P",
            "format": "CRAM",
            "genome_build": "GRCh38",
            "input_url": "https://example.test/a.cram",
            "index_url": "https://example.test/a.crai",
            "input_md5": "a" * 32,
            "index_md5": "b" * 32,
            "source_record": "record",
        }
    ]

    with pytest.raises(ValueError, match="missing"):
        MODULE.build_rows(caller, [], expected_counts=None)
    with pytest.raises(ValueError, match="ambiguous"):
        MODULE.build_rows(caller, assay + assay, expected_counts=None)


def test_roster_count_drift_fails_closed():
    caller = [{"subject": "HG1", "modality": "wes"}]
    assay = [
        {
            "sample_id": "HG1",
            "modality": "wes",
            "population": "P",
            "format": "CRAM",
            "genome_build": "GRCh38",
            "input_url": "https://example.test/a.cram",
            "index_url": "https://example.test/a.crai",
            "input_md5": "a" * 32,
            "index_md5": "b" * 32,
            "source_record": "record",
        }
    ]

    with pytest.raises(ValueError, match="roster counts changed"):
        MODULE.build_rows(caller, assay)
