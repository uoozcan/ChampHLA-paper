"""Regenerate Markdown tables from corrected development artifacts.

The generator owns only text between explicit BEGIN/END markers. It refuses to
continue if a marker is absent or duplicated, preventing broad manuscript
rewrites and hand-maintained scientific table values.
"""
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "artifacts"
MANUSCRIPT = ROOT / "manuscripts" / "benchmark" / "manuscript.md"
SUPPLEMENT = ROOT / "manuscripts" / "benchmark" / "supplementary.md"

DISPLAY = {
    "wes": "WES", "rnaseq": "RNA-seq", "SimplePluralityLex": "ChampHLA-Consensus",
    "SimpleStrictMajority": "Strict majority",
    "SimpleTwoThirdsConsensus": "Two-thirds consensus",
    "ArcasHLA": "arcasHLA", "Caller:ArcasHLA": "arcasHLA", "Caller:HLA-HD": "HLA-HD",
    "Caller:OptiType": "OptiType", "Caller:POLYSOLVER": "POLYSOLVER",
    "Caller:SpecHLA": "SpecHLA", "Caller:T1K": "T1K",
    "BestSingleTool_nestedCV": "Best single caller (nested CV)",
    "ChampionChallenger": "Champion–challenger",
    "TwoThirdsGuardedCC": "Two-thirds-guarded champion–challenger",
    "MVFlooredCC": "Vote-support-restricted champion–challenger",
    "MetaConsensus": "Logistic meta-consensus",
    "FamilyGatedCC": "Algorithm-family-restricted champion–challenger",
}


