"""Characterise the plurality vote itself: is its own agreement a confidence signal?

The paper reports that the callers "expose no common confidence scale", which is true
of the callers individually. It is not true of the panel: the number of callers backing
the emitted pair is a scale the vote produces for free, and it turns out to be strongly
calibrated. That matters to a practitioner deciding which calls to accept unreviewed.

Two tables are written:

* ``support_calibration.tsv`` -- accuracy by vote support, as ``top_support`` of
  ``callable_tools``. A locus where only some of the panel could be called is reported
  under its own denominator rather than being folded in with the full-panel loci,
  because those are different situations.
* ``tie_audit.tsv`` -- how often the frozen alphabetical tie-break was invoked and how
  often it was right. Ties are rare, and the rule is arbitrary by construction, so the
  honest thing is to count them rather than to describe them.

The input carries reference-typing columns and is therefore not version-controlled; the
outputs carry counts only.

Usage:
    python scripts/plurality_support_calibration.py <joined.tsv> <out_dir>
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import METHOD_PLURALITY, PANELS  # noqa: E402

TRUE_TOKENS = {"1", "true", "True", "TRUE"}


def _pair(first: str, second: str) -> tuple[str, str]:
    return tuple(sorted([first.strip(), second.strip()]))


def _plurality_rows(path: Path) -> list[dict]:
    """Rows emitted by the plurality rule under its machine identifier.

    ``MajorityVote`` is the same rule under its historical name and is emitted as a
    duplicate row; including both would double every count here.
    """
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        return [row for row in csv.DictReader(handle, delimiter="\t")
                if row["method"] == METHOD_PLURALITY and (row.get("truth_allele1") or "").strip()]


def calibration(rows: list[dict]) -> list[dict]:
    buckets: dict[tuple[str, int, int], list[int]] = defaultdict(lambda: [0, 0])
    for row in rows:
        modality = row["modality"]
        if modality not in PANELS:
            continue
        support, callable_tools = int(row["top_support"]), int(row["callable_tools"])
        correct = _pair(row["allele1"], row["allele2"]) == _pair(row["truth_allele1"],
                                                                 row["truth_allele2"])
        bucket = buckets[(modality, support, callable_tools)]
        bucket[0] += 1
        bucket[1] += int(correct)
    out = []
    for (modality, support, callable_tools), (loci, correct) in sorted(buckets.items()):
        out.append({
            "modality": modality,
            "panel_size": len(PANELS[modality]),
            "callable_tools": callable_tools,
            "top_support": support,
            "support_label": f"{support}/{callable_tools}",
            "full_panel": int(callable_tools == len(PANELS[modality])),
            "loci": loci,
            "correct": correct,
            "accuracy": correct / loci,
        })
    return out


def ties(rows: list[dict]) -> list[dict]:
    buckets: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for row in rows:
        modality = row["modality"]
        if modality not in PANELS or row["tie_at_top"] not in TRUE_TOKENS:
            continue
        correct = _pair(row["allele1"], row["allele2"]) == _pair(row["truth_allele1"],
                                                                 row["truth_allele2"])
        buckets[modality][0] += 1
        buckets[modality][1] += int(correct)
    return [{"modality": modality, "tied_loci": tied, "tie_break_correct": correct,
             "tie_break_accuracy": (correct / tied) if tied else 0.0}
            for modality, (tied, correct) in sorted(buckets.items())]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        raise SystemExit(__doc__)
    joined, out_dir = Path(argv[1]), Path(argv[2])
    if not joined.is_file():
        raise SystemExit(f"missing joined table: {joined}\n"
                         "Rebuild it with join_truth_once before running this.")
    rows = _plurality_rows(joined)
    if not rows:
        raise SystemExit(f"no {METHOD_PLURALITY} rows with truth in {joined}")
    calibration_rows, tie_rows = calibration(rows), ties(rows)
    write_tsv(out_dir / "support_calibration.tsv", calibration_rows)
    write_tsv(out_dir / "tie_audit.tsv", tie_rows)
    print(f"wrote {out_dir / 'support_calibration.tsv'} ({len(calibration_rows)} rows)")
    for row in calibration_rows:
        print(f"  {row['modality']:<7} {row['support_label']:>6}  "
              f"{row['correct']:>4}/{row['loci']:<4} {row['accuracy']:.3f}")
    print(f"wrote {out_dir / 'tie_audit.tsv'}")
    for row in tie_rows:
        print(f"  {row['modality']:<7} ties={row['tied_loci']} "
              f"correct={row['tie_break_correct']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
