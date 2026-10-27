"""Compare consensus calls for one specimen across assays, paired by identity.

    python scripts/compare_cross_modality.py \
        --consensus artifacts/fimm_consensus/FIMM-AML-WES/panel3/consensus_calls.SECURE.tsv \
        --consensus artifacts/fimm_consensus/FIMM-AML-BulkRNA/panel3/consensus_calls.SECURE.tsv \
        --consensus artifacts/fimm_consensus/FIMM-AML-SCRNA/panel3/consensus_calls.SECURE.tsv \
        --calls data/fimm/normalized_caller_calls.tsv \
        --output-dir artifacts/fimm_consensus/cross_modality

Pairing is on the specimen identifier (primary) and on the donor identifier (secondary).
It is **never** on allele content: the earlier FIMM analysis matched specimens by allele
fingerprint and then measured HLA concordance on those pairs, which is circular and was
withdrawn (`decisions/20260929_fimm_legacy_withdrawal.json`).

Two caveats are emitted onto every row rather than left to the prose:

* **Shared callers.** Each row carries the caller set behind both sides and their
  intersection. Where the two assays run the same tools, agreement partly measures one tool
  reproducing itself on different input, not two methods concurring.
* **Different specimens.** In the donor-level comparison the two assays may come from
  different specimens of the same patient, where a difference can be disease evolution or
  HLA loss rather than assay disagreement. Those rows are counted separately.
"""
from __future__ import annotations

import argparse
import collections
import csv
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import GENES, METHOD_PLURALITY  # noqa: E402
from champhla_recovery.fimm import wilson_interval  # noqa: E402

CALLABLE = "callable"
ELIGIBILITY_RULES = ("all_callable", "contested_both")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _index(consensus: list[dict[str, str]], method: str) -> dict[tuple[str, str, str], dict]:
    return {
        (row["cohort"], row["subject"], row["gene"]): row
        for row in consensus if row["method"] == method
    }


