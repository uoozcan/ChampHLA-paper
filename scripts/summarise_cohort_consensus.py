"""Run the ChampHLA consensus over a cohort's calls and summarise what it supports.

    python scripts/summarise_cohort_consensus.py data/venex/normalized_caller_calls.tsv \
        --modality wes --output-dir artifacts/venex

The cohort this is written for carries **no independent HLA typing**, so nothing here is an
accuracy endpoint. What a truth-free cohort can show is the *structure of caller agreement*:
how much of the panel actually calls each locus, how often the panel splits, how often the
consensus departs from each individual caller, and how often the stricter rules abstain where
plurality still calls. That is the protection thesis measured directly, without a reference.

Every aggregate carries the denominator it was computed on. The per-subject consensus table is
written separately and is **not** an export artifact: it carries subject identifiers.
"""
from __future__ import annotations

import argparse
import collections
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.consensus import build_consensus  # noqa: E402
from champhla_confirmation.io import read_tsv, write_tsv  # noqa: E402
from champhla_confirmation.panels import (  # noqa: E402
    GENES,
    METHOD_BASELINE,
    METHOD_PLURALITY,
    METHOD_STRICT_MAJORITY,
    PANELS,
)
from champhla_recovery.fimm import wilson_interval  # noqa: E402

METHODS = (METHOD_PLURALITY, METHOD_BASELINE, METHOD_STRICT_MAJORITY)
CALLABLE = "callable"


def _pair(row: dict[str, str]) -> tuple[str, str] | None:
    if row.get("allele1") and row.get("allele2"):
        return (row["allele1"], row["allele2"])
    return None


