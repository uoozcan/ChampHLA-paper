"""Measure the algorithm-family challenger diversity gate as a comparator.

Authorised by decisions/20260918_family_gate_measurement.json, which fixes the rule
and the endpoint before this runs.

Supplementary S2 asserts that family and correlation-aware gates give "no material
change in held-out accuracy (<= ~0.5 points)" with no artifact behind the figure.
This produces the number.

The gate is re-applied to the existing Champion-Challenger calls rather than
rebuilding the policy: each CC row records its decision_reason, champion_pair,
challenger_pair and supporting_callers, so an override can be reverted to its
champion exactly. No caller is re-run.

Output carries counts only and no reference typing.

    python scripts/family_gate_measurement.py <joined.tsv> <out_dir>
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.families import (DEFAULT_MIN_SUPPORTING_FAMILIES,  # noqa: E402
                                            supporting_families)
from champhla_confirmation.io import canonical_allele, write_tsv  # noqa: E402

CC = "ChampionChallenger"
OVERRIDE = "challenger_override"
LABEL = {"wes": "wes", "rnaseq": "rnaseq"}


def cell(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def pair_from(value: str, gene: str) -> tuple[str, str] | None:
    """Parse an 'A*01:01+A*29:02' field into a canonical pair."""
    if "+" not in value:
        return None
    a, b = value.split("+", 1)
    try:
        first, second = canonical_allele(a, gene), canonical_allele(b, gene)
    except ValueError:
        return None
    if not first or not second:
        return None
    return tuple(sorted((first, second)))


def pair_of(row: dict[str, str]) -> tuple[str, str] | None:
    gene = cell(row, "gene")
    try:
        a = canonical_allele(cell(row, "allele1"), gene)
        b = canonical_allele(cell(row, "allele2"), gene)
    except ValueError:
        return None
    return tuple(sorted((a, b))) if a and b else None


def truth_of(row: dict[str, str]) -> tuple[str, str] | None:
    gene = cell(row, "gene")
    try:
        a = canonical_allele(cell(row, "truth_allele1"), gene)
        b = canonical_allele(cell(row, "truth_allele2"), gene)
    except ValueError:
        return None
    return tuple(sorted((a, b))) if a and b else None


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    joined, out_dir = Path(argv[1]), Path(argv[2])

    with joined.open(newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    cc_rows = [r for r in rows if r["method"] == CC]
    if not cc_rows:
        raise SystemExit("no ChampionChallenger rows in the joined table")

    summary, detail = [], []
    for modality in ("wes", "rnaseq"):
        subset = [r for r in cc_rows if r["modality"] == modality]
        if not subset:
            continue
        cc_correct = gated_correct = reverted = overrides = 0
        loci = 0
        for row in subset:
            truth = truth_of(row)
            if truth is None:
                continue
            loci += 1
            cc_pair = pair_of(row)
            gated_pair = cc_pair

            if cell(row, "decision_reason") == OVERRIDE:
                overrides += 1
                families = supporting_families(cell(row, "supporting_callers"))
                if len(families) < DEFAULT_MIN_SUPPORTING_FAMILIES:
                    # Gate rejects the override; the champion call is retained.
                    reverted += 1
                    gated_pair = pair_from(cell(row, "champion_pair"), cell(row, "gene"))
                    detail.append({
                        "modality": modality, "subject": row["subject"],
                        "gene": row["gene"],
                        "supporting_callers": cell(row, "supporting_callers"),
                        "families": ",".join(sorted(families)),
                        "family_count": len(families),
                        "override_was_correct": int(cc_pair == truth),
                        "champion_is_correct": int(gated_pair == truth),
                    })

            cc_correct += int(cc_pair == truth)
            gated_correct += int(gated_pair == truth)

        summary.append({
            "modality": modality, "loci": loci,
            "champion_challenger_correct": cc_correct,
            "family_gated_correct": gated_correct,
            "delta": gated_correct - cc_correct,
            "overrides": overrides,
            "overrides_reverted_by_gate": reverted,
            "min_supporting_families": DEFAULT_MIN_SUPPORTING_FAMILIES,
        })

    for row in summary + detail:
        leaked = [k for k in row if k.lower().startswith("truth")]
        if leaked:
            raise SystemExit(f"refusing to write truth-bearing columns: {leaked}")

    out_dir.mkdir(parents=True, exist_ok=True)
    write_tsv(out_dir / "family_gate_results.tsv", summary)
    if detail:
        write_tsv(out_dir / "family_gate_reverted_overrides.tsv", detail)
    print(f"wrote {out_dir / 'family_gate_results.tsv'}")

    print(f"\n{'modality':<9}{'CC':>8}{'gated':>8}{'delta':>8}{'overrides':>11}{'reverted':>10}")
    for row in summary:
        print(f"{row['modality']:<9}{row['champion_challenger_correct']:>8}"
              f"{row['family_gated_correct']:>8}{row['delta']:>+8d}"
              f"{row['overrides']:>11}{row['overrides_reverted_by_gate']:>10}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
