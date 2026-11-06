"""POST HOC: naive baselines that use no reads, scored leave one subject out.

decisions/20261106_posthoc_round3_amendment.json, B3. For each held-out subject, assay
and gene, the pool is the exact-resolved reference genotypes of every other subject in
that assay and gene. Baseline 1 predicts the pool's most common unordered genotype.
Baseline 2 predicts the pool's two most common alleles, counted over both alleles of
each genotype. Ties go to the alphabetically first. Each baseline is scored on the
exact endpoint, the set-valued endpoint and the loci excluded from the exact endpoint.
These are descriptive rows, not comparators.

Writes ``artifacts/development_characterisation/naive_baselines_posthoc.tsv``.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402

CANDIDATES = ROOT / "runtime_data" / "development_candidate_truth.tsv"
OUTPUT = ROOT / "artifacts" / "development_characterisation" / "naive_baselines_posthoc.tsv"
BASELINES = ("most_common_genotype", "two_most_common_alleles")


def most_common(counter: Counter):
    """Highest count, alphabetically first among ties; None for an empty pool."""
    if not counter:
        return None
    top = max(counter.values())
    return min(item for item, count in counter.items() if count == top)


def predict(pool: list[tuple[str, str]], baseline: str) -> tuple[str, str] | None:
    if baseline == "most_common_genotype":
        return most_common(Counter(pool))
    alleles = Counter(allele for pair in pool for allele in pair)
    first = most_common(alleles)
    if first is None:
        return None
    alleles.pop(first)
    second = most_common(alleles)
    return tuple(sorted((first, second))) if second else (first, first)


def main() -> int:
    candidates, status = {}, {}
    with CANDIDATES.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            pairs = {tuple(pair) for pair in json.loads(row["truth_candidate_pairs_json"])}
            if pairs:
                key = (row["subject"], row["modality"], row["gene"])
                candidates[key], status[key] = pairs, row["truth_status"]
    resolved = {key: next(iter(pairs)) for key, pairs in candidates.items()
                if status[key] == "resolved"}
    out = []
    for modality in sorted({key[1] for key in candidates}):
        loci = sorted(key for key in candidates if key[1] == modality)
        for baseline in BASELINES:
            hits = Counter()
            totals = Counter()
            for locus in loci:
                pool = [pair for key, pair in resolved.items()
                        if key[1] == modality and key[2] == locus[2] and key[0] != locus[0]]
                call = predict(pool, baseline)
                scopes = ["set_valued"]
                scopes.append("exact" if status[locus] == "resolved" else "excluded")
                for scope in scopes:
                    totals[scope] += 1
                    hits[scope] += call is not None and call in candidates[locus]
            out.append({"modality": modality, "baseline": baseline,
                        **{f"{scope}_{part}": (hits if part == "correct" else totals)[scope]
                           for scope in ("exact", "set_valued", "excluded")
                           for part in ("correct", "loci")}})
    write_tsv(OUTPUT, out, list(out[0]))
    for row in out:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
