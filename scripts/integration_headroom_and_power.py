"""What was available to win, and what the study could have detected.

Two questions sit behind this paper's negative finding, and reporting the finding
without them invites a reader to conclude more than the data support.

*How much was there to win?*  A method that selects among caller outputs cannot be
right where every caller is wrong. Comparing the vote against an oracle that takes
any caller's correct answer bounds what any such method could ever have achieved.

*Could a difference have been seen?*  The exact sign-flip test enumerates all 2^k
sign assignments of the k subjects whose net delta is non-zero, so the smallest
attainable two-sided p is 2/2^k = 2^(1-k). Where k is small, no effect of any size
could have reached significance, and "not significant" carries no information. The
resampling curve then answers the practical question: how large a cohort *would*
resolve each comparison.

Outputs, all truth-free:

* ``headroom.tsv``   -- oracle ceiling and recoverable loci per modality
* ``detectability.tsv`` -- per comparator: k, minimum attainable p, whether 0.05 was
  reachable uncorrected and after Holm, and the smallest difference that could have
  been significant with no losses
* ``power_curve.tsv``  -- power against cohort size for every paired comparison

Usage:
    python scripts/integration_headroom_and_power.py <joined.tsv> <out_dir> [iterations]
"""
from __future__ import annotations

import csv
import math
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import METHOD_PLURALITY, PANELS  # noqa: E402
from champhla_confirmation.statistics import exact_cluster_signflip, holm_adjust  # noqa: E402

ALPHA = 0.05
SEED = 20260921
COHORT_SIZES = (130, 200, 300, 500, 1000)
FAMILIES = ("descriptive_comparator", "exploratory_fitted")


def _pair(first: str, second: str) -> tuple[str, str]:
    return tuple(sorted([first.strip(), second.strip()]))


def load(path: Path) -> tuple[dict, dict, dict]:
    """(method, locus) -> correct, and modality -> set of loci."""
    correct: dict[tuple[str, tuple], bool] = {}
    loci: dict[str, set] = defaultdict(set)
    scopes: dict[tuple[str, str], str] = {}
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            modality = row["modality"]
            if modality not in PANELS or not (row.get("truth_allele1") or "").strip():
                continue
            locus = (row["subject"], modality, row["gene"])
            loci[modality].add(locus)
            correct[(row["method"], locus)] = _pair(row["allele1"], row["allele2"]) == _pair(
                row["truth_allele1"], row["truth_allele2"])
            scopes[(modality, row["method"])] = row.get("analysis_scope", "")
    return correct, loci, scopes


def _subject_deltas(correct, loci, modality, comparator) -> dict[str, int]:
    deltas: dict[str, int] = defaultdict(int)
    for locus in loci[modality]:
        vote = correct.get((METHOD_PLURALITY, locus), False)
        # A comparator with no row at a locus scores incorrect there, which is the
        # fixed-denominator convention used throughout the paper.
        deltas[locus[0]] += int(correct.get((comparator, locus), False)) - int(vote)
    return deltas


def headroom(correct, loci) -> list[dict]:
    out = []
    for modality in sorted(loci):
        callers = [f"Caller:{name}" for name in PANELS[modality]]
        vote_ok = {l for l in loci[modality] if correct.get((METHOD_PLURALITY, l), False)}
        oracle_ok = {l for l in loci[modality]
                     if any(correct.get((c, l), False) for c in callers)}
        out.append({
            "modality": modality,
            "loci": len(loci[modality]),
            "consensus_correct": len(vote_ok),
            "oracle_correct": len(oracle_ok),
            "consensus_errors": len(loci[modality]) - len(vote_ok),
            "recoverable_by_any_caller": len(oracle_ok - vote_ok),
            "unreachable_by_any_caller": len(loci[modality] - oracle_ok),
            # If this is ever false the arithmetic above is not a partition and the
            # "recoverable" column would be meaningless.
            "consensus_subset_of_oracle": int(vote_ok <= oracle_ok),
        })
    return out


def _families(correct, loci, scopes, modality) -> dict[str, tuple[list[str], dict]]:
    """Family -> (members, subject deltas), as the paper's paired inference defines them."""
    comparators = sorted({m for m, _ in correct
                          if m != METHOD_PLURALITY and m != "MajorityVote"
                          and (not m.startswith("Caller:")
                               or m[7:] in PANELS[modality])})
    comparators = [c for c in comparators
                   if any((c, l) in correct for l in loci[modality])]
    families = {}
    for family_name in FAMILIES:
        members = [c for c in comparators if scopes.get((modality, c)) == family_name]
        families[family_name] = (members, {c: _subject_deltas(correct, loci, modality, c)
                                           for c in members})
    return families


def _all_win_subjects_needed(family_size: int) -> int:
    """Fewest subjects, all favouring one method, whose exact two-sided sign-flip
    p (2^(1-k)) survives Holm when ranked first in a family of this size."""
    k = 1
    while 2.0 ** (1 - k) * family_size >= ALPHA:
        k += 1
    return k


