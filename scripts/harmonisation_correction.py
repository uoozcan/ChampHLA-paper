"""Re-derive the consensus with the harmonisation defect corrected.

Authorised by decisions/20260918_harmonisation_correction.json, signed 2026-09-18.
That record fixes the rule and the endpoint before this runs; nothing here is
chosen after seeing a score.

The defect replaced a caller's undetermined second allele with a copy of the first,
turning a partial call into a confident homozygous genotype. Both corrected rules
are computed, as pre-registered:

  current  the published behaviour, for comparison only
  abstain  PRIMARY. A caller with an undetermined second allele casts no vote at
           that locus and is not counted among the callable voters.
  partial  SENSITIVITY. The same caller instead votes for the one allele it did
           determine, contributing to every candidate pair containing that allele.

The input keeps the raw caller output beside the harmonised result, so no caller
is re-run. Output carries counts only and no reference typing.

    python scripts/harmonisation_correction.py <wes_rows.tsv> <rna_rows.tsv> <out_dir>
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.io import canonical_allele, write_tsv  # noqa: E402
from champhla_confirmation.panels import GENES, PANELS  # noqa: E402

PLACEHOLDERS = {"", "-", ".", "NA", "na", "N/A", "none", "None", "no", "not typed"}
VARIANTS = ("current", "abstain", "partial")
LABEL = {"wes": "wes", "rna": "rnaseq"}


def cell(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def safe_pair(a: str, b: str, gene: str) -> tuple[str, str] | None:
    try:
        first, second = canonical_allele(a, gene), canonical_allele(b, gene)
    except ValueError:
        return None
    if not first or not second:
        return None
    return tuple(sorted((first, second)))


def safe_allele(a: str, gene: str) -> str | None:
    try:
        return canonical_allele(a, gene) or None
    except ValueError:
        return None


def vote(pair_votes: dict[tuple[str, str], int]) -> tuple[str, str] | None:
    """Plurality with alphabetical tie-break, unchanged from the frozen rule."""
    if not pair_votes:
        return None
    return sorted(pair_votes, key=lambda pair: (-pair_votes[pair], pair))[0]


def derive(path: Path, modality: str) -> tuple[list[dict], list[dict], list[dict]]:
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    panel = set(PANELS[modality])
    loci: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    truth: dict[tuple[str, str], tuple[str, str] | None] = {}
    for row in rows:
        gene = cell(row, "gene")
        if gene not in GENES:
            continue
        key = (cell(row, "sample"), gene)
        loci[key].append(row)
        if key not in truth:
            truth[key] = safe_pair(cell(row, "truth_allele1"), cell(row, "truth_allele2"), gene)

    consensus = {v: {"loci": 0, "correct": 0} for v in VARIANTS}
    per_caller = {c: {v: {"loci": 0, "correct": 0} for v in ("current", "abstain")}
                  for c in sorted(panel)}
    abstentions = 0
    # Why the correction moves the score: a placeholder second allele may signal a
    # genuine homozygote rather than a lost allele. Measured, not assumed.
    ev = {"all_loci": 0, "all_homozygous": 0, "affected_loci": 0,
          "affected_homozygous": 0, "affected_rows": 0, "manufactured_correct": 0}

    for key, group in sorted(loci.items()):
        gene = key[1]
        expected = truth.get(key)
        if expected is None:
            continue  # no resolvable two-field reference typing at this locus

        ev["all_loci"] += 1
        if expected[0] == expected[1]:
            ev["all_homozygous"] += 1
        locus_affected = False

        complete: dict[str, tuple[str, str]] = {}
        partial: dict[str, str] = {}
        for row in group:
            caller = cell(row, "tool")
            if caller not in panel:
                continue
            pair = safe_pair(cell(row, "allele1"), cell(row, "allele2"), gene)
            placeholder = cell(row, "allele2_raw") in PLACEHOLDERS
            if pair is None:
                continue
            if placeholder:
                allele = safe_allele(cell(row, "allele1_raw") or cell(row, "allele1"), gene)
                if allele:
                    partial[caller] = allele
                abstentions += 1
                locus_affected = True
                ev["affected_rows"] += 1
                if pair == expected:
                    ev["manufactured_correct"] += 1
                # The published behaviour still counts the manufactured pair.
                complete.setdefault(caller, pair)
            else:
                complete[caller] = pair

        # current: every caller votes, manufactured homozygotes included
        current_votes: dict[tuple[str, str], int] = defaultdict(int)
        for caller, pair in complete.items():
            current_votes[pair] += 1

        # abstain: a caller with an undetermined second allele does not vote
        abstain_votes: dict[tuple[str, str], int] = defaultdict(int)
        for caller, pair in complete.items():
            if caller not in partial:
                abstain_votes[pair] += 1

        # partial: complete votes, plus a determined allele supporting any pair containing it
        partial_votes = dict(abstain_votes)
        for allele in partial.values():
            for pair in list(partial_votes):
                if allele in pair:
                    partial_votes[pair] += 1

        for name, votes in (("current", current_votes), ("abstain", abstain_votes),
                            ("partial", partial_votes)):
            consensus[name]["loci"] += 1
            if vote(votes) == expected:
                consensus[name]["correct"] += 1

        if locus_affected:
            ev["affected_loci"] += 1
            if expected[0] == expected[1]:
                ev["affected_homozygous"] += 1

        for caller in panel:
            pair = complete.get(caller)
            per_caller[caller]["current"]["loci"] += 1
            if pair == expected:
                per_caller[caller]["current"]["correct"] += 1
            per_caller[caller]["abstain"]["loci"] += 1
            if caller not in partial and pair == expected:
                per_caller[caller]["abstain"]["correct"] += 1

    summary = [{
        "modality": modality, "scope": "consensus", "name": "ChampHLA-Consensus",
        "variant": v, "loci": consensus[v]["loci"], "correct": consensus[v]["correct"],
        "delta_vs_current": consensus[v]["correct"] - consensus["current"]["correct"],
    } for v in VARIANTS]

    callers = []
    for caller in sorted(panel):
        for v in ("current", "abstain"):
            callers.append({
                "modality": modality, "scope": "caller", "name": caller, "variant": v,
                "loci": per_caller[caller][v]["loci"],
                "correct": per_caller[caller][v]["correct"],
                "delta_vs_current": (per_caller[caller][v]["correct"]
                                     - per_caller[caller]["current"]["correct"]),
            })
    print(f"  {modality}: {abstentions} caller-locus abstentions under the primary rule")

    def rate(numerator: int, denominator: int) -> str:
        return f"{numerator / denominator:.4f}" if denominator else ""

    baseline = ev["all_homozygous"] / ev["all_loci"] if ev["all_loci"] else 0
    affected = (ev["affected_homozygous"] / ev["affected_loci"]) if ev["affected_loci"] else 0
    evidence = [{
        "modality": modality,
        "all_loci": ev["all_loci"], "all_homozygous": ev["all_homozygous"],
        "baseline_homozygous_rate": rate(ev["all_homozygous"], ev["all_loci"]),
        "affected_loci": ev["affected_loci"],
        "affected_homozygous": ev["affected_homozygous"],
        "affected_homozygous_rate": rate(ev["affected_homozygous"], ev["affected_loci"]),
        "enrichment": f"{affected / baseline:.2f}" if baseline and affected else "",
        "affected_rows": ev["affected_rows"],
        "manufactured_correct": ev["manufactured_correct"],
        "manufactured_correct_rate": rate(ev["manufactured_correct"], ev["affected_rows"]),
    }]
    return summary, callers, evidence


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__)
        return 2
    out_dir = Path(argv[3])
    rows: list[dict] = []
    evidence_rows: list[dict] = []
    for path, modality in ((Path(argv[1]), "wes"), (Path(argv[2]), "rnaseq")):
        summary, callers, evidence = derive(path, modality)
        rows.extend(summary)
        rows.extend(callers)
        evidence_rows.extend(evidence)

    for row in rows:
        leaked = [k for k in row if k.lower().startswith("truth")]
        if leaked:
            raise SystemExit(f"refusing to write truth-bearing columns: {leaked}")

    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "harmonisation_correction_results.tsv"
    write_tsv(target, rows)
    evidence_target = out_dir / "placeholder_homozygosity_evidence.tsv"
    write_tsv(evidence_target, evidence_rows)
    print(f"\nwrote {target}")
    print(f"wrote {evidence_target}")
    for row in evidence_rows:
        print(f"  {row['modality']:<8} placeholder loci homozygous "
              f"{float(row['affected_homozygous_rate']) * 100:.1f}% vs baseline "
              f"{float(row['baseline_homozygous_rate']) * 100:.1f}% "
              f"({row['enrichment']}x); manufactured genotype correct "
              f"{float(row['manufactured_correct_rate']) * 100:.1f}%")

    print(f"\n{'modality':<9}{'variant':<10}{'correct':>9}{'loci':>7}{'delta':>8}")
    for row in rows:
        if row["scope"] != "consensus":
            continue
        print(f"{row['modality']:<9}{row['variant']:<10}{row['correct']:>9}"
              f"{row['loci']:>7}{row['delta_vs_current']:>+8d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
