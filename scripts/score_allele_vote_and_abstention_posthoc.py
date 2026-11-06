"""POST HOC: an allele-level vote, and the vote's callability trade-off by support.

decisions/20261106_posthoc_round3_amendment.json, B8. Exact-endpoint loci only.

(a) Each callable panel caller contributes two allele copies, a homozygote two of one
allele. With n callable callers and c(a) the copies of allele a, a1 is the allele with
most copies; the call is a1 homozygous if c(a1) - n is at least the largest c(b) for b
other than a1, and otherwise a1 with the next allele. Ties go to the alphabetically
first. A labelled post hoc row, not a candidate primary.

(b) For every support threshold from 1 to the panel size, the loci called and correct
when ChampHLA-Consensus abstains below that support, support being the number of
callers voting for the reported genotype.

Writes ``allele_level_vote_posthoc.tsv`` and ``vote_abstention_tradeoff_posthoc.tsv`` in
``artifacts/development_characterisation``.
"""
from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import METHOD_PLURALITY, PANELS  # noqa: E402

PER_LOCUS = ROOT / "artifacts" / "development_corrected" / "per_locus_results.tsv"
PREDICTIONS = ROOT / "runtime_data" / "development_predictions.tsv"
OUT = ROOT / "artifacts" / "development_characterisation"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _top(counter: Counter) -> str:
    best = max(counter.values())
    return min(allele for allele, count in counter.items() if count == best)


def allele_vote(pairs: list[tuple[str, str]]) -> tuple[str, str] | None:
    """The allele-level call for one locus from the callable callers' pairs."""
    if not pairs:
        return None
    copies = Counter(allele for pair in pairs for allele in pair)
    first = _top(copies)
    rest = Counter({allele: count for allele, count in copies.items() if allele != first})
    if not rest or copies[first] - len(pairs) >= max(rest.values()):
        return (first, first)
    return tuple(sorted((first, _top(rest))))


def main() -> int:
    truth, calls, vote = {}, defaultdict(list), {}
    for row in read(PER_LOCUS):
        if row["modality"] not in PANELS:
            continue
        locus = (row["subject"], row["modality"], row["gene"])
        truth[locus] = tuple(sorted((row["truth_allele1"], row["truth_allele2"])))
        if row["method"].startswith("Caller:") and row["call_status"] == "callable":
            calls[locus].append(tuple(sorted((row["allele1"], row["allele2"]))))
        if row["method"] == METHOD_PLURALITY:
            vote[locus] = (row["call_status"] == "callable", row["correct"] == "1")
    support = {(r["subject"], r["modality"], r["gene"]): int(r["top_support"] or 0)
               for r in read(PREDICTIONS) if r["method"] == METHOD_PLURALITY}
    allele_rows, tradeoff = [], []
    for modality in sorted({locus[1] for locus in truth}):
        loci = sorted(locus for locus in truth if locus[1] == modality)
        correct = sum(allele_vote(calls[locus]) == truth[locus] for locus in loci)
        differs = sum(allele_vote(calls[locus]) != _plurality_pair(calls[locus]) for locus in loci)
        allele_rows.append({"modality": modality, "loci": len(loci),
                            "allele_vote_correct": correct,
                            "plurality_correct": sum(vote[l][1] for l in loci),
                            "loci_where_calls_differ": differs})
        for threshold in range(1, len(PANELS[modality]) + 1):
            kept = [l for l in loci if vote[l][0] and support[l] >= threshold]
            tradeoff.append({"modality": modality, "minimum_support": threshold,
                             "loci": len(loci), "called": len(kept),
                             "correct": sum(vote[l][1] for l in kept)})
    write_tsv(OUT / "allele_level_vote_posthoc.tsv", allele_rows, list(allele_rows[0]))
    write_tsv(OUT / "vote_abstention_tradeoff_posthoc.tsv", tradeoff, list(tradeoff[0]))
    for row in allele_rows + tradeoff:
        print(row)
    return 0


def _plurality_pair(pairs: list[tuple[str, str]]) -> tuple[str, str] | None:
    """The genotype vote with the alphabetical tie-break, for counting differing calls."""
    if not pairs:
        return None
    counts = Counter(pairs)
    best = max(counts.values())
    return min(pair for pair, count in counts.items() if count == best)


if __name__ == "__main__":
    raise SystemExit(main())