def read(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise SystemExit(f"missing table source: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def label(value: str) -> str:
    return DISPLAY.get(value, value)


def pct(value: str, digits: int = 1) -> str:
    return f"{100 * float(value):.{digits}f}"


def number(value: str, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}"


def pvalue(value: str) -> str:
    number_ = float(value)
    if number_ < 0.001:
        return f"{number_:.2e}"
    return f"{number_:.3f}".rstrip("0").rstrip(".")


def table(headers: list[str], rows: list[list[object]], aligns: list[str] | None = None) -> str:
    # Internal registry keys and decision-file paths belong in the machine-readable
    # provenance files rather than wide reader-facing table columns.
    keep = [i for i, value in enumerate(headers)
            if value not in {"Registry ID", "Registry IDs", "Decision record"}]
    rows = [[row[i] for i in keep] for row in rows]
    headers = [headers[i] for i in keep]
    if aligns:
        aligns = [aligns[i] for i in keep]
    def reader_label(value):
        value = str(value)
        for old, new in (("Signed adjudication", "Planned adjudication"),
                         ("signed", "recorded"), ("frozen primary", "previous primary"),
                         ("Frozen primary", "Previous primary"),
                         ("Locked after all", "Specified after all"),
                         ("extension truth remains sealed", "extension reference genotypes have not been used for scoring"),
                         ("Freeze TwoThirdsGuardedCC", "Specify the two-thirds-guarded rule"),
                         ("Fail-closed truth parser", "Exclude unresolved reference genotypes"),
                         ("prediction freeze", "finalize predictions"),
                         ("truth join", "comparison with reference typing")):
            value = value.replace(old, new)
        return value
    rows = [[reader_label(cell) for cell in row] for row in rows]
    headers = [reader_label(value) for value in headers]
    aligns = aligns or ["---"] * len(headers)
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join(aligns) + "|"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def replace_block(path: Path, name: str, content: str) -> None:
    begin, end = f"<!-- BEGIN GENERATED {name} -->", f"<!-- END GENERATED {name} -->"
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(begin) + r".*?" + re.escape(end), re.S)
    if len(pattern.findall(text)) != 1:
        raise SystemExit(f"expected exactly one generated block {name!r} in {path}")
    updated = pattern.sub(f"{begin}\n{content.rstrip()}\n{end}", text)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(updated)


def main_table(performance: list[dict[str, str]],
               corrected_reference: list[dict[str, str]] | None = None) -> str:
    allowed = {"primary", "descriptive_comparator"}
    rows = [
        row for row in performance
        if (
            row["analysis_scope"] in allowed
            or row["method"] == "BestSingleTool_nestedCV"
        )
        and not (
            row["modality"] == "rnaseq"
            and row["method"] == "SimpleTwoThirdsConsensus"
        )
    ]
    order = {
        "SimplePluralityLex": 0, "SimpleStrictMajority": 1,
        "SimpleTwoThirdsConsensus": 2, "Caller:POLYSOLVER": 3,
        "Caller:OptiType": 4, "Caller:SpecHLA": 5, "Caller:T1K": 6,
        "Caller:HLA-HD": 7, "Caller:ArcasHLA": 8,
        "BestSingleTool_nestedCV": 9,
    }
    rows.sort(key=lambda row: ((0 if row["modality"] == "wes" else 1), order[row["method"]]))
    corrected = ({(row["modality"], row["method"]): row for row in corrected_reference}
                 if corrected_reference is not None else None)
    body = []
    for row in rows:
        scope = ("individual caller" if row["method"].startswith("Caller:") else
                 "exploratory fitted; nested CV" if row["method"] == "BestSingleTool_nestedCV" else
                 row["analysis_scope"].replace("_", " "))
        result = [
            label(row["modality"]), label(row["method"]), scope,
            f"{row['callable']}/{row['loci']}", f"{row['genotypes_correct']}/{row['loci']}",
        ]
        if corrected is not None:
            sensitivity = corrected.get((row["modality"], row["method"]))
            if sensitivity is None:
                raise ValueError(
                    f"missing corrected-reference row for {row['modality']} {row['method']}"
                )
            result.append(
                f"{sensitivity['agreement_correct']}/{sensitivity['agreement_loci']}"
            )
        result.extend([
            f"{pct(row['genotype_accuracy'])} "
            f"({pct(row['genotype_ci_lo'])}–{pct(row['genotype_ci_hi'])})",
            f"{pct(row['called_only_accuracy'])} "
            f"({pct(row['called_only_ci_lo'])}–{pct(row['called_only_ci_hi'])})",
        ])
        body.append(result)
    # BMC: a title of at most 15 words above the table, the legend below it.
    title = "**Table 2. Primary and descriptive comparator performance.**\n\n"
    legend = (
        "\n\nConcordance uses the fixed denominator; intervals are 95% subject-cluster\n"
        "percentile bootstrap intervals, or exact Clopper–Pearson intervals for estimates\n"
        "of 0% or 100%. In the four-caller RNA-seq panel, strict majority and\n"
        "two-thirds consensus are mathematically identical and therefore appear once."
    )
    correct_header = "Exact-reference correct" if corrected is not None else "Correct"
    headers = ["Assay", "Method", "Scope", "Callable", correct_header]
    aligns = ["---", "---", "---", "---:", "---:"]
    if corrected is not None:
        headers.append("Corrected-reference sensitivity, correct")
        aligns.append("---:")
    headers.extend(["Fixed-denominator concordance, % (95% CI)",
                    "Called-only concordance, % (95% CI)"])
    aligns.extend(["---:", "---:"])
    return title + table(headers, body, aligns) + legend


def singleton_sensitivity_table(primary: list[dict[str, str]],
                                abstain: list[dict[str, str]]) -> str:
    """Primary native-declaration results beside the abstain-all sensitivity.

    The v3.5.0 T1K parser emits documented native homozygotes as completed pairs,
    so this generated slot reports the requested T1K-completed row without a
    hand-transcribed value.
    """
    primary_rows = {(row["modality"], row["method"]): row for row in primary}
    abstain_rows = {(row["modality"], row["method"]): row for row in abstain}
    if set(primary_rows) != set(abstain_rows):
        raise ValueError("primary and abstain sensitivity method sets differ")
    order = {"wes": 0, "rnaseq": 1}
    body = []
    for key in sorted(primary_rows, key=lambda item: (order.get(item[0], 9), label(item[1]))):
        current, sensitivity = primary_rows[key], abstain_rows[key]
        body.append([
            label(key[0]), label(key[1]), current["analysis_scope"].replace("_", " "),
            f"{current['genotypes_correct']}/{current['loci']}",
            f"{sensitivity['genotypes_correct']}/{sensitivity['loci']}",
            f"{current['callable']}/{current['loci']}",
            f"{sensitivity['callable']}/{sensitivity['loci']}",
        ])
    return table(
        ["Assay", "Method", "Scope", "Native-declaration correct",
         "Abstain-all correct", "Native-declaration callable", "Abstain-all callable"],
        body, ["---", "---", "---", "---:", "---:", "---:", "---:"],
    )


def rerun_cell_comparison_table(rows: list[dict[str, str]]) -> str:
    """Aggregate SR-005's cell ledger without exposing subject identifiers."""
    counts: dict[tuple[str, str, str], int] = {}
    for row in rows:
        key = row["modality"], row["caller"], row["difference_class"]
        counts[key] = counts.get(key, 0) + 1
    body = [[label(modality), label(caller), difference.replace("_", " "), count]
            for (modality, caller, difference), count in sorted(counts.items())]
    return table(
        ["Assay", "Caller", "Stored-to-rerun cell state", "Caller–gene cells"],
        body, ["---", "---", "---", "---:"],
    )


RERUN_CHANGE_CLASSES = ("call_changed", "callable_to_noncall", "noncall_to_callable")
T1K_PARSER_RULE_DISPOSITIONS = ("native_homozygous", "partial_after_quality_filter",
                                "no_call_after_quality_filter")


def rerun_cell_change_character_table(cells: list[dict[str, str]],
                                      t1k: list[dict[str, str]]) -> str:
    """Characterise SR-005's changed cells truth-free; cells new in the rerun are excluded."""
    def pair(row: dict[str, str], side: str) -> tuple[str, ...]:
        return tuple(sorted(allele for allele in (row[f"{side}_allele1"], row[f"{side}_allele2"])
                            if allele))

    def complete(alleles: tuple[str, ...]) -> bool:
        return len(alleles) == 2

    grid = {(row["subject"], row["modality"], row["gene"], row["caller"]): row for row in cells}
    panel: dict[str, set[str]] = {}
    changed_at: dict[tuple[str, str, str], int] = {}
    for row in cells:
        panel.setdefault(row["modality"], set()).add(row["caller"])
        if row["difference_class"] in RERUN_CHANGE_CLASSES:
            locus = row["subject"], row["modality"], row["gene"]
            changed_at[locus] = changed_at.get(locus, 0) + 1
    parser = {(row["subject"], row["modality"], row["gene"]): row["disposition"] for row in t1k}

    counts: dict[tuple[str, str], dict[str, int]] = {}
    for row in cells:
        if row["difference_class"] not in RERUN_CHANGE_CLASSES:
            continue
        modality, caller = row["modality"], row["caller"]
        stored, rerun = pair(row, "stored"), pair(row, "rerun")
        found = ["changed"]
        add = found.append
        if row["difference_class"] != "call_changed":
            add("state")
        elif complete(stored) and complete(rerun):
            stored_hom, rerun_hom = stored[0] == stored[1], rerun[0] == rerun[1]
            if stored_hom and not rerun_hom:
                add("hom_to_het")
            elif rerun_hom and not stored_hom:
                add("het_to_hom")
            elif len(set(stored) & set(rerun)) == 1:
                add("one_replaced")
            else:
                add("both_replaced")
            if sorted(a.split(":")[0] for a in stored) != sorted(a.split(":")[0] for a in rerun):
                add("group_changed")
        else:
            raise ValueError(f"call_changed cell without two alleles: {modality} {caller}")
        if caller == "T1K":
            locus = row["subject"], modality, row["gene"]
            if locus not in parser:
                raise ValueError(f"changed T1K cell without a parser audit row: {modality}")
            if parser[locus] in T1K_PARSER_RULE_DISPOSITIONS:
                add("t1k_rule")
        if changed_at[(row["subject"], modality, row["gene"])] == 1:
            add("alone")
        others = []
        for other in sorted(panel[modality] - {caller}):
            other_row = grid.get((row["subject"], modality, row["gene"], other))
            if other_row is not None and complete(pair(other_row, "rerun")):
                others.append(pair(other_row, "rerun"))
        stored_matches = sum(1 for other in others if complete(stored) and other == stored)
        rerun_matches = sum(1 for other in others if complete(rerun) and other == rerun)
        add("rerun_closer" if rerun_matches > stored_matches
            else "stored_closer" if stored_matches > rerun_matches else "equal")
        tally = counts.setdefault((modality, caller), {})
        for key in found:
            tally[key] = tally.get(key, 0) + 1

    body = []
    columns = ("changed", "state", "hom_to_het", "het_to_hom", "one_replaced",
               "both_replaced", "group_changed", "t1k_rule", "alone", "rerun_closer",
               "stored_closer")
    for (modality, caller), tally in sorted(counts.items()):
        values: list[object] = [tally.get(key, 0) for key in columns]
        if caller != "T1K":
            values[columns.index("t1k_rule")] = "–"
        body.append([label(modality), label(caller), *values])
    # Cells with equal panel matches are the remainder of "Changed cells".
    return table(
        ["Assay", "Caller", "Changed cells", "Call state changed", "Homozygous to heterozygous",
         "Heterozygous to homozygous", "One allele replaced", "Both alleles replaced",
         "Allele group changed", "Follows a 3.5.0 T1K parser rule",
         "Only changed caller at the locus", "Rerun call matches more panel callers",
         "Stored call matches more panel callers"],
        body, ["---", "---"] + ["---:"] * 11,
    )


def rerun_state_table(rows: list[dict[str, str]]) -> str:
    """Aggregate SR-007's checksummed caller-run ledger."""
    counts: dict[tuple[str, str, str], int] = {}
    for row in rows:
        key = row["modality"], row["caller"], row["disposition"]
        counts[key] = counts.get(key, 0) + 1
    body = [[label(modality), label(caller), disposition.replace("_", " "), count]
            for (modality, caller, disposition), count in sorted(counts.items())]
    return table(
        ["Assay", "Caller", "Recorded caller task disposition", "Caller tasks"],
        body, ["---", "---", "---", "---:"],
    )


def cohort_table(rows: list[dict[str, str]]) -> str:
    body = [[label(row["modality"]), row["requested_subjects_before_truth_filter"],
             row["requested_loci"], row["subjects"], row["loci"],
             row["excluded_ambiguous_or_unresolved_loci"],
             row["subjects_shared_between_assays"]] for row in rows]
    return table(["Assay", "Requested subjects", "Requested loci", "Retained subjects",
                  "Retained loci", "Excluded loci", "Retained cross-assay overlap"], body,
                 ["---", "---:", "---:", "---:", "---:", "---:", "---:"])


def performance_table(rows: list[dict[str, str]]) -> str:
    body = []
    for row in rows:
        body.append([label(row["modality"]), label(row["method"]),
                     row["analysis_scope"].replace("_", " "),
                     f"{row['callable']}/{row['loci']} "
                     f"({pct(row['callability_ci_lo'])}–{pct(row['callability_ci_hi'])})",
                     f"{row['genotypes_correct']}/{row['loci']}",
                     f"{pct(row['genotype_accuracy'])} ({pct(row['genotype_ci_lo'])}–{pct(row['genotype_ci_hi'])})",
                     f"{pct(row['called_only_accuracy'])} "
                     f"({pct(row['called_only_ci_lo'])}–{pct(row['called_only_ci_hi'])})",
                     f"{row['alleles_correct']}/{row['alleles_total']}",
                     f"{pct(row['allele_accuracy'])} ({pct(row['allele_ci_lo'])}–{pct(row['allele_ci_hi'])})"])
    return table(["Assay", "Method", "Scope", "Callable (95% CI)", "Genotypes correct",
                  "Fixed-denominator genotype %, 95% CI", "Called-only genotype %, 95% CI",
                  "Alleles correct", "Allele %, 95% CI"], body,
                 ["---", "---", "---", "---:", "---:", "---:", "---:", "---:", "---:"])


def comparison_table(rows: list[dict[str, str]]) -> str:
    body = []
    for row in rows:
        body.append([label(row["modality"]), label(row["comparator"]),
                     f"{row['comparator_correct']}/{row['loci']}",
                     number(row["delta_points"]),
                     row["inference_family"].replace("_", " "), row["family_size"],
                     f"{number(row['pointwise_ci_lo_points'])} to {number(row['pointwise_ci_hi_points'])}",
                     f"{number(row['simultaneous_ci_lo_points'])} to {number(row['simultaneous_ci_hi_points'])}",
                     f"{row['wins']}/{row['losses']}",
                     pvalue(row["signflip_p_value"]),
                     pvalue(row["signflip_holm_adjusted_p"]),
                     "yes" if row["signflip_holm_significant"] == "1" else "no",
                     pvalue(row["holm_adjusted_p"])])
    # decisions/20261009_signflip_governs.json: the sign-flip columns decide
    # significance; the cluster-t columns are descriptive (raw cluster-t p values
    # stay in the source TSV).
    return table(["Assay", "Comparator", "Comparator correct", "Delta, points",
                  "Family", "m", "Pointwise cluster-t 95% CI",
                  "Bonferroni-adjusted cluster-t 95% CI", "Wins/losses",
                  "Sign-flip raw p", "Sign-flip Holm p", "Significant",
                  "Cluster-t Holm p"], body,
                 ["---", "---", "---:", "---:", "---", "---:", "---:", "---:",
                  "---:", "---:", "---:", "---", "---:"])


def stratified_table(rows: list[dict[str, str]]) -> str:
    display_type = {
        "minimum_within_benchmark_truth_allele_count":
            "rarer truth allele: within-benchmark count",
    }
    body = [[label(r["modality"]), display_type.get(
                r["stratum_type"], r["stratum_type"].replace("_", " ")),
             f"HLA-{r['stratum']}" if r["stratum_type"] == "gene" else r["stratum"],
             f"{r['correct']}/{r['loci']}",
             ("suppressed (n<5)" if int(r["loci"]) < 5 else
              f"{pct(r['accuracy'])} ({pct(r['ci_lo'])}–{pct(r['ci_hi'])})")]
            for r in rows]
    return table(["Assay", "Stratum type", "Stratum", "Correct", "Concordance, % (95% CI)"],
                 body, ["---", "---", "---", "---:", "---:"])


def missingness_table(rows: list[dict[str, str]]) -> str:
    body = [[label(r["modality"]), label(r["caller"]), r["loci"], r["rows_present"],
             r["callable"], r["partial"], r["missing"], r["absent"], r["invalid"]]
            for r in rows]
    return table(["Assay", "Caller", "Loci", "Rows", "Callable", "Partial", "Missing",
                  "Absent", "Invalid"], body,
                 ["---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---:"])


def mutually_available_table(rows: list[dict[str, str]]) -> str:
    body = [
        [
            label(r["modality"]),
            label(r["caller"]),
            f"{r['consensus_correct_fixed']}/{r['fixed_loci']}",
            f"{r['caller_correct_fixed']}/{r['fixed_loci']}",
            f"{r['consensus_correct_mutually_available']}/{r['mutually_available_loci']}",
            f"{r['caller_correct_mutually_available']}/{r['mutually_available_loci']}",
            f"{r['consensus_wins_mutually_available']}/"
            f"{r['consensus_losses_mutually_available']}",
            r["absent_subject_gene"] or "none",
        ]
        for r in rows
    ]
    return table(
        [
            "Assay", "Caller", "Plurality, fixed", "Caller, fixed",
            "Plurality, mutually available", "Caller, mutually available",
            "Plurality wins/losses, mutually available", "Absent stored rows",
        ],
        body,
        ["---", "---", "---:", "---:", "---:", "---:", "---:", "---"],
    )


def support_table(rows: list[dict[str, str]]) -> str:
    body = [[label(r["modality"]), r["support_profile"],
             r["tied_loci"], f"{r['correct']}/{r['loci']}",
             f"{pct(r['accuracy'])} ({pct(r['ci_lo'])}–{pct(r['ci_hi'])})"] for r in rows]
    return table(["Assay", "Support profile (supporting/callable)", "Tied loci", "Correct",
                  "Concordance, % (95% CI)"], body,
                 ["---", "---:", "---:", "---:", "---:"])


def truth_flow_table(rows: list[dict[str, str]]) -> str:
    body = [[label(r["modality"]), r["truth_state"], r["loci"], r["requested_loci"]]
            for r in rows]
    return table(["Assay", "Source-truth state", "Loci", "Requested loci"], body,
                 ["---", "---", "---:", "---:"])


def exclusion_table(rows: list[dict[str, str]]) -> str:
    grouped: dict[tuple[str, str, str], dict[str, int]] = defaultdict(
        lambda: {"resolved": 0, "ambiguous": 0, "invalid": 0, "absent": 0}
    )
    for row in rows:
        grouped[(row["modality"], row["gene"], row["population"])][
            row["truth_state"]
        ] += int(row["loci"])
    body = []
    for (modality, gene, population), counts in sorted(grouped.items()):
        total = sum(counts.values())
        body.append([
            label(modality), f"HLA-{gene}", population, counts["resolved"],
            counts["ambiguous"], counts["invalid"], counts["absent"], total,
            f"{100 * counts['resolved'] / total:.1f}" if total else "undefined",
        ])
    return table(
        ["Assay", "Gene", "Source population", "Resolved", "Ambiguous", "Invalid",
         "Absent", "Total", "Exact retention, %"],
        body,
        ["---", "---", "---", "---:", "---:", "---:", "---:", "---:", "---:"],
    )


def compatibility_table(two_field: list[dict[str, str]],
                        g_group: list[dict[str, str]],
                        p_group: list[dict[str, str]]) -> str:
    rows = []
    for endpoint, source in (("Allowed two-field candidate", two_field),
                             ("G-compatible under a two-field mapping", g_group),
                             ("P-group-compatible under a two-field mapping", p_group)):
        for r in sorted(source, key=lambda x: (x["modality"], label(x["method"]))):
            rows.append([
                label(r["modality"]), label(r["method"]), endpoint,
                f"{r['compatible']}/{r['loci']}",
                f"{pct(r['compatibility_concordance'])} "
                f"({pct(r['ci_lo'])}–{pct(r['ci_hi'])})",
            ])
    return table(["Assay", "Method", "Compatibility endpoint", "Compatible",
                  "Concordance, % (95% CI)"], rows,
                 ["---", "---", "---", "---:", "---:"])



def ambiguity_paired_table(rows: list[dict[str, str]]) -> str:
    order = {"wes": 0, "rnaseq": 1}
    body = []
    for row in sorted(
        rows,
        key=lambda item: (
            order[item["modality"]],
            item["inference_family"] != "descriptive_comparator",
            label(item["comparator"]),
        ),
    ):
        body.append([
            label(row["modality"]),
            label(row["comparator"]),
            row["inference_family"].replace("_", " "),
            f"{row['consensus_compatible']}/{row['loci']}",
            f"{row['comparator_compatible']}/{row['loci']}",
            number(row["delta_points"]),
            f"{row['wins']}/{row['losses']}",
            pvalue(row["signflip_p_value"]),
            pvalue(row["signflip_holm_adjusted_p"]),
            row["signflip_method"].replace("_", " "),
        ])
    return table(
        [
            "Assay", "Comparator", "Family", "ChampHLA compatible",
            "Comparator compatible", "Difference, points", "Wins/losses",
            "Raw sign-flip p", "Holm p", "Test",
        ],
        body,
        ["---", "---", "---", "---:", "---:", "---:", "---:", "---:", "---:", "---"],
    )




def protocol_change_table(rows: list[dict[str, str]]) -> str:
    body = [
        [
            row["date"], row["change"], row["direction_and_size"],
            row["verdict_effect"], row["truth_exposure"], row["decision_record"],
        ]
        for row in rows
    ]
    return table(
        [
            "Date", "Change", "Direction and size", "Effect on verdict",
            "Truth exposure at decision", "Decision record",
        ],
        body,
        ["---", "---", "---", "---", "---", "---"],
    )




def representability_table(rows: list[dict[str, str]]) -> str:
    order = {"wes": 0, "rnaseq": 1}
    body = [
        [
            label(row["modality"]),
            label(row["caller"]),
            row["caller_database_release"],
            row["catalog_alleles"],
            f"{row['representable_loci']}/{row['loci']}",
            f"{row['representable_allele_copies']}/{row['truth_allele_copies']}",
        ]
        for row in sorted(rows, key=lambda item: (order[item["modality"]], item["caller"]))
    ]
    return table(
        [
            "Assay", "Caller", "Verified native-list release", "Catalog alleles",
            "Exact-truth genotypes represented", "Truth allele copies represented",
        ],
        body,
        ["---", "---", "---", "---:", "---:", "---:"],
    )



def correlation_table(rows: list[dict[str, str]]) -> str:
    body = [[label(r["modality"]), label(r["caller1"]), label(r["caller2"]),
             r["loci"],
             f"{r['both_correct']}/{r['caller2_only_wrong']}/{r['caller1_only_wrong']}/"
             f"{r['both_wrong']}",
             f"{number(r['error_phi'])} ({number(r['error_phi_ci_lo'])} to "
             f"{number(r['error_phi_ci_hi'])})",
             r["mutually_callable_loci"],
             number(r["mutually_callable_error_phi"])] for r in rows]
    return table(["Assay", "Caller 1", "Caller 2", "Fixed-denominator loci",
                  "Both right / only 2 wrong / only 1 wrong / both wrong",
                  "Error φ (95% CI)", "Mutually callable loci", "Mutually callable error φ"],
                 body, ["---", "---", "---", "---:", "---:", "---:", "---:", "---:"])


def truth_selection_table(rows: list[dict[str, str]]) -> str:
    """Retained (exact) against excluded (ambiguous) loci, one row per method.

    Every method is shown: the fitted policies were built on retained loci, so the
    excluded loci are the nearest thing to unseen data they have.
    """
    cells = {(r["modality"], r["method"], r["stratum"]): r for r in rows}
    order = {"wes": 0, "rnaseq": 1}
    methods = sorted({(r["modality"], r["method"]) for r in rows},
                     key=lambda key: (order[key[0]], key[1] != "SimplePluralityLex",
                                      key[1].startswith("Caller:"), label(key[1])))
    body = []
    for modality, method in methods:
        row = [label(modality), label(method)]
        for stratum in ("resolved", "ambiguous"):
            cell = cells[(modality, method, stratum)]
            row.append(f"{cell['compatible']}/{cell['loci']} ({pct(cell['compatibility_concordance'])})")
        body.append(row)
    return table(["Assay", "Method", "Retained exact loci, correct (%)",
                  "Excluded ambiguous loci, compatible (%)"], body,
                 ["---", "---", "---:", "---:"])


def truth_selection_profile_table(rows: list[dict[str, str]]) -> str:
    order = {"wes": 0, "rnaseq": 1}
    body = [[label(r["modality"]),
             "retained (resolved)" if r["stratum"] == "resolved" else "excluded (ambiguous)",
             r["loci"], r["subjects"],
             f"{r['ceu_ceph_or_yri_loci']} ({pct(r['ceu_ceph_or_yri_share'])})",
             f"{r['caller_unanimous_loci']} ({pct(r['caller_unanimous_share'])})",
             number(r["median_candidate_pairs"], 1)]
            for r in sorted(rows, key=lambda r: (order[r["modality"]], r["stratum"] != "resolved"))]
    return table(["Assay", "Reference loci", "Loci", "Subjects", "CEU or YRI loci (%)",
                  "Caller-unanimous loci (%)", "Median candidate pairs"], body,
                 ["---", "---", "---:", "---:", "---:", "---:", "---:"])


def _holm(p_values: list[float]) -> list[float]:
    """Holm step-down adjustment (same rule as statistics.holm_adjust)."""
    order = sorted(range(len(p_values)), key=lambda i: p_values[i])
    adjusted = [1.0] * len(p_values)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, min(1.0, (len(p_values) - rank) * p_values[index]))
        adjusted[index] = running
    return adjusted