def detectability(correct, loci, scopes) -> list[dict]:
    out = []
    for modality in sorted(loci):
        for family_name, (family_members, delta_map) in _families(
                correct, loci, scopes, modality).items():
            active = [c for c in family_members if any(delta_map[c].values())]
            family_size = len(active)
            observed_rows = []
            for comparator in active:
                observed_rows.append({
                    "comparator": comparator,
                    "p_value": exact_cluster_signflip(delta_map[comparator].values()),
                })
            observed_adjusted = {
                row["comparator"]: row for row in holm_adjust(observed_rows)
            }
            for comparator in family_members:
                deltas = delta_map[comparator]
                non_zero = [value for value in deltas.values() if value]
                k = len(non_zero)
                min_p = 2.0 ** (1 - k) if k else 1.0
                adjusted = observed_adjusted.get(comparator)
                # A comparison identical to the vote would join the family if it differed.
                needed = _all_win_subjects_needed(
                    family_size if comparator in active else family_size + 1)
                out.append({
                    "modality": modality, "comparator": comparator,
                    "inference_family": family_name,
                    "family_size": family_size,
                    "multiplicity_included": int(comparator in active),
                    "net_loci": sum(non_zero),
                    "discordant_subjects": k,
                    "min_attainable_p": min_p,
                    "observed_p": adjusted["p_value"] if adjusted else 1.0,
                    "observed_holm_p": adjusted["holm_adjusted_p"] if adjusted else 1.0,
                    "significance_reachable_uncorrected": int(min_p < ALPHA),
                    "significance_reachable_holm_worst_case": int(
                        comparator in active and min_p * family_size < ALPHA
                    ),
                    "loci": len(loci[modality]),
                    "all_win_subjects_needed_holm_worst_case": needed,
                    # Each such subject contributes at least one locus, so this is the
                    # smallest difference that could have been significant with no losses.
                    "smallest_detectable_points_no_losses": 100 * needed / len(loci[modality]),
                    "interpretation": "exact_signflip_detectability",
                })
    return out


def power_curve(correct, loci, scopes, iterations: int) -> list[dict]:
    """Joint subject bootstrap with the paper's Holm families.

    Each assay's descriptive-comparator and exploratory-fitted families are
    corrected separately, over the comparisons that differ from the vote, exactly
    as in the observed analysis. A normal approximation to the randomization
    statistic is used inside the projection because an exact enumeration for every
    comparator in thousands of size-1000 replicates is computationally prohibitive.
    The observed analysis continues to use the exact sign-flip test.
    """
    rng = random.Random(SEED)
    out = []

    def approximate_p(values: list[int]) -> float:
        variance = sum(value * value for value in values)
        if variance == 0:
            return 1.0
        z = abs(sum(values)) / math.sqrt(variance)
        return math.erfc(z / math.sqrt(2.0))

    for modality in sorted(loci):
        subjects = sorted({l[0] for l in loci[modality]})
        for family_name, (members, by_method) in _families(
                correct, loci, scopes, modality).items():
            family = [method for method in members if any(by_method[method].values())]
            for size in COHORT_SIZES:
                hits = {method: 0 for method in family}
                for _ in range(iterations):
                    sampled_subjects = [rng.choice(subjects) for _ in range(size)]
                    tests = [{"comparator": method,
                              "p_value": approximate_p([by_method[method][s]
                                                        for s in sampled_subjects])}
                             for method in family]
                    for row in holm_adjust(tests):
                        hits[row["comparator"]] += int(row["holm_significant"])
                for method in members:
                    identical = method not in family
                    out.append({
                        "modality": modality, "comparator": method,
                        "inference_family": family_name,
                        "cohort_subjects": size,
                        "family_size": len(family),
                        "power": "" if identical else f"{hits[method] / iterations:.3f}",
                        "p_value_method": "normal_approximation_to_subject_sign_flip",
                        "multiplicity": "Holm step-down within the comparison's family "
                                        "in each replicate",
                        "note": "identical to the vote at every locus" if identical else
                                "conditional empirical-resampling projection; "
                                "not a sample-size guarantee",
                    })
    return out


def main(argv: list[str]) -> int:
    if len(argv) not in (3, 4):
        raise SystemExit(__doc__)
    joined, out_dir = Path(argv[1]), Path(argv[2])
    iterations = int(argv[3]) if len(argv) == 4 else 2000
    if not joined.is_file():
        raise SystemExit(f"missing joined table: {joined}")
    correct, loci, scopes = load(joined)
    rows = headroom(correct, loci)
    for row in rows:
        if not row["consensus_subset_of_oracle"]:
            raise SystemExit(f"{row['modality']}: consensus-correct is not a subset of "
                             "oracle-correct; the recoverable/unreachable split is invalid")
    write_tsv(out_dir / "headroom.tsv", rows)
    for row in rows:
        print(f"  {row['modality']:<7} errors={row['consensus_errors']:<3} "
              f"recoverable={row['recoverable_by_any_caller']:<3} "
              f"unreachable={row['unreachable_by_any_caller']}")
    detect = detectability(correct, loci, scopes)
    write_tsv(out_dir / "detectability.tsv", detect)
    blind = [r for r in detect if not r["significance_reachable_uncorrected"]]
    print(f"  {len(blind)} of {len(detect)} comparisons could not reach "
          f"p < {ALPHA} at any effect size")
    write_tsv(out_dir / "power_curve.tsv", power_curve(correct, loci, scopes, iterations))
    print(f"wrote headroom.tsv, detectability.tsv, power_curve.tsv into {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
