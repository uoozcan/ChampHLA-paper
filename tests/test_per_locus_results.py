"""The released per-locus results reproduce every reported method total (PSR-037)."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORRECTED = ROOT / "artifacts" / "development_corrected"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_per_locus_results_reproduce_method_totals():
    per_locus = _read(CORRECTED / "per_locus_results.tsv")
    correct = Counter((r["modality"], r["method"]) for r in per_locus if r["correct"] == "1")
    loci = Counter((r["modality"], r["method"]) for r in per_locus)
    for row in _read(CORRECTED / "method_performance.tsv"):
        key = (row["modality"], row["method"])
        assert correct[key] == int(row["genotypes_correct"]), key
        assert loci[key] == int(row["rows_present"]), key


def test_per_locus_results_carry_no_columns_beyond_the_public_inputs():
    with (CORRECTED / "per_locus_results.tsv").open(encoding="utf-8") as handle:
        header = handle.readline().rstrip("\n").split("\t")
    assert header == ["subject", "superpopulation", "modality", "gene", "method",
                      "analysis_scope", "call_status", "allele1", "allele2",
                      "truth_allele1", "truth_allele2", "correct"]