FAMILY_DEFINITIONS = (
    ("assay and family (primary)", lambda r: (r["modality"], r["inference_family"])),
    ("assay", lambda r: (r["modality"],)),
    ("both assays pooled", lambda r: ()),
)


def family_sensitivity_table(rows: list[dict[str, str]]) -> str:
    """Sign-flip verdicts of every active comparison under alternative families (PSR-009)."""
    active = [r for r in rows if r["multiplicity_included"] == "1"]
    adjusted: dict[str, dict[int, float]] = {}
    for name, key in FAMILY_DEFINITIONS:
        groups: dict[tuple, list[int]] = defaultdict(list)
        for index, row in enumerate(active):
            groups[key(row)].append(index)
        adjusted[name] = {}
        for members in groups.values():
            for index, value in zip(members, _holm(
                    [float(active[i]["signflip_p_value"]) for i in members])):
                adjusted[name][index] = value
    order = {"wes": 0, "rnaseq": 1}
    body = []
    for index in sorted(range(len(active)), key=lambda i: (
            order[active[i]["modality"]], active[i]["inference_family"],
            label(active[i]["comparator"]))):
        row = active[index]
        raw = float(row["signflip_p_value"])
        verdicts = ["unadjusted"] if raw < 0.05 else []
        verdicts += [name for name, _ in FAMILY_DEFINITIONS if adjusted[name][index] < 0.05]
        body.append([label(row["modality"]), label(row["comparator"]),
                     row["inference_family"].replace("_", " "), pvalue(row["signflip_p_value"])]
                    + [pvalue(str(adjusted[name][index])) for name, _ in FAMILY_DEFINITIONS]
                    + ["; ".join(verdicts) or "none"])
    return table(["Assay", "Comparator", "Family", "Raw sign-flip p",
                  "Holm: assay and family (primary)", "Holm: assay",
                  "Holm: both assays pooled", "p<0.05 under"], body,
                 ["---", "---", "---", "---:", "---:", "---:", "---:", "---"])


