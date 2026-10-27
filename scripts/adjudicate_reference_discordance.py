"""Adjudicate consensus-discordant development loci against a second typing.

decisions/20261009_reference_adjudication.json. The second typing (Abi-Rached et al.
2018, IGSR) was computed in silico from the same 1000 Genomes exomes, so it only
adjudicates and supports a sensitivity analysis; it never replaces the reference.

Writes to artifacts/development_characterisation/:

* ``reference_adjudication.tsv``          -- every callable consensus call that
  disagrees with the reference, with its adjudication class and G-equivalence
* ``reference_typing_agreement.tsv``      -- agreement of the two typings, per assay and gene
* ``reference_agreement_sensitivity.tsv`` -- every method rescored on the loci where
  the two typings agree, beside its full-set score
* ``reference_agreement_headroom.tsv`` / ``reference_agreement_error_phi.tsv``
* ``reference_agreement_vote_correction.tsv`` -- on the same loci, how many of each
  caller's errors the vote corrects

    python scripts/adjudicate_reference_discordance.py [joined] [second_typing]
"""
from __future__ import annotations

import csv
import math
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from champhla_confirmation.hla_reference import HLAReference  # noqa: E402
from champhla_confirmation.io import sha256, write_tsv  # noqa: E402
from champhla_confirmation.panels import GENES, METHOD_PLURALITY, PANELS  # noqa: E402
from integration_headroom_and_power import headroom  # noqa: E402

JOINED = ROOT / "runtime_data" / "joined_development.tsv"
SECOND = ROOT / "runtime_data" / "public_truth" / "20181129_HLA_types_full_1000_Genomes_Project_panel.txt"
SECOND_SHA256 = "570b5cc5523273826a5695452f18b77f8742e568e1e35a34aed5d2a313472e8e"
OUT = ROOT / "artifacts" / "development_characterisation"
FIELD_RE = re.compile(r"^\d{2,3}(?::\d{2,3})+$")

MATCHES_CONSENSUS = "second typing matches consensus"
MATCHES_REFERENCE = "second typing matches reference"
MATCHES_NEITHER = "second typing matches neither"
UNAVAILABLE = "second typing unavailable"


def _pair(first: str, second: str) -> tuple[str, str]:
    return tuple(sorted([first.strip(), second.strip()]))


def _allele(gene: str, value: str) -> str | None:
    value = value.strip()
    if not FIELD_RE.match(value):
        return None
    return f"{gene}*{':'.join(value.split(':')[:2])}"


def load_second_typing(path: Path, subjects: set[str]) -> dict[tuple[str, str], tuple | None]:
    """(subject, gene) -> unordered two-field pair, or None when unavailable.

    Rows for subjects outside the development set are dropped before any genotype
    field is read (decision firewall: extension subjects are never compared).
    """
    observed = sha256(path)
    if observed != SECOND_SHA256:
        raise SystemExit(f"second typing checksum mismatch: {observed}")
    typing = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["Sample ID"].strip() not in subjects:
                continue
            for gene in GENES:
                first = _allele(gene, row[f"HLA-{gene} 1"])
                second = _allele(gene, row[f"HLA-{gene} 2"])
                typing[(row["Sample ID"].strip(), gene)] = (
                    _pair(first, second) if first and second else None)
    return typing


def load_flagged_typing(path: Path, subjects: set[str]) -> dict[tuple[str, str], tuple]:
    """POST HOC (decisions/20261009_reference_adjudication_posthoc.json, corrected by
    decisions/20261012_second_typing_asterisk_documented.json).

    Some values in the IGSR file carry a trailing asterisk; the signed rule above
    treats them as unavailable. The IGSR README does not describe it, but the source
    article does (S1 Table legend and footnote, S3 Fig): it marks a PolyPheMe typing
    that disagreed with the previously published typing and was kept after manual
    verification. Here the asterisk is stripped, and only loci where at least one
    allele carried it are returned.
    """
    flagged = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["Sample ID"].strip() not in subjects:
                continue
            for gene in GENES:
                raw = [row[f"HLA-{gene} 1"].strip(), row[f"HLA-{gene} 2"].strip()]
                if not any(value.endswith("*") for value in raw):
                    continue
                alleles = [_allele(gene, value.rstrip("*")) for value in raw]
                if all(alleles):
                    flagged[(row["Sample ID"].strip(), gene)] = _pair(*alleles)
    return flagged


