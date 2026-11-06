from __future__ import annotations

import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "artifacts" / "protocol_change_ledger.tsv"


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_protocol_change_ledger_is_complete_and_every_record_resolves():
    rows = _rows(LEDGER)
    assert len(rows) == 19
    assert len({row["change_id"] for row in rows}) == len(rows)
    for row in rows:
        assert row["direction_and_size"]
        assert row["verdict_effect"]
        assert row["truth_exposure"]
        for record in row["decision_record"].split(";"):
            assert (ROOT / record).is_file(), record
        for artifact in row["evidence_artifact"].split(";"):
            assert (ROOT / artifact).is_file(), artifact


def test_frozen_primary_failure_and_prior_truth_exposure_are_plain():
    row = next(row for row in _rows(LEDGER) if row["change_id"] == "frozen_protocol")
    assert "142/153" in row["direction_and_size"]
    assert "143/153" in row["direction_and_size"]
    assert "113/118" in row["direction_and_size"]
    assert "failed to outperform" in row["verdict_effect"]
    assert "not before analysts first saw truth" in row["truth_exposure"]
    manuscript = (ROOT / "manuscripts" / "benchmark" / "supplementary.md").read_text(
        encoding="utf-8"
    )
    assert "This was not the analysts' first sight of truth" in manuscript
    assert "the previous primary method did not outperform" in " ".join(manuscript.split())


def test_protocol_change_ledger_is_registry_backed():
    row = next(
        row for row in _rows(ROOT / "result_registry.tsv")
        if row["result_id"] == "PROTOCOL_CHANGE_LEDGER_20261013"
    )
    assert row["artifact_path"] == "artifacts/protocol_change_ledger.tsv"
    assert row["artifact_sha256"] == _sha256(LEDGER)
    assert row["record_type"] == "protocol_change_ledger"
    assert row["estimate"] == "19"