def adjudication_table(classes: list[dict[str, str]], flagged: list[dict[str, str]]) -> str:
    """Consensus error loci, the signed adjudication and the post hoc flagged typing."""
    posthoc = {(r["modality"], r["subject"], r["gene"]): r["flagged_second_typing"]
               for r in flagged}
    order = {"wes": 0, "rnaseq": 1}
    body = [[label(r["modality"]), r["subject"], f"HLA-{r['gene']}", r["reference"],
             r["consensus"], r["adjudication"].replace("second typing ", ""),
             posthoc.get((r["modality"], r["subject"], r["gene"]), "") or "none",
             "yes" if r["g_compatible_under_two_field_mapping"] == "1" else "no",
             "yes" if r["p_group_equivalent_to_reference"] == "1" else "no"]
            for r in sorted(classes, key=lambda r: (order[r["modality"]], r["subject"], r["gene"]))]
    return table(["Assay", "Subject", "Gene", "Reference", "ChampHLA-Consensus",
                  "Signed adjudication", "Second typing's corrected value (asterisked in the source)",
                  "G-compatible under a two-field mapping",
                  "P-compatible under a two-field mapping"], body,
                 ["---", "---", "---", "---", "---", "---", "---", "---", "---"])


def reference_agreement_table(rows: list[dict[str, str]]) -> str:
    order = {"wes": 0, "rnaseq": 1}
    body = [[label(r["modality"]), label(r["method"]),
             f"{r['all_correct']}/{r['all_loci']}",
             f"{r['agreement_correct']}/{r['agreement_loci']}"]
            for r in sorted(rows, key=lambda r: (order.get(r["modality"], 9),
                                                 r["method"] != "SimplePluralityLex",
                                                 r["method"].startswith("Caller:"),
                                                 label(r["method"])))
            if r["agreement_loci"] != "0"]
    return table(["Assay", "Method", "All exact loci, correct",
                  "Loci where both typings agree, correct"], body,
                 ["---", "---", "---:", "---:"])