def load_joined(path: Path) -> dict[tuple[str, str, str, str], dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {(row["subject"], row["modality"], row["gene"], row["method"]): row
                for row in csv.DictReader(handle, delimiter="\t")
                if row["modality"] in PANELS and (row.get("truth_allele1") or "").strip()}


def _called(row: dict | None) -> tuple | None:
    if not row or row["call_status"] != "callable":
        return None
    return _pair(row["allele1"], row["allele2"])


def group_compatible(
    reference: HLAReference, first: tuple, second: tuple, kind: str
) -> bool:
    """True when diploid alleles can pair bijectively through official P/G groups."""
    groups = {
        allele: reference.groups_for_two_field(allele, kind)
        for allele in (*first, *second)
    }
    return any(
        all(groups[a] & groups[b] for a, b in zip(first, order))
        for order in permutations(second)
    )


def g_equivalent(reference: HLAReference, first: tuple, second: tuple) -> bool:
    """Backward-compatible name for the lenient two-field G mapping."""
    return group_compatible(reference, first, second, "G")


def p_group_equivalent(reference: HLAReference, first: tuple, second: tuple) -> bool:
    return group_compatible(reference, first, second, "P")


def _phi(n00: int, n01: int, n10: int, n11: int) -> float:
    denominator = math.sqrt((n10 + n11) * (n00 + n01) * (n01 + n11) * (n00 + n10))
    return (n11 * n00 - n10 * n01) / denominator if denominator else 0.0


def main(argv: list[str]) -> int:
    joined_path = Path(argv[1]) if len(argv) > 1 else JOINED
    second_path = Path(argv[2]) if len(argv) > 2 else SECOND
    joined = load_joined(joined_path)
    subjects = {key[0] for key in joined}
    second = load_second_typing(second_path, subjects)
    ipd = ROOT / "resources" / "ipd_imgt_hla" / "3.65.0"
    reference = HLAReference.from_files(
        "3.65.0",
        ipd / "Allelelist.txt",
        p_groups=ipd / "wmda" / "hla_nom_p.txt",
        g_groups=ipd / "wmda" / "hla_nom_g.txt",
    )

    truth = {key[:3]: _pair(row["truth_allele1"], row["truth_allele2"])
             for key, row in joined.items()}
    loci = sorted(truth)

    adjudication = []
    for locus in loci:
        consensus = _called(joined.get((*locus, METHOD_PLURALITY)))
        if consensus is None or consensus == truth[locus]:
            continue
        other = second.get((locus[0], locus[2]))
        status = (UNAVAILABLE if other is None else MATCHES_CONSENSUS if other == consensus
                  else MATCHES_REFERENCE if other == truth[locus] else MATCHES_NEITHER)
        adjudication.append({
            "modality": locus[1], "subject": locus[0], "gene": locus[2],
            "superpopulation": joined[(*locus, METHOD_PLURALITY)]["superpopulation"],
            "reference": "+".join(truth[locus]), "consensus": "+".join(consensus),
            "second_typing": "+".join(other) if other else "",
            "adjudication": status,
            "g_compatible_under_two_field_mapping": int(
                group_compatible(reference, consensus, truth[locus], "G")
            ),
            "p_group_equivalent_to_reference": int(
                p_group_equivalent(reference, consensus, truth[locus])
            ),
        })
    write_tsv(OUT / "reference_adjudication.tsv", adjudication)

    agreement = []
    for modality in sorted(PANELS):
        for gene in (*GENES, "all"):
            subset = [l for l in loci if l[1] == modality and gene in {"all", l[2]}]
            available = [l for l in subset if second.get((l[0], l[2])) is not None]
            agreement.append({
                "modality": modality, "gene": gene, "loci": len(subset),
                "second_typing_available": len(available),
                "typings_agree": sum(second[(l[0], l[2])] == truth[l] for l in available),
            })
    write_tsv(OUT / "reference_typing_agreement.tsv", agreement)

    agreed = {l for l in loci if second.get((l[0], l[2])) == truth[l]}
    correct = {(key[3], key[:3]): _called(row) == truth[key[:3]] for key, row in joined.items()}
    sensitivity = []
    for modality in sorted(PANELS):
        full = [l for l in loci if l[1] == modality]
        subset = [l for l in full if l in agreed]
        for method in sorted({key[3] for key in joined if key[1] == modality}):
            # Fixed denominators: a method with no row at a locus scores incorrect.
            sensitivity.append({
                "modality": modality, "method": method,
                "all_loci": len(full),
                "all_correct": sum(correct.get((method, l), False) for l in full),
                "agreement_loci": len(subset),
                "agreement_correct": sum(correct.get((method, l), False) for l in subset),
            })
    write_tsv(OUT / "reference_agreement_sensitivity.tsv", sensitivity)

    by_modality = defaultdict(set)
    for locus in agreed:
        by_modality[locus[1]].add(locus)
    write_tsv(OUT / "reference_agreement_headroom.tsv", headroom(correct, by_modality))

    correlations = []
    for modality in sorted(PANELS):
        subset = sorted(by_modality[modality])
        for first, second_caller in combinations(PANELS[modality], 2):
            pairs = Counter(
                (1 - correct.get((f"Caller:{first}", l), False),
                 1 - correct.get((f"Caller:{second_caller}", l), False)) for l in subset)
            correlations.append({
                "modality": modality, "caller1": first, "caller2": second_caller,
                "loci": len(subset), "both_correct": pairs[(0, 0)],
                "caller2_only_wrong": pairs[(0, 1)], "caller1_only_wrong": pairs[(1, 0)],
                "both_wrong": pairs[(1, 1)],
                "error_phi": _phi(pairs[(0, 0)], pairs[(0, 1)], pairs[(1, 0)], pairs[(1, 1)]),
            })
    write_tsv(OUT / "reference_agreement_error_phi.tsv", correlations)

    # What the vote does with each caller's errors on the same subset: a vote can
    # only correct errors that the other callers do not share.
    corrections = []
    for modality in sorted(PANELS):
        subset = sorted(by_modality[modality])
        for caller in PANELS[modality]:
            wrong = [l for l in subset if not correct.get((f"Caller:{caller}", l), False)]
            vote_wrong = [l for l in subset if not correct.get((METHOD_PLURALITY, l), False)]
            corrections.append({
                "modality": modality, "caller": caller, "loci": len(subset),
                "caller_errors": len(wrong),
                "vote_correct_at_caller_errors": sum(
                    correct.get((METHOD_PLURALITY, l), False) for l in wrong),
                "vote_errors": len(vote_wrong),
                "caller_correct_at_vote_errors": sum(
                    correct.get((f"Caller:{caller}", l), False) for l in vote_wrong),
            })
    write_tsv(OUT / "reference_agreement_vote_correction.tsv", corrections)

    # POST HOC: asterisk-flagged values, read after the signed analysis was run.
    flagged = load_flagged_typing(second_path, subjects)
    posthoc = []
    for modality in sorted({locus[1] for locus in loci}):
        subset = [l for l in loci if l[1] == modality]
        flagged_loci = [l for l in subset if (l[0], l[2]) in flagged]
        discordant = {(r["subject"], r["gene"]) for r in adjudication if r["modality"] == modality}
        flagged_discordant = [l for l in flagged_loci if (l[0], l[2]) in discordant]
        consensus_of = {l: _called(joined.get((*l, METHOD_PLURALITY))) for l in flagged_loci}
        posthoc.append({
            "modality": modality, "exact_loci": len(subset),
            "flagged_loci": len(flagged_loci),
            "flagged_loci_consensus_discordant": len(flagged_discordant),
            "consensus_discordant_loci": len(discordant),
            "flagged_typing_equals_consensus": sum(
                flagged[(l[0], l[2])] == consensus_of[l] for l in flagged_loci),
            "flagged_typing_equals_reference": sum(
                flagged[(l[0], l[2])] == truth[l] for l in flagged_loci),
            "analysis_status": "post_hoc_after_results",
        })
    write_tsv(OUT / "reference_adjudication_flagged_posthoc.tsv", posthoc)
    flagged_rows = [{
        "modality": l[1], "subject": l[0], "gene": l[2],
        "flagged_second_typing": "+".join(flagged[(l[0], l[2])]),
        "equals_consensus": int(flagged[(l[0], l[2])] == _called(joined.get((*l, METHOD_PLURALITY)))),
        "equals_reference": int(flagged[(l[0], l[2])] == truth[l]),
        "analysis_status": "post_hoc_after_results",
    } for l in loci if (l[0], l[2]) in flagged]
    write_tsv(OUT / "reference_adjudication_flagged_loci_posthoc.tsv", flagged_rows)

    for modality in sorted(PANELS):
        rows = [r for r in adjudication if r["modality"] == modality]
        counts = Counter(r["adjudication"] for r in rows)
        print(f"{modality}: {len(rows)} discordant consensus calls; "
              + "; ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
