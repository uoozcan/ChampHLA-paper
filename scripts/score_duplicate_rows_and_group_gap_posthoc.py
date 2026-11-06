"""POST HOC: set-valued scoring under intersected duplicate rows, and the G-over-P gap.

decisions/20261106_posthoc_round3_amendment.json, B4.

(a) The set-valued endpoint takes the union of candidate pairs across a subject's
duplicate rows in the 2014 table. Here each locus's candidates are instead the
intersection over its rows; a row that does not parse contributes nothing, as in the
union, and a locus whose intersection is empty is excluded. Every method is scored on
the set-valued loci and on the loci excluded from the exact endpoint, beside its union
score.

(b) For T1K and arcasHLA, counts the loci that are compatible under the two-field G
mapping but not under the P mapping, and how many of those carry a null (N) suffix in
the caller's normalized output.

Writes ``set_valued_intersection_posthoc.tsv`` and ``g_over_p_gap_posthoc.tsv`` in
``artifacts/development_characterisation``.
"""
from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.consensus import canonical_pair, is_callable  # noqa: E402
from champhla_confirmation.hla_reference import HLAReference, _two_field  # noqa: E402
from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_recovery.truth import GENES, _read_2014, candidate_genotype_pairs  # noqa: E402

RUNTIME = ROOT / "runtime_data"
PREDICTIONS = RUNTIME / "development_predictions.tsv"
CANDIDATES = RUNTIME / "development_candidate_truth.tsv"
SOURCE = RUNTIME / "public_truth" / "20140702_hla_diversity.txt"
CALLS = ROOT / "data" / "development" / "normalized_caller_calls.tsv"
IPD = ROOT / "resources" / "ipd_imgt_hla" / "3.65.0"
OUT = ROOT / "artifacts" / "development_characterisation"
GAP_CALLERS = ("T1K", "ArcasHLA")


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def intersect_rows(row_candidates: list[set | None]) -> set:
    """Intersection over the rows that parsed; None marks a row that did not."""
    parsed = [candidates for candidates in row_candidates if candidates is not None]
    return set.intersection(*parsed) if parsed else set()


def intersection_truth(source: Path) -> dict[tuple[str, str], set]:
    rows = defaultdict(list)
    for row in _read_2014(str(source)):
        subject = row.get("id", "").strip().upper()
        if subject:
            rows[subject].append(row)
    truth = {}
    for subject, records in rows.items():
        for gene in GENES:
            per_row = []
            for row in records:
                try:
                    per_row.append(candidate_genotype_pairs(row[gene], row[f"{gene}.1"], gene))
                except (KeyError, ValueError):
                    per_row.append(None)
            truth[(subject, gene)] = intersect_rows(per_row)
    return truth


def score(pred: dict, loci: list, candidates: dict) -> tuple[int, int]:
    """(loci scored, compatible) for one method; a missing or non-callable call scores 0."""
    scored = compatible = 0
    for locus in loci:
        allowed = candidates.get(locus)
        if not allowed:
            continue
        scored += 1
        row = pred.get(locus)
        if row and is_callable(row):
            compatible += canonical_pair(row["allele1"], row["allele2"], locus[2]) in allowed
    return scored, compatible


def main() -> int:
    predictions = read(PREDICTIONS)
    union, status = {}, {}
    for row in read(CANDIDATES):
        key = (row["subject"], row["modality"], row["gene"])
        pairs = {tuple(pair) for pair in json.loads(row["truth_candidate_pairs_json"])}
        if pairs:
            union[key], status[key] = pairs, row["truth_status"]
    by_row = intersection_truth(SOURCE)
    intersected = {key: by_row.get((key[0], key[2]), set()) for key in union}
    by_method = defaultdict(dict)
    for row in predictions:
        by_method[row["method"]][(row["subject"], row["modality"], row["gene"])] = row
    out = []
    for modality in sorted({key[1] for key in union}):
        for method in sorted(by_method):
            pred = by_method[method]
            loci = sorted(key for key in union if key[1] == modality and key in pred)
            if not loci:
                continue
            excluded = [key for key in loci if status[key] == "ambiguous"]
            entry = {"modality": modality, "method": method}
            for scope, subset in (("set_valued", loci), ("excluded", excluded)):
                for rule, candidates in (("union", union), ("intersection", intersected)):
                    scored, compatible = score(pred, subset, candidates)
                    entry[f"{scope}_{rule}_loci"] = scored
                    entry[f"{scope}_{rule}_compatible"] = compatible
            out.append(entry)
    write_tsv(OUT / "set_valued_intersection_posthoc.tsv", out, list(out[0]))

    reference = HLAReference.from_files(
        "3.65.0", IPD / "Allelelist.txt",
        p_groups=IPD / "wmda" / "hla_nom_p.txt", g_groups=IPD / "wmda" / "hla_nom_g.txt")
    groups = {}
    for kind, source in (("P", reference.p_groups), ("G", reference.g_groups)):
        mapping = defaultdict(set)
        for group, members in source.items():
            for member in members:
                if _two_field(member):
                    mapping[_two_field(member)].add(group)
        groups[kind] = mapping

    def group_pairs(pair, kind):
        left = groups[kind].get(_two_field(pair[0]), set())
        right = groups[kind].get(_two_field(pair[1]), set())
        return {tuple(sorted(item)) for item in product(left, right)}

    suffixes = {(r["subject"], r["modality"], r["gene"], r["caller"]):
                f"{r['allele1_suffix']}{r['allele2_suffix']}" for r in read(CALLS)}
    gap = []
    for modality in sorted({key[1] for key in union}):
        for caller in GAP_CALLERS:
            pred = by_method.get(f"Caller:{caller}", {})
            g_only = with_null = 0
            for locus in sorted(key for key in union if key[1] == modality and key in pred):
                row = pred[locus]
                if not is_callable(row):
                    continue
                pair = canonical_pair(row["allele1"], row["allele2"], locus[2])
                truth = {kind: set().union(*(group_pairs(p, kind) for p in union[locus]))
                         for kind in ("G", "P")}
                if not truth["P"] or not truth["G"]:
                    continue  # the same exclusion as the group endpoints
                g_match = bool(group_pairs(pair, "G") & truth["G"])
                p_match = bool(group_pairs(pair, "P") & truth["P"])
                if g_match and not p_match:
                    g_only += 1
                    with_null += "N" in suffixes.get((*locus, caller), "")
            if pred and any(key[1] == modality for key in pred):
                gap.append({"modality": modality, "caller": caller,
                            "g_compatible_not_p_compatible": g_only,
                            "of_which_null_suffix": with_null})
    write_tsv(OUT / "g_over_p_gap_posthoc.tsv", gap, list(gap[0]))
    for row in out:
        if row["method"] in {"SimplePluralityLex", "Caller:OptiType"}:
            print(row)
    for row in gap:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