def reference_agreement_phi_table(agreement: list[dict[str, str]],
                                  full: list[dict[str, str]]) -> str:
    """Caller-error phi on the loci where both typings agree, beside all exact loci."""
    overall = {(r["modality"], r["caller1"], r["caller2"]): r for r in full}
    order = {"wes": 0, "rnaseq": 1}
    body = []
    for r in sorted(agreement, key=lambda r: order.get(r["modality"], 9)):
        if r["loci"] == "0":
            continue
        whole = overall[(r["modality"], r["caller1"], r["caller2"])]
        body.append([label(r["modality"]), label(r["caller1"]), label(r["caller2"]),
                     f"{number(whole['error_phi'])} ({whole['both_wrong']}/{whole['loci']})",
                     r["loci"],
                     f"{r['both_correct']}/{r['caller2_only_wrong']}/"
                     f"{r['caller1_only_wrong']}/{r['both_wrong']}",
                     number(r["error_phi"])])
    return table(["Assay", "Caller 1", "Caller 2",
                  "All exact loci: error φ (both wrong/loci)", "Loci where both typings agree",
                  "Both right / only 2 wrong / only 1 wrong / both wrong",
                  "Error φ where both typings agree"], body,
                 ["---", "---", "---", "---:", "---:", "---:", "---:"])


