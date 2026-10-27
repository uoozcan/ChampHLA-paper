from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from .hla_reference import HLAReference

TRUTH_TOKENS = {
    "truth", "truth_allele1", "truth_allele2", "label", "labels",
    "is_correct", "is_correct_2field", "correct_status", "candidate_set_oracle",
    "match_grade", "compatibility_grade",
}
UNCALLABLE = {
    "", "missing", "partial", "ambiguous", "invalid", "uncallable",
    "no_call", "no_consensus", "no_evidence", "abstained", "failed",
}
PLACEHOLDER_ALLELES = frozenset({
    "", "-", ".", "na", "n/a", "none", "no", "not typed", "nottyped",
    "not_typed", "unknown",
})
# Second-allele tokens that a caller's own documented output format uses to declare a
# homozygous call (decisions/20261008_singleton_native_homozygosity.json). HLA-HD writes
# '-' in final.result.txt (failures are 'Not typed'); arcasHLA < 0.5 writes a one-element
# genotype list, which the workflow parser renders as '-'. T1K's '.' placeholder covers
# both missing and homozygous alleles, so it is deliberately absent.
NATIVE_HOMOZYGOUS_MARKERS = {
    "HLA-HD": frozenset({"-"}),
    "ARCASHLA": frozenset({"-"}),
}
SINGLETON_POLICIES = ("abstain", "native_declaration")
ALLELE_RE = re.compile(
    r"^(?:HLA-)?([A-Za-z0-9]+)\*([0-9]+):([0-9]+)"
    r"((?::[0-9]+)*)([NLSQCAPG])?$",
    re.I,
)


@dataclass(frozen=True)
class NormalizedAllele:
    """An HLA allele normalized for an explicit two-field endpoint."""

    raw: str
    gene: str
    two_field: str
    suffix: str
    higher_fields: tuple[str, ...]
    designation_type: str = "allele"
    membership_status: str = "not_checked"
    mapping_status: str = "syntax_only"
    normalization_release: str = ""


def is_placeholder_allele(value: str | None) -> bool:
    return (value or "").strip().lower() in PLACEHOLDER_ALLELES


def declares_native_homozygosity(caller: str, a: str | None, b: str | None) -> bool:
    """True when exactly one allele is reported and the other field is the caller's
    documented homozygous marker (not merely any placeholder)."""
    markers = NATIVE_HOMOZYGOUS_MARKERS.get((caller or "").strip().upper())
    if not markers:
        return False
    raw_a, raw_b = (a or "").strip(), (b or "").strip()
    if is_placeholder_allele(raw_a) == is_placeholder_allele(raw_b):
        return False
    marker = raw_b if not is_placeholder_allele(raw_a) else raw_a
    return marker in markers


def normalize_allele(value: str, gene: str | None = None,
                     reference: "HLAReference | None" = None) -> NormalizedAllele:
    raw = value.strip()
    token = raw.replace("HLA-", "")
    if not token:
        raise ValueError("allele is empty")
    if "/" in token:
        raise ValueError(f"allele is ambiguous: {value!r}")
    if "*" not in token and gene:
        token = f"{normalize_gene(gene)}*{token}"
    match = ALLELE_RE.fullmatch(token)
    if not match:
        raise ValueError(f"allele is not resolvable to two fields: {value!r}")
    allele_gene = normalize_gene(match.group(1))
    if gene and allele_gene != normalize_gene(gene):
        raise ValueError(f"allele/gene mismatch: {value!r} vs {gene!r}")
    higher = tuple(part for part in match.group(4).split(":") if part)
    suffix = (match.group(5) or "").upper()
    two_field = f"{allele_gene}*{match.group(2)}:{match.group(3)}"
    classification = {
        "designation_type": "group" if suffix in {"P", "G"} else "allele",
        "membership_status": "not_checked",
        "mapping_status": "syntax_only",
        "normalized_allele": "" if suffix in {"P", "G"} else two_field,
    }
    if reference:
        classification = reference.classify(token, two_field, suffix)
    if not classification["normalized_allele"]:
        reason = ("group designation is not uniquely resolvable at two fields"
                  if suffix in {"P", "G"} else
                  f"allele is absent from IPD-IMGT/HLA {reference.release if reference else ''}")
        raise ValueError(reason.strip())
    return NormalizedAllele(
        raw=raw,
        gene=allele_gene,
        two_field=classification["normalized_allele"],
        suffix=suffix,
        higher_fields=higher,
        designation_type=classification["designation_type"],
        membership_status=classification["membership_status"],
        mapping_status=classification["mapping_status"],
        normalization_release=reference.release if reference else "",
    )


