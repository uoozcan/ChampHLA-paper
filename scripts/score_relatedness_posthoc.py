"""POST HOC: relatedness of retained subjects and family-clustered sign-flip tests.

decisions/20261106_posthoc_round3_amendment.json, B5. Reads the public IGSR pedigree
file `20130606_g1k.ped` (URL and SHA-256 below; fetch it into runtime_data/public_pedigree/).

Truth-free part: among each assay's exact-endpoint subjects, count parent-offspring,
sibling (listed, or sharing a recorded parent), second-order and third-order pairs.

Post hoc part: repeat every multiplicity-included sign-flip comparison with clusters
formed by pedigree family identifier instead of subject; a subject without one is its
own cluster. Seeds, the exact/Monte Carlo policy and the Holm families are those of the
primary analysis. Reports each comparison's verdict under both clusterings.

Writes ``relatedness_pairs_posthoc.tsv`` and ``family_clustered_signflip_posthoc.tsv`` in
``artifacts/development_characterisation``.
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import METHOD_PLURALITY  # noqa: E402
from champhla_confirmation.statistics import holm_adjust, subject_cluster_signflip  # noqa: E402

PEDIGREE = ROOT / "runtime_data" / "public_pedigree" / "20130606_g1k.ped"
PEDIGREE_URL = ("https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/working/"
                "20130606_sample_info/20130606_g1k.ped")
PEDIGREE_SHA256 = "38687335d053056d799891a37c42b1ac24a5a2a1eb5fccaf34db58188bccfff7"
PER_LOCUS = ROOT / "artifacts" / "development_corrected" / "per_locus_results.tsv"
SECONDARY = ROOT / "artifacts" / "development_corrected" / "secondary_method_results.tsv"
OUT = ROOT / "artifacts" / "development_characterisation"
RELATIONS = ("parent_offspring", "siblings", "second_order", "third_order")
ID = re.compile(r"[A-Z]{2}\d{5}")


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def load_pedigree(rows: list[dict[str, str]]) -> tuple[dict[str, str], dict[frozenset, set]]:
    """Family identifier per individual, and the relations recorded for each pair."""
    family, parents = {}, {}
    pairs: dict[frozenset, set] = defaultdict(set)
    for row in rows:
        person = row["Individual ID"].strip()
        family[person] = row["Family ID"].strip()
        parents[person] = {p for p in (row["Paternal ID"].strip(), row["Maternal ID"].strip())
                           if p and p != "0"}
        for parent in parents[person]:
            pairs[frozenset((person, parent))].add("parent_offspring")
        for column, relation in (("Siblings", "siblings"), ("Second Order", "second_order"),
                                 ("Third Order", "third_order")):
            for other in ID.findall(row.get(column, "")):
                if other != person:
                    pairs[frozenset((person, other))].add(relation)
    for first, second in combinations(sorted(parents), 2):
        if parents[first] & parents[second]:
            pairs[frozenset((first, second))].add("siblings")
    return family, pairs


def related_pairs(subjects: set[str], pairs: dict[frozenset, set]) -> dict[str, int]:
    counts = dict.fromkeys(RELATIONS, 0)
    for pair, relations in pairs.items():
        if pair <= subjects and len(pair) == 2:
            for relation in relations:
                counts[relation] += 1
    return counts


def cluster_deltas(locus_deltas: dict[tuple[str, str], int], cluster_of) -> dict[str, int]:
    """Sum locus differences over clusters; ``cluster_of`` maps a subject to its cluster."""
    totals: dict[str, int] = defaultdict(int)
    for (subject, _gene), delta in locus_deltas.items():
        totals[cluster_of(subject)] += delta
    return dict(totals)


def main() -> int:
    observed = hashlib.sha256(PEDIGREE.read_bytes()).hexdigest()
    if observed != PEDIGREE_SHA256:
        raise SystemExit(f"pedigree checksum {observed} does not match {PEDIGREE_SHA256}")
    family, pairs = load_pedigree(read(PEDIGREE))

    correct = {}
    for row in read(PER_LOCUS):
        correct[(row["modality"], row["subject"], row["gene"], row["method"])] = int(row["correct"] or 0)
    loci = {key[:3] for key in correct if key[3] == METHOD_PLURALITY}

    relatedness = []
    for modality in sorted({locus[0] for locus in loci}):
        subjects = {locus[1] for locus in loci if locus[0] == modality}
        clusters = {family.get(subject) or subject for subject in subjects}
        relatedness.append({"modality": modality, "subjects": len(subjects),
                            "subjects_in_pedigree": sum(s in family for s in subjects),
                            "family_clusters": len(clusters),
                            **related_pairs(subjects, pairs)})
    write_tsv(OUT / "relatedness_pairs_posthoc.tsv", relatedness, list(relatedness[0]))

    tests = [row for row in read(SECONDARY) if row["multiplicity_included"] == "1"]
    results = []
    for row in tests:
        modality, method = row["modality"], row["comparator"]
        deltas = {(locus[1], locus[2]):
                  correct[(*locus, METHOD_PLURALITY)] - correct.get((*locus, method), 0)
                  for locus in loci if locus[0] == modality}
        family_totals = cluster_deltas(deltas, lambda s: family.get(s) or s)
        p_value, test_method = subject_cluster_signflip(
            family_totals.values(), seed=int(row["signflip_seed"]))
        results.append({"modality": modality, "comparator": method,
                        "inference_family": row["inference_family"],
                        "subject_holm_p": row["signflip_holm_adjusted_p"],
                        "subject_significant": row["signflip_holm_significant"],
                        "family_clusters": len(family_totals),
                        "discordant_family_clusters": sum(v != 0 for v in family_totals.values()),
                        "p_value": p_value, "signflip_method": test_method})
    by_family = defaultdict(list)
    for item in results:
        by_family[(item["modality"], item["inference_family"])].append(item)
    out = []
    for members in by_family.values():
        for item in holm_adjust(members):
            out.append({**{k: v for k, v in item.items() if k not in {"holm_adjusted_p", "holm_significant"}},
                        "family_holm_p": f"{item['holm_adjusted_p']:.6g}",
                        "family_significant": item["holm_significant"],
                        "verdict_changed": int(str(item["holm_significant"]) != item["subject_significant"])})
    out.sort(key=lambda r: (r["modality"], r["inference_family"], r["comparator"]))
    write_tsv(OUT / "family_clustered_signflip_posthoc.tsv", out, list(out[0]))
    for row in relatedness:
        print(row)
    for row in out:
        print(row["modality"], row["comparator"], row["subject_holm_p"], row["family_holm_p"],
              row["subject_significant"], row["family_significant"], row["verdict_changed"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