def reference_agreement_correction_table(rows: list[dict[str, str]]) -> str:
    """How many of each caller's errors the vote corrects where both typings agree."""
    order = {"wes": 0, "rnaseq": 1}
    body = [[label(r["modality"]), label(r["caller"]), r["loci"], r["caller_errors"],
             r["vote_correct_at_caller_errors"], r["vote_errors"],
             r["caller_correct_at_vote_errors"]]
            for r in sorted(rows, key=lambda r: order.get(r["modality"], 9))
            if r["loci"] != "0"]
    return table(["Assay", "Caller", "Loci where both typings agree", "Caller errors",
                  "Of these, vote correct", "Vote errors", "Of these, caller correct"], body,
                 ["---", "---", "---:", "---:", "---:", "---:", "---:"])


def detectability_table(rows: list[dict[str, str]]) -> str:
    body = [[label(r["modality"]), label(r["comparator"]),
             r["inference_family"].replace("_", " "), r["family_size"],
             r["discordant_subjects"], pvalue(r["min_attainable_p"]),
             "yes" if r["significance_reachable_holm_worst_case"] == "1" else "no",
             f"{r['all_win_subjects_needed_holm_worst_case']} "
             f"({number(r['smallest_detectable_points_no_losses'])})"]
            for r in rows]
    return table(["Assay", "Comparator", "Sign-flip family", "m",
                  "Nonzero subject aggregates", "Minimum attainable raw p",
                  "Holm significance reachable in worst rank",
                  "All-win subjects needed (points)"], body,
                 ["---", "---", "---", "---:", "---:", "---:", "---", "---:"])


def power_table(rows: list[dict[str, str]]) -> str:
    sizes = sorted({int(r["cohort_subjects"]) for r in rows})
    grid: dict[tuple[str, str, str], dict[int, str]] = {}
    for r in rows:
        key = (r["modality"], r["inference_family"], r["comparator"])
        grid.setdefault(key, {})[int(r["cohort_subjects"])] = r["power"]
    order = {"wes": 0, "rnaseq": 1}
    body = []
    for (modality, family, comparator), powers in sorted(
            grid.items(), key=lambda item: (order[item[0][0]], item[0][1], item[0][2])):
        body.append([label(modality), label(comparator), family.replace("_", " ")]
                    + [powers[size] or "identical" for size in sizes])
    return table(["Assay", "Comparator", "Family"]
                 + [f"{size} subjects" for size in sizes], body,
                 ["---", "---", "---"] + ["---:"] * len(sizes))


def _clock(seconds: str) -> str:
    value = float(seconds)
    if value < 60:
        return f"{value:.3f}".rstrip("0").rstrip(".") + " s"
    minutes, remainder = divmod(round(value), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours} h {minutes} min {remainder} s" if hours else f"{minutes} min {remainder} s"


def _gb(value: str) -> str:
    return f"{int(value) / 1_000_000_000:.2f}"


