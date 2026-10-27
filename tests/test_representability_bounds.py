from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from champhla_confirmation.panels import PANELS

ROOT = Path(__file__).resolve().parents[1]
SUMMARY = (
    ROOT / "artifacts" / "development_characterisation"
    / "caller_truth_representability_summary.tsv"
)
MANIFEST = ROOT / "resources" / "caller_native" / "MANIFEST.json"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _slug(value: str) -> str:
    import re
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def test_representability_is_limited_to_intended_assay_panels():
    rows = _rows(SUMMARY)
    observed = {(row["modality"], row["caller"]) for row in rows}
    expected = {
        (modality, caller)
        for modality in ("wes", "rnaseq")
        for caller in PANELS[modality]
    }
    assert observed == expected


def test_native_list_checksums_and_complete_membership_recompute():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["callers"]
    for row in _rows(SUMMARY):
        caller = row["caller"]
        allele_list = ROOT / manifest[caller]["allele_list"]
        assert row["allele_list_sha256"] == _sha256(allele_list)
        assert row["allele_list_sha256"] == manifest[caller]["sha256"]
        assert int(row["representable_loci"]) == int(row["loci"])
        assert int(row["representable_allele_copies"]) == int(row["truth_allele_copies"])
        assert float(row["representability"]) == 1
        assert float(row["allele_copy_representability"]) == 1


def test_every_representability_result_is_registry_backed_and_bounded():
    registry = {row["result_id"]: row for row in _rows(ROOT / "result_registry.tsv")}
    for row in _rows(SUMMARY):
        result_id = (
            f"DEV_NATIVE_REPRESENTABILITY_{row['modality'].upper()}_"
            f"{_slug(row['caller'])}"
        )
        registered = registry[result_id]
        assert registered["artifact_sha256"] == _sha256(SUMMARY)
        assert "not reconstruction" in registered["claim_boundary"]
        assert registered["abstract_allowed"] == "0"
    supplement = (
        ROOT / "manuscripts" / "benchmark" / "supplementary.md"
    ).read_text(encoding="utf-8")
    assert "not evidence that an\nolder database improves accuracy" in supplement
    assert "Presence is necessary but\nnot sufficient" in supplement
