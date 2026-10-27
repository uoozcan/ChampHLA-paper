import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_rnaseq_ceph_retention_is_registry_backed_and_current():
    with (ROOT / "result_registry.tsv").open(newline="", encoding="utf-8") as handle:
        rows = {row["result_id"]: row for row in csv.DictReader(handle, delimiter="\t")}

    row = rows["DEV_TRUTH_RETENTION_RNASEQ_CEPH"]
    assert (row["correct"], row["loci"]) == ("59", "69")
    assert abs(float(row["estimate"]) - 59 / 69) < 1e-6

    supplement = (ROOT / "manuscripts/benchmark/supplementary.md").read_text(encoding="utf-8")
    assert "rates were 85.5%, 90.2%, 3.9% and 7.4%" in supplement
    assert "[RESULT:DEV_TRUTH_RETENTION_RNASEQ_CEPH]" in supplement
    assert "rates were 84.7%, 90.2%, 3.9% and 7.4%" not in supplement