def compute_smoke_table(rows: list[dict[str, str]]) -> str:
    callers = [row for row in rows if row["workflow_role"] == "caller"]
    route_labels = {
        "dna_short_read_caller_route": "DNA route (WGS-derived HLA BAM)",
        "rna_seq_caller_route": "RNA-seq route (paired FASTQ)",
    }
    body = []
    for row in callers:
        artifact = row["execution_artifact"]
        if row["execution_mode"] != "native_local_install" and artifact.endswith(".sif"):
            artifact = artifact[:-4]
        version = row["caller_version"]
        if row["caller_version_status"] == "unresolved_usage_output":
            version = "unresolved (usage output)"
        elif row["caller_version_status"] == "empty_version_output":
            version = "unresolved (empty output)"
        revision = row["workflow_commit"][:7] + (" (modified)" if row["workflow_dirty"] == "true" else "")
        body.append([
            route_labels[row["assay_route"]], row["tool"],
            version or "unresolved", artifact,
            row["container_sha256"][:12] or "native install", revision, row["native_job_id"],
            _clock(row["trace_realtime_seconds"]), _gb(row["trace_peak_rss_bytes"]),
            _clock(row["slurm_elapsed_seconds"]), _clock(row["slurm_total_cpu_seconds"]),
            _gb(row["slurm_max_rss_bytes"]),
        ])
    return table(
        ["Route and actual input", "Caller", "Version output", "Execution artifact",
         "SIF SHA-256 (first 12)", "Workflow revision",
         "Slurm job", "Nextflow realtime", "Nextflow peak RSS, GB",
         "Slurm elapsed", "Slurm TotalCPU", "Slurm MaxRSS, GB"], body,
        ["---", "---", "---", "---", "---", "---", "---:", "---:", "---:", "---:", "---:",
         "---:"],
    )


def headroom_table(rows: list[dict[str, str]]) -> str:
    order = {"wes": 0, "rnaseq": 1}
    body = [[label(row["modality"]), row["loci"], row["consensus_correct"],
             row["oracle_correct"], row["consensus_errors"],
             row["recoverable_by_any_caller"], row["unreachable_by_any_caller"]]
            for row in sorted(rows, key=lambda r: order[r["modality"]])]
    return table(["Assay", "Loci", "Consensus correct", "Oracle correct", "Consensus errors",
                  "Recoverable", "No caller correct"], body,
                 ["---", "---:", "---:", "---:", "---:", "---:", "---:"])


S12_CLASSES = {
    "no_evidence": "No callable caller", "single_caller": "Single callable caller",
    "unanimous": "Unanimous", "one_allele_conflict": "One-allele conflict",
    "two_allele_conflict": "Two-allele conflict",
}
S12_STRATA = {
    "all": "All shared loci", "assays_agree": "WES and RNA-seq calls agree",
    "assays_disagree": "WES and RNA-seq calls disagree",
    "gene_A": "HLA-A", "gene_B": "HLA-B", "gene_C": "HLA-C",
}


def s12_disagreement_table(rows: list[dict[str, str]]) -> str:
    body = []
    for row in rows:
        empty = row["loci"] == "0"
        body.append([
            label(row["assay"]), S12_CLASSES[row["category"]], row["loci"],
            "—" if empty else row["consensus_correct"],
            "—" if empty else (f"{row['consensus_concordance_percent']} "
                               f"({row['ci_low_percent']}–{row['ci_high_percent']})"),
        ])
    return table(["Assay", "Class", "Loci", "Consensus correct", "Concordance, % (95% CI)"],
                 body, ["---", "---", "---:", "---:", "---"])


def s12_cross_assay_table(rows: list[dict[str, str]]) -> str:
    body = [[S12_STRATA[row["stratum"]], row["loci"], row["wes_consensus_correct"],
             row["rnaseq_consensus_correct"], row["pooled_vote_correct"]] for row in rows]
    return table(["Stratum", "Loci", "WES consensus correct", "RNA-seq consensus correct",
                  "Pooled vote correct"], body, ["---", "---:", "---:", "---:", "---:"])


def s12_per_gene_table(rows: list[dict[str, str]]) -> str:
    cells: dict[tuple[str, str], dict[str, str]] = defaultdict(dict)
    order: list[tuple[str, str]] = []
    for row in rows:
        key = (row["assay"], row["method"])
        if key not in cells:
            order.append(key)
        cells[key][row["gene"]] = f"{row['correct']}/{row['loci']} ({row['concordance_percent']})"
    body = [[label(assay), label(method), *(cells[(assay, method)][g] for g in ("A", "B", "C", "all"))]
            for assay, method in order]
    return table(["Assay", "Method", "HLA-A", "HLA-B", "HLA-C", "All"], body,
                 ["---", "---", "---:", "---:", "---:", "---:"])


def s12_calibration_table(rows: list[dict[str, str]]) -> str:
    body = []
    for row in rows:
        empty = row["scored_loci"] == "0"
        values = ["—"] * 4 if empty else [row["mean_probability"], row["observed_concordance"],
                                          row["brier"], row["ece"]]
        body.append([
            label(row["assay"]), label(row["caller"]),
            f"{row['scored_loci']}/{row['callable_loci']}", *values,
        ])
    return table(["Assay", "Caller", "Scored/callable loci", "Mean probability", "Observed concordance",
                  "Brier score", "ECE"], body, ["---", "---", "---:", "---:", "---:", "---:", "---:"])


