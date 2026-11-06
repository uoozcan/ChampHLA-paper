"""POST HOC: rescore the plurality and strict-majority votes with each panel caller left out.

decisions/20261105_posthoc_round2_amendment.json. Votes use the same pair-counting and
tie rule as champhla_confirmation.consensus on the truth-free caller table; the 2014
type is read from the per-locus results only to score exact-endpoint loci. This selects
nothing and never changes a panel: it describes how much each row depends on one caller.

Writes ``artifacts/development_characterisation/leave_one_caller_out_posthoc.tsv``.
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.consensus import canonical_pair, is_callable  # noqa: E402
from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import METHOD_PLURALITY, PANELS  # noqa: E402

CALLS = ROOT / "data" / "development" / "normalized_caller_calls.tsv"
PER_LOCUS = ROOT / "artifacts" / "development_corrected" / "per_locus_results.tsv"
OUTPUT = ROOT / "artifacts" / "development_characterisation" / "leave_one_caller_out_posthoc.tsv"
NO_CALLER_LEFT_OUT = "none"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def vote(pairs: dict[str, tuple[str, str]]) -> tuple[tuple[str, str] | None, bool]:
    """Return the plurality pair and whether it also holds a strict majority."""
    tools: dict[tuple[str, str], set[str]] = defaultdict(set)
    for caller, pair in pairs.items():
        tools[pair].add(caller)
    if not tools:
        return None, False
    top = sorted(tools, key=lambda pair: (-len(tools[pair]), pair))[0]
    return top, len(tools[top]) * 2 > len(pairs)


def score(calls: list[dict[str, str]], per_locus: list[dict[str, str]],
          panels: dict[str, tuple[str, ...]]) -> list[dict[str, object]]:
    truth = {
        (row["modality"], row["subject"], row["gene"]):
            tuple(sorted((row["truth_allele1"], row["truth_allele2"])))
        for row in per_locus if row["method"] == METHOD_PLURALITY
    }
    by_locus: dict[tuple[str, str, str], dict[str, tuple[str, str]]] = defaultdict(dict)
    for row in calls:
        locus = (row["modality"], row["subject"], row["gene"])
        if locus in truth and row["caller"] in panels[row["modality"]] and is_callable(row):
            by_locus[locus][row["caller"]] = canonical_pair(
                row["allele1"], row["allele2"], row["gene"])
    results = []
    for modality in sorted(panels):
        loci = sorted(locus for locus in truth if locus[0] == modality)
        if not loci:
            continue
        for left_out in (NO_CALLER_LEFT_OUT, *sorted(panels[modality])):
            plurality_correct = strict_callable = strict_correct = 0
            for locus in loci:
                pairs = {caller: pair for caller, pair in by_locus[locus].items()
                         if caller != left_out}
                pair, majority = vote(pairs)
                correct = pair is not None and tuple(sorted(pair)) == truth[locus]
                plurality_correct += correct
                strict_callable += majority
                strict_correct += majority and correct
            results.append({
                "modality": modality, "left_out": left_out, "loci": len(loci),
                "plurality_correct": plurality_correct,
                "strict_majority_callable": strict_callable,
                "strict_majority_correct": strict_correct,
                "analysis_status": "post_hoc_after_results",
            })
    return results


def main() -> int:
    results = score(read_rows(CALLS), read_rows(PER_LOCUS), PANELS)
    write_tsv(OUTPUT, results)
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(results)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