def normalize_diploid_call(a: str | None, b: str | None, gene: str,
                            *, explicit_homozygous: bool = False,
                            reference: "HLAReference | None" = None) -> dict[str, object]:
    """Normalize a caller result without inventing an unreported second allele."""
    raw_a, raw_b = (a or "").strip(), (b or "").strip()
    present = [not is_placeholder_allele(raw_a), not is_placeholder_allele(raw_b)]
    if not any(present):
        return {"call_status": "missing", "no_call_reason": "no_resolved_allele", "pair": None}
    if sum(present) == 1:
        value = raw_a if present[0] else raw_b
        try:
            allele = normalize_allele(value, gene, reference)
        except ValueError as exc:
            status = "ambiguous" if "/" in value else "invalid"
            return {"call_status": status, "no_call_reason": str(exc), "pair": None}
        if explicit_homozygous:
            return {
                "call_status": "complete", "no_call_reason": "",
                "pair": (allele.two_field, allele.two_field),
                "allele1_suffix": allele.suffix, "allele2_suffix": allele.suffix,
                "allele1_designation_type": allele.designation_type,
                "allele2_designation_type": allele.designation_type,
                "allele1_membership_status": allele.membership_status,
                "allele2_membership_status": allele.membership_status,
                "allele1_mapping_status": allele.mapping_status,
                "allele2_mapping_status": allele.mapping_status,
                "normalization_release": allele.normalization_release,
            }
        return {
            "call_status": "partial", "no_call_reason": "undetermined_second_allele",
            "pair": None, "allele1_two_field": allele.two_field,
            "allele1_suffix": allele.suffix,
            "allele1_designation_type": allele.designation_type,
            "allele1_membership_status": allele.membership_status,
            "allele1_mapping_status": allele.mapping_status,
            "normalization_release": allele.normalization_release,
        }
    try:
        first = normalize_allele(raw_a, gene, reference)
        second = normalize_allele(raw_b, gene, reference)
    except ValueError as exc:
        status = "ambiguous" if "/" in raw_a or "/" in raw_b else "invalid"
        return {"call_status": status, "no_call_reason": str(exc), "pair": None}
    return {
        "call_status": "complete", "no_call_reason": "",
        "pair": tuple(sorted((first.two_field, second.two_field))),
        "allele1_suffix": first.suffix, "allele2_suffix": second.suffix,
        "allele1_designation_type": first.designation_type,
        "allele2_designation_type": second.designation_type,
        "allele1_membership_status": first.membership_status,
        "allele2_membership_status": second.membership_status,
        "allele1_mapping_status": first.mapping_status,
        "allele2_mapping_status": second.mapping_status,
        "normalization_release": first.normalization_release or second.normalization_release,
    }


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_tsv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: str | Path, rows: Iterable[dict], fields: list[str] | None = None) -> None:
    rows = list(rows)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fields,
                                extrasaction="ignore", lineterminator="\n")
        if fields:
            writer.writeheader()
            writer.writerows(rows)


def read_json(path: str | Path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, value: object) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # Bytes, not write_text: on Windows write_text turns every \n into \r\n, so the
    # same manifest would differ between platforms.
    target.write_bytes((json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def reject_truth_columns(rows: list[dict[str, str]], context: str) -> None:
    if not rows:
        return
    columns = {column.lower() for column in rows[0]}
    forbidden = sorted(columns & TRUTH_TOKENS)
    if forbidden:
        raise ValueError(f"{context} contains forbidden truth-bearing columns: {forbidden}")


def normalize_modality(value: str) -> str:
    token = value.strip().lower().replace("-", "")
    aliases = {"rna": "rnaseq", "rnaseq": "rnaseq", "wgs": "wgs", "wes": "wes"}
    if token not in aliases:
        raise ValueError(f"unsupported modality: {value!r}")
    return aliases[token]


def normalize_gene(value: str) -> str:
    token = value.strip().upper()
    if token.startswith("HLA-"):
        token = token[4:]
    if token not in {"A", "B", "C"}:
        raise ValueError(f"unsupported primary gene: {value!r}")
    return token


def canonical_allele(value: str, gene: str | None = None) -> str:
    if not value.strip():
        return ""
    return normalize_allele(value, gene).two_field


def canonical_pair(a: str, b: str, gene: str | None = None) -> tuple[str, str]:
    first = canonical_allele(a, gene)
    second = canonical_allele(b, gene)
    if not first or not second:
        raise ValueError("a callable diploid pair requires two alleles")
    return tuple(sorted((first, second)))


def is_callable(row: dict[str, str]) -> bool:
    status = row.get("call_status", "").strip().lower()
    return status not in UNCALLABLE and bool(row.get("allele1", "").strip() and row.get("allele2", "").strip())


def row_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row.get("cohort", ""), row["subject"], normalize_modality(row["modality"]),
            normalize_gene(row["gene"]))


def require_columns(rows: list[dict[str, str]], required: set[str], context: str) -> None:
    if not rows:
        raise ValueError(f"{context} is empty")
    missing = sorted(required - set(rows[0]))
    if missing:
        raise ValueError(f"{context} missing columns: {missing}")
