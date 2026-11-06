"""POST HOC: the vote and each panel caller in the archived outputs and the study runs.

decisions/20261106_posthoc_round4_amendment.json, C1 (JP-014, option C). Both caller
tables are scored the same way, with the frozen plurality rule (``build_consensus``) and
each table's recorded call states, at the current exact-endpoint loci (153 WES, 118
RNA-seq). The study-run scores must reproduce ``per_locus_results.tsv`` before the
archived scores are written.

Writes ``run_stability_posthoc.tsv`` (one row per assay and method) and
``run_stability_summary_posthoc.tsv`` (one row per assay) in
``artifacts/development_characterisation``.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.consensus import build_consensus  # noqa: E402
from champhla_confirmation.io import canonical_pair, is_callable, write_tsv  # noqa: E402
from champhla_confirmation.panels import METHOD_PLURALITY, PANELS  # noqa: E402

PER_LOCUS = ROOT / "artifacts" / "development_corrected" / "per_locus_results.tsv"
STUDY = ROOT / "data" / "development" / "normalized_caller_calls.tsv"
ARCHIVED = (ROOT / "provenance" / "development_rerun_v350" / "historical_inputs_pre_v350"
            / "normalized_caller_calls.tsv")
OUT = ROOT / "artifacts" / "development_characterisation"
VOTE = "ChampHLA-Consensus"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def locus(row: dict[str, str]) -> tuple[str, str, str]:
    return row["subject"], row["modality"], row["gene"]


def run_calls(rows: list[dict[str, str]], loci: set) -> dict[tuple, tuple | None]:
    """Each method's call at each exact locus; a non-callable row or no row is None."""
    rows = [row for row in rows if locus(row) in loci]
    calls: dict[tuple, tuple | None] = {}
    for row in build_consensus(rows):
        if row["method"] == METHOD_PLURALITY:
            calls[(VOTE, locus(row))] = (canonical_pair(row["allele1"], row["allele2"], row["gene"])
                                         if row["call_status"] == "callable" else None)
    for row in rows:
        if row["caller"] in PANELS[row["modality"]]:
            calls[(row["caller"], locus(row))] = (
                canonical_pair(row["allele1"], row["allele2"], row["gene"])
                if is_callable(row) else None)
    return calls


def score(truth: dict, archived: dict, study: dict) -> tuple[list[dict], list[dict]]:
    rows, summary = [], []
    for modality in sorted({key[1] for key in truth}):
        loci = sorted(key for key in truth if key[1] == modality)
        methods = (VOTE, *sorted(PANELS[modality]))
        per = {}
        for method in methods:
            a = sum(archived.get((method, key)) == truth[key] for key in loci)
            s = sum(study.get((method, key)) == truth[key] for key in loci)
            per[method] = (a, s)
            rows.append({"modality": modality, "method": method, "loci": len(loci),
                         "archived_correct": a, "study_run_correct": s, "change": s - a})
        callers = [m for m in methods if m != VOTE]
        moved = max(callers, key=lambda m: (abs(per[m][1] - per[m][0]), m))
        lead_a = max(callers, key=lambda m: (per[m][0], m))
        lead_s = max(callers, key=lambda m: (per[m][1], m))
        summary.append({
            "modality": modality, "loci": len(loci),
            "vote_archived_correct": per[VOTE][0], "vote_study_run_correct": per[VOTE][1],
            "vote_calls_changed": sum(archived.get((VOTE, k)) != study.get((VOTE, k))
                                      for k in loci),
            "largest_caller_change": abs(per[moved][1] - per[moved][0]),
            "largest_change_caller": moved,
            "leading_caller_archived": lead_a, "leading_caller_archived_correct": per[lead_a][0],
            "leading_caller_study_run": lead_s, "leading_caller_study_run_correct": per[lead_s][1],
        })
    return rows, summary


def main() -> int:
    truth, recorded = {}, {}
    for row in read(PER_LOCUS):
        if row["modality"] not in PANELS:
            continue
        key = locus(row)
        truth[key] = canonical_pair(row["truth_allele1"], row["truth_allele2"], row["gene"])
        method = VOTE if row["method"] == METHOD_PLURALITY else row["method"].removeprefix("Caller:")
        recorded[(method, key)] = row["correct"] == "1"
    study = run_calls(read(STUDY), set(truth))
    for (method, key), correct in recorded.items():
        if (method == VOTE or method in PANELS[key[1]]) and \
                (study.get((method, key)) == truth[key]) != correct:
            raise SystemExit(f"study-run score does not reproduce per_locus_results: {method} {key}")
    archived = run_calls(read(ARCHIVED), set(truth))
    rows, summary = score(truth, archived, study)
    write_tsv(str(OUT / "run_stability_posthoc.tsv"), rows, list(rows[0]))
    write_tsv(str(OUT / "run_stability_summary_posthoc.tsv"), summary, list(summary[0]))
    for row in summary:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