def summarise(calls: list[dict[str, str]], modality: str,
              panels: dict[str, tuple[str, ...]] | None = None) -> dict[str, list[dict]]:
    consensus = build_consensus(calls, panels)
    panel = (panels or PANELS)[modality]

    by_method_gene: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for row in consensus:
        by_method_gene[(row["method"], row["gene"])].append(row)

    # 1. Per method and gene: how often the rule calls at all, and how contested it was.
    method_rows: list[dict] = []
    for method in METHODS:
        for gene in list(GENES) + ["ALL"]:
            rows = (by_method_gene[(method, gene)] if gene != "ALL"
                    else [r for g in GENES for r in by_method_gene[(method, g)]])
            if not rows:
                continue
            called = sum(1 for r in rows if r["call_status"] == CALLABLE)
            ties = sum(1 for r in rows if str(r.get("tie_at_top", "")).lower() in {"1", "true"})
            fractions = [float(r["support_fraction"]) for r in rows
                         if r.get("support_fraction") not in (None, "")]
            low, high = wilson_interval(called, len(rows))
            method_rows.append({
                "method": method, "gene": gene, "loci": len(rows), "called": called,
                "call_rate": called / len(rows) if rows else "",
                "call_rate_ci_lo": low if low is not None else "",
                "call_rate_ci_hi": high if high is not None else "",
                "ties_at_top": ties,
                "mean_support_fraction": sum(fractions) / len(fractions) if fractions else "",
            })

    # 2. How much of the panel was actually available at each locus. A plurality over two
    #    callers is a tie-break, not a vote, so this distribution governs interpretation.
    plurality = [r for r in consensus if r["method"] == METHOD_PLURALITY]
    panel_rows = [
        {"callable_tools": size, "loci": count,
         "share": count / len(plurality) if plurality else "",
         "panel_size": len(panel)}
        for size, count in sorted(collections.Counter(
            int(r["callable_tools"]) for r in plurality).items())
    ]

    # 3. Dissent: where both the consensus and a single caller call, how often do they differ?
    #
    #    Reported twice. At a locus where only one caller called, the plurality *is* that
    #    caller, so agreement is guaranteed by construction and dilutes the rate towards
    #    zero. The `contested` variant keeps only loci where at least two callers called,
    #    which is the only place a vote can disagree with a member. In this cohort that
    #    distinction is decisive: most WES loci have a single callable caller.
    caller_pairs: dict[tuple[str, str, str], tuple[str, str]] = {}
    for row in calls:
        if row["call_status"] == CALLABLE and _pair(row):
            caller_pairs[(row["subject"], row["gene"], row["caller"])] = _pair(row)
    dissent_rows: list[dict] = []
    for caller in panel:
        tally = {"all": [0, 0], "contested": [0, 0]}
        for row in plurality:
            if row["call_status"] != CALLABLE:
                continue
            theirs = caller_pairs.get((row["subject"], row["gene"], caller))
            if theirs is None:
                continue
            agreed = theirs == (row["allele1"], row["allele2"])
            for scope in ("all", "contested"):
                if scope == "contested" and int(row["callable_tools"]) < 2:
                    continue
                tally[scope][0] += 1
                tally[scope][1] += int(agreed)
        row_out = {"caller": caller}
        for scope in ("all", "contested"):
            both, agree = tally[scope]
            low, high = wilson_interval(both - agree, both)
            prefix = "" if scope == "all" else "contested_"
            row_out.update({
                f"{prefix}mutually_callable_loci": both,
                f"{prefix}agreements": agree,
                f"{prefix}dissents": both - agree,
                f"{prefix}dissent_rate": (both - agree) / both if both else "",
                f"{prefix}dissent_ci_lo": low if low is not None else "",
                f"{prefix}dissent_ci_hi": high if high is not None else "",
            })
        dissent_rows.append(row_out)

    # 4. Where the stricter rules abstain although plurality called.
    indexed = {(r["method"], r["subject"], r["gene"]): r for r in consensus}
    rule_rows: list[dict] = []
    for method in (METHOD_BASELINE, METHOD_STRICT_MAJORITY):
        abstained = differs = compared = 0
        for row in plurality:
            other = indexed.get((method, row["subject"], row["gene"]))
            if other is None or row["call_status"] != CALLABLE:
                continue
            compared += 1
            if other["call_status"] != CALLABLE:
                abstained += 1
            elif (other["allele1"], other["allele2"]) != (row["allele1"], row["allele2"]):
                differs += 1
        rule_rows.append({
            "method": method, "compared_against_plurality": compared,
            "abstained_where_plurality_called": abstained,
            "abstention_rate": abstained / compared if compared else "",
            "called_a_different_pair": differs,
        })

    return {
        "consensus": consensus,
        "method_summary": method_rows,
        "panel_composition": panel_rows,
        "plurality_vs_caller": dissent_rows,
        "rule_agreement": rule_rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("calls", type=Path)
    parser.add_argument("--modality", required=True, choices=sorted(PANELS))
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--panel", action="append", default=[], metavar="MODALITY=C1,C2,C3",
        help="override the intended-use panel for a modality; repeat per modality. "
             "Any override is a protocol deviation and belongs in a decisions/ record.")
    args = parser.parse_args(argv)

    panels: dict[str, tuple[str, ...]] | None = None
    if args.panel:
        panels = {modality: tuple(callers) for modality, callers in PANELS.items()}
        for item in args.panel:
            if "=" not in item:
                print(f"--panel needs MODALITY=C1,C2: {item}", file=sys.stderr)
                return 2
            modality, callers = item.split("=", 1)
            panels[modality.strip()] = tuple(
                c.strip() for c in callers.split(",") if c.strip())

    calls = read_tsv(args.calls)
    if not calls:
        print(f"no rows in {args.calls}", file=sys.stderr)
        return 2
    result = summarise(calls, args.modality, panels)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    # Subject-level, therefore secure: kept beside the aggregates but never exported.
    write_tsv(out / "consensus_calls.SECURE.tsv", result["consensus"],
              list(result["consensus"][0]))
    for name in ("method_summary", "panel_composition", "plurality_vs_caller",
                 "rule_agreement"):
        rows = result[name]
        write_tsv(out / f"{name}.tsv", rows, list(rows[0]) if rows else ["empty"])

    subjects = len({r["subject"] for r in calls})
    print(f"cohort rows {len(calls)} subjects {subjects} modality {args.modality}")
    active_panel = (panels or PANELS)[args.modality]
    print(f"  panel {','.join(active_panel)}"
          f"{'  (OVERRIDE, a protocol deviation)' if panels else ''}")
    print(f"  panel composition (callable callers per locus, panel size "
          f"{len(active_panel)}):")
    for row in result["panel_composition"]:
        print(f"    {row['callable_tools']} callers: {row['loci']:>5} loci ({row['share']:.1%})")
    print("  plurality versus each single caller (all loci | contested loci, >=2 callers):")
    for row in result["plurality_vs_caller"]:
        if not row["mutually_callable_loci"]:
            print(f"    {row['caller']:<12} no mutually callable loci")
            continue
        contested = (f"{row['contested_agreements']:>4}/{row['contested_mutually_callable_loci']:<4}"
                     f" dissent {row['contested_dissent_rate']:.3f}"
                     if row["contested_mutually_callable_loci"] else "  no contested loci")
        print(f"    {row['caller']:<12} {row['agreements']:>4}/{row['mutually_callable_loci']:<5}"
              f" dissent {row['dissent_rate']:.3f}   |  {contested}")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
