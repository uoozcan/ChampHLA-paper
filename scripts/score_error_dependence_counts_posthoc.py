"""POST HOC: joint, expected and same-genotype error counts for every caller pair.

decisions/20261106_posthoc_round3_amendment.json, B2. For each assay and caller pair,
on the fixed denominator and on the loci where the two reference typings agree, this
counts loci where both callers are wrong, the number expected if their errors were
independent, and loci where both return the same wrong callable genotype. A missing or
non-callable call counts as wrong, as in the fixed-denominator phi. Phi is left blank
when either caller has no error or no correct call, where it is undefined.

Writes ``artifacts/development_characterisation/error_dependence_counts_posthoc.tsv``.
"""
from __future__ import annotations

import csv
import math
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import PANELS  # noqa: E402
from adjudicate_reference_discordance import SECOND, load_second_typing  # noqa: E402

PER_LOCUS = ROOT / "artifacts" / "development_corrected" / "per_locus_results.tsv"
OUTPUT = ROOT / "artifacts" / "development_characterisation" / "error_dependence_counts_posthoc.tsv"
FIELDS = ["modality", "scope", "caller1", "caller2", "loci", "caller1_errors",
          "caller2_errors", "both_wrong", "expected_both_wrong_if_independent",
          "both_wrong_same_genotype", "error_phi"]


def _pair(first: str, second: str) -> tuple[str, str]:
    return tuple(sorted((first, second)))


def phi(n00: int, n01: int, n10: int, n11: int) -> float | None:
    """Phi of two error indicators, or None where a margin is empty."""
    denominator = math.sqrt((n10 + n11) * (n00 + n01) * (n01 + n11) * (n00 + n10))
    return (n11 * n00 - n10 * n01) / denominator if denominator else None


def pair_counts(loci: list, calls: dict, truth: dict, first: str, second: str) -> dict:
    """Counts for one caller pair over ``loci``; ``calls`` maps (caller, locus) to a pair or None."""
    wrong = {caller: {l for l in loci if calls.get((caller, l)) != truth[l]}
             for caller in (first, second)}
    both = wrong[first] & wrong[second]
    same = sum(1 for l in both
               if calls.get((first, l)) is not None and calls.get((first, l)) == calls.get((second, l)))
    n = len(loci)
    n11 = len(both)
    n10 = len(wrong[first]) - n11
    n01 = len(wrong[second]) - n11
    value = phi(n - n11 - n10 - n01, n01, n10, n11)
    return {"loci": n, "caller1_errors": len(wrong[first]), "caller2_errors": len(wrong[second]),
            "both_wrong": n11,
            "expected_both_wrong_if_independent":
                f"{len(wrong[first]) * len(wrong[second]) / n:.2f}" if n else "",
            "both_wrong_same_genotype": same,
            "error_phi": "" if value is None else f"{value:.6f}"}


def main() -> int:
    with PER_LOCUS.open(newline="", encoding="utf-8") as handle:
        records = [r for r in csv.DictReader(handle, delimiter="\t") if r["modality"] in PANELS]
    truth, calls = {}, {}
    for row in records:
        locus = (row["subject"], row["modality"], row["gene"])
        truth[locus] = _pair(row["truth_allele1"], row["truth_allele2"])
        if row["method"].startswith("Caller:"):
            calls[(row["method"][len("Caller:"):], locus)] = (
                _pair(row["allele1"], row["allele2"]) if row["call_status"] == "callable" else None)
    second = load_second_typing(SECOND, {locus[0] for locus in truth})
    out = []
    for modality in sorted(PANELS):
        full = sorted(l for l in truth if l[1] == modality)
        if not full:  # WGS has no exact-endpoint loci
            continue
        agreed = [l for l in full if second.get((l[0], l[2])) == truth[l]]
        for scope, loci in (("fixed_denominator", full), ("typings_agree", agreed)):
            for first, other in combinations(PANELS[modality], 2):
                out.append({"modality": modality, "scope": scope, "caller1": first,
                            "caller2": other, **pair_counts(loci, calls, truth, first, other)})
    write_tsv(OUTPUT, out, FIELDS)
    for row in out:
        print("\t".join(str(row[field]) for field in FIELDS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
