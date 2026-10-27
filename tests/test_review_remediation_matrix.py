from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "reports" / "peer_review_20260928_remediation.tsv"


def test_every_review_issue_has_one_evidenced_status():
    with MATRIX.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    ids = [row["issue_id"] for row in rows]
    expected = {f"MAJ-{number:02d}" for number in range(1, 17)} | {
        f"MIN-{number:02d}" for number in range(1, 27)
    }
    assert len(ids) == len(set(ids)) == 42
    assert set(ids) == expected
    for row in rows:
        assert row["status"]
        assert row["implementation_location"]
        assert row["manuscript_location"]
        assert row["validation"]
        assert row["closure_evidence"]
        assert row["status"].startswith("closed") or row["status"].startswith("blocked")