def _compare(left_rows: dict, right_rows: dict, left: str, right: str,
             panels: dict[str, set[str]], label: str,
             eligibility: str, extra: dict | None = None) -> list[dict]:
    """Exact unordered two-field agreement between two cohorts over shared keys."""
    if eligibility not in ELIGIBILITY_RULES:
        raise ValueError(f"unsupported eligibility rule: {eligibility}")
    out: list[dict] = []
    left_panel = panels.get(left, set())
    right_panel = panels.get(right, set())
    shared = sorted(left_panel & right_panel)
    for gene in list(GENES) + ["ALL"]:
        genes = GENES if gene == "ALL" else (gene,)
        overlap = agree = 0
        for key, lrow in left_rows.items():
            if key[2] not in genes:
                continue
            rrow = right_rows.get((right, key[1], key[2]))
            if rrow is None:
                continue
            if lrow["call_status"] != CALLABLE or rrow["call_status"] != CALLABLE:
                continue
            if eligibility == "contested_both" and (
                int(lrow.get("callable_tools", 0)) < 2
                or int(rrow.get("callable_tools", 0)) < 2
            ):
                continue
            overlap += 1
            if (lrow["allele1"], lrow["allele2"]) == (rrow["allele1"], rrow["allele2"]):
                agree += 1
        low, high = wilson_interval(agree, overlap)
        row = {
            "pairing": label, "eligibility": eligibility,
            "left_cohort": left, "right_cohort": right, "gene": gene,
            "overlap": overlap, "agreement": agree,
            "estimate": agree / overlap if overlap else "",
            "ci_lo": low if low is not None else "",
            "ci_hi": high if high is not None else "",
            "left_panel": ",".join(sorted(left_panel)),
            "right_panel": ",".join(sorted(right_panel)),
            "shared_callers": ",".join(shared),
            "shared_caller_count": len(shared),
            "panels_identical": int(bool(left_panel) and left_panel == right_panel),
        }
        row.update(extra or {})
        out.append(row)
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--consensus", action="append", required=True, type=Path)
    parser.add_argument("--calls", required=True, type=Path,
                        help="calls table supplying the subject-to-donor map")
    parser.add_argument("--method", default=METHOD_PLURALITY)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    consensus: list[dict[str, str]] = []
    for path in args.consensus:
        consensus.extend(read_tsv(path))
    indexed = _index(consensus, args.method)
    if not indexed:
        print(f"no rows for method {args.method}", file=sys.stderr)
        return 2

    calls = read_tsv(args.calls)
    donor_of = {row["subject"]: row.get("donor", "") for row in calls}
    panels: dict[str, set[str]] = collections.defaultdict(set)
    for row in calls:
        panels[row["cohort"]].add(row["caller"])

    cohorts = sorted({key[0] for key in indexed})
    by_cohort: dict[str, dict] = {c: {} for c in cohorts}
    for key, row in indexed.items():
        by_cohort[key[0]][key] = row

    # ---- specimen-level, the primary comparison ----
    specimen_rows: list[dict] = []
    for left, right in itertools.combinations(cohorts, 2):
        for eligibility in ELIGIBILITY_RULES:
            specimen_rows.extend(_compare(
                by_cohort[left], by_cohort[right], left, right, panels,
                "specimen", eligibility,
            ))

    # ---- donor-level, secondary ----
    # One donor may contribute several specimens to a cohort. Collapse them: if the callable
    # specimens agree, that is the donor's call; if they disagree the donor is not called for
    # that cohort and locus, rather than one specimen being picked over another.
    donor_rows: list[dict] = []
    donor_conflicts: collections.Counter[str] = collections.Counter()
    donor_index: dict[str, dict] = {}
    for cohort in cohorts:
        grouped: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
        for key, row in by_cohort[cohort].items():
            donor = donor_of.get(key[1], "")
            if donor:
                grouped[(donor, key[2])].append(row)
        collapsed: dict[tuple[str, str, str], dict] = {}
        for (donor, gene), rows in grouped.items():
            callable_rows = [r for r in rows if r["call_status"] == CALLABLE]
            pairs = {(r["allele1"], r["allele2"]) for r in callable_rows}
            if len(pairs) > 1:
                donor_conflicts[cohort] += 1
                status, pair = "no_call", ("", "")
            elif len(pairs) == 1:
                status, pair = CALLABLE, next(iter(pairs))
            else:
                status, pair = "missing", ("", "")
            collapsed[(cohort, donor, gene)] = {
                "cohort": cohort, "subject": donor, "gene": gene,
                "allele1": pair[0], "allele2": pair[1], "call_status": status,
                "specimens": len({r["subject"] for r in rows}),
                # A donor-level call is contested only when every callable
                # longitudinal specimen contributing to it had >=2 valid callers.
                "callable_tools": min(
                    (int(r.get("callable_tools", 0)) for r in callable_rows),
                    default=0,
                ),
            }
        donor_index[cohort] = collapsed
    for left, right in itertools.combinations(cohorts, 2):
        # The collapse sets a donor to no_call where that donor's own specimens disagree
        # within one cohort, which removes exactly the unstable donors from the comparison.
        # The donor-level estimate is therefore optimistically biased, and the number of
        # donor-loci removed rides on every row so it cannot be quoted without them.
        for eligibility in ELIGIBILITY_RULES:
            donor_rows.extend(_compare(
                donor_index[left], donor_index[right], left, right, panels,
                "donor", eligibility,
                extra={
                    "left_donor_loci_dropped_as_conflict": donor_conflicts.get(left, 0),
                    "right_donor_loci_dropped_as_conflict": donor_conflicts.get(right, 0),
                    "estimate_is_optimistically_biased": 1,
                }))
    for row in specimen_rows:
        row["left_donor_loci_dropped_as_conflict"] = ""
        row["right_donor_loci_dropped_as_conflict"] = ""
        row["estimate_is_optimistically_biased"] = 0

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    rows = specimen_rows + donor_rows
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    write_tsv(out / "cross_modality_agreement.tsv", rows, fields)
    write_tsv(out / "donor_collapse_conflicts.tsv",
              [{"cohort": c, "donor_locus_conflicts": n}
               for c, n in sorted(donor_conflicts.items())] or [{"cohort": "", "donor_locus_conflicts": 0}],
              ["cohort", "donor_locus_conflicts"])

    print(f"method {args.method}; cohorts {', '.join(cohorts)}")
    for row in rows:
        if row["gene"] != "ALL":
            continue
        estimate = f"{row['estimate']:.3f}" if row["estimate"] != "" else "  -  "
        flag = "  [identical panels]" if row["panels_identical"] else ""
        print(f"  {row['pairing']:<9} {row['eligibility']:<15} "
              f"{row['left_cohort']:<18} vs {row['right_cohort']:<18}"
              f" overlap {row['overlap']:>5} agree {row['agreement']:>5} = {estimate}{flag}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