def main() -> int:
    corrected = ART / "development_corrected"
    characterised = ART / "development_characterisation"
    performance = read(corrected / "method_performance.tsv")
    comparisons = read(corrected / "secondary_method_results.tsv")
    reference_sensitivity = characterised / "reference_agreement_sensitivity.tsv"
    replace_block(MANUSCRIPT, "MAIN TABLE", main_table(
        performance, read(reference_sensitivity) if reference_sensitivity.is_file() else None
    ))
    replace_block(SUPPLEMENT, "COHORT TABLE", cohort_table(read(characterised / "cohort_summary.tsv")))
    replace_block(SUPPLEMENT, "PERFORMANCE TABLE", performance_table(performance))
    abstain_performance = read(
        ART / "development_sensitivity_abstain" / "method_performance.tsv"
    )
    input_manifest = ROOT / "data/development/input_manifest.json"
    rerun_inputs = (input_manifest.is_file() and
                    json.loads(input_manifest.read_text(encoding="utf-8")).get(
                        "schema_version") == "champhla-development-rerun-inputs-1")
    singleton_table = (singleton_sensitivity_table(performance, abstain_performance)
                       if rerun_inputs else performance_table(abstain_performance))
    replace_block(SUPPLEMENT, "SINGLETON SENSITIVITY TABLE", singleton_table)
    replace_block(SUPPLEMENT, "COMPARISON TABLE", comparison_table(comparisons))
    replace_block(SUPPLEMENT, "STRATIFIED TABLE", stratified_table(read(characterised / "stratified_primary_results.tsv")))
    replace_block(SUPPLEMENT, "MISSINGNESS TABLE", missingness_table(
        read(characterised / "caller_missingness.tsv")))
    replace_block(SUPPLEMENT, "MUTUALLY AVAILABLE TABLE", mutually_available_table(
        read(characterised / "caller_mutually_available_comparison.tsv")))
    replace_block(SUPPLEMENT, "SUPPORT TABLE", support_table(
        read(characterised / "support_stratified_concordance.tsv")))
    replace_block(SUPPLEMENT, "TRUTH FLOW TABLE", truth_flow_table(read(characterised / "truth_flow.tsv")))
    replace_block(SUPPLEMENT, "EXCLUSION TABLE", exclusion_table(
        read(characterised / "truth_exclusion_by_gene_population.tsv")))
    replace_block(SUPPLEMENT, "COMPATIBILITY TABLE", compatibility_table(
        read(characterised / "ambiguity_compatibility.tsv"),
        read(characterised / "g_group_compatibility.tsv"),
        read(characterised / "p_group_compatibility.tsv")))
    replace_block(SUPPLEMENT, "AMBIGUITY PAIRED TABLE", ambiguity_paired_table(
        read(characterised / "ambiguity_paired_results.tsv")))
    replace_block(SUPPLEMENT, "REPRESENTABILITY TABLE", representability_table(
        read(characterised / "caller_truth_representability_summary.tsv")))
    replace_block(SUPPLEMENT, "CORRELATION TABLE", correlation_table(
        read(characterised / "caller_error_correlation.tsv")))
    replace_block(SUPPLEMENT, "FAMILY SENSITIVITY TABLE", family_sensitivity_table(
        read(ART / "development_corrected" / "secondary_method_results.tsv")))
    replace_block(SUPPLEMENT, "DETECTABILITY TABLE", detectability_table(
        read(ART / "development_limits" / "detectability.tsv")))
    replace_block(SUPPLEMENT, "TRUTH SELECTION TABLE", truth_selection_table(
        read(ART / "development_characterisation" / "truth_selection_compatibility.tsv")))
    replace_block(SUPPLEMENT, "TRUTH SELECTION PROFILE TABLE", truth_selection_profile_table(
        read(ART / "development_characterisation" / "truth_selection_profile.tsv")))
    replace_block(SUPPLEMENT, "POWER TABLE", power_table(
        read(ART / "development_limits" / "power_curve.tsv")))
    character = ART / "development_characterisation"
    if (character / "reference_adjudication.tsv").is_file():
        replace_block(SUPPLEMENT, "ADJUDICATION TABLE", adjudication_table(
            read(character / "reference_adjudication.tsv"),
            read(character / "reference_adjudication_flagged_loci_posthoc.tsv")))
        replace_block(SUPPLEMENT, "REFERENCE AGREEMENT TABLE", reference_agreement_table(
            read(character / "reference_agreement_sensitivity.tsv")))
        replace_block(SUPPLEMENT, "REFERENCE AGREEMENT PHI TABLE", reference_agreement_phi_table(
            read(character / "reference_agreement_error_phi.tsv"),
            read(character / "caller_error_correlation.tsv")))
        replace_block(SUPPLEMENT, "REFERENCE AGREEMENT CORRECTION TABLE",
                      reference_agreement_correction_table(
                          read(character / "reference_agreement_vote_correction.tsv")))
    replace_block(SUPPLEMENT, "HEADROOM TABLE", headroom_table(
        read(ART / "development_limits" / "headroom.tsv")))
    replace_block(SUPPLEMENT, "PROTOCOL CHANGE TABLE", protocol_change_table(
        read(ART / "protocol_change_ledger.tsv")))
    replace_block(SUPPLEMENT, "COMPUTE SMOKE TABLE", compute_smoke_table(
        read(ART / "compute_smoke_benchmark.tsv")))
    rerun_collection = ROOT / "provenance/development_rerun_v350/truth_free_collection"
    rerun_tasks = rerun_collection / "caller_run_state.tsv"
    rerun_cells = rerun_collection / "stored_vs_rerun_cells.tsv"
    if rerun_tasks.is_file() != rerun_cells.is_file():
        raise SystemExit("incomplete v3.5.0 rerun provenance table pair")
    if rerun_tasks.is_file():
        replace_block(SUPPLEMENT, "RERUN TASK STATE TABLE", rerun_state_table(
            read(rerun_tasks)))
        replace_block(SUPPLEMENT, "RERUN CELL COMPARISON TABLE", rerun_cell_comparison_table(
            read(rerun_cells)))
        replace_block(SUPPLEMENT, "RERUN CELL CHANGE CHARACTER TABLE",
                      rerun_cell_change_character_table(
                          read(rerun_cells), read(rerun_collection / "t1k_parser_provenance.tsv")))
    restored = ART / "restored_analyses"
    replace_block(SUPPLEMENT, "S12 DISAGREEMENT TABLE", s12_disagreement_table(
        read(restored / "discordance_taxonomy.tsv")))
    replace_block(SUPPLEMENT, "S12 CROSS-ASSAY TABLE", s12_cross_assay_table(
        read(restored / "cross_assay_agreement.tsv")))
    replace_block(SUPPLEMENT, "S12 PER-GENE TABLE", s12_per_gene_table(
        read(restored / "per_gene_caller_concordance.tsv")))
    replace_block(SUPPLEMENT, "S12 CALIBRATION TABLE", s12_calibration_table(
        read(restored / "caller_calibration.tsv")))
    print("regenerated manuscript and supplementary tables")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
