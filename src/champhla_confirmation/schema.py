from __future__ import annotations

from typing import TYPE_CHECKING

from .io import (
    SINGLETON_POLICIES,
    declares_native_homozygosity,
    normalize_diploid_call,
    normalize_gene,
    normalize_modality,
)

if TYPE_CHECKING:
    from .hla_reference import HLAReference

MISSING_ALLELE_TOKENS = {"", "NOTTYPED", "NOT_TYPED", "NA", "N/A", "NONE", "UNKNOWN", "."}


def _reported_alleles(row: dict[str, str]) -> tuple[str, str]:
    raw1 = row.get("allele1_raw", "").strip()
    raw2 = row.get("allele2_raw", "").strip()
    # Recovered fitted-method rows did not carry native raw fields. In that
    # specific shape, their normalized emitted pair is the only reported call.
    if not raw1 and not raw2:
        return row.get("allele1", "").strip(), row.get("allele2", "").strip()
    return raw1, raw2


def normalize_status(value: str, has_pair: bool) -> str:
    token = value.strip().lower()
    if token in {"callable", "called", "call", "pass", "passed", "typed"}:
        return "callable" if has_pair else "missing"
    if token in {"", "unknown"}:
        return "callable" if has_pair else "missing"
    return token


def normalize_caller_row(row: dict[str, str], cohort_default: str = "",
                         reference: "HLAReference | None" = None,
                         singleton_policy: str = "abstain") -> dict[str, str]:
    if singleton_policy not in SINGLETON_POLICIES:
        raise ValueError(f"unknown singleton policy {singleton_policy!r}")
    subject = row.get("subject", row.get("sample", "")).strip()
    caller = row.get("caller", row.get("tool", "")).strip()
    if not subject or not caller:
        raise ValueError("caller rows require subject/sample and caller/tool")
    modality = normalize_modality(row["modality"])
    gene = normalize_gene(row["gene"])
    raw1, raw2 = _reported_alleles(row)
    native = (singleton_policy == "native_declaration"
              and declares_native_homozygosity(caller, raw1, raw2))
    normalized = normalize_diploid_call(raw1, raw2, gene, explicit_homozygous=native,
                                        reference=reference)
    pair = normalized.get("pair")
    a1, a2 = pair if pair else ("", "")
    status = "callable" if pair else str(normalized["call_status"])
    return {
        "cohort": row.get("cohort", cohort_default), "subject": subject,
        "superpopulation": row.get("superpopulation", row.get("population", "")),
        "modality": modality, "gene": gene, "caller": caller,
        "homozygosity_basis": (
            "" if not pair else "caller_native_declaration" if native else "two_alleles"
        ),
        "allele1_raw": raw1, "allele2_raw": raw2,
        "original_allele1": raw1, "original_allele2": raw2,
        "allele1": a1, "allele2": a2, "call_status": status,
        "no_call_reason": str(normalized.get("no_call_reason", "")),
        "allele1_suffix": str(normalized.get("allele1_suffix", "")),
        "allele2_suffix": str(normalized.get("allele2_suffix", "")),
        "allele1_designation_type": str(normalized.get("allele1_designation_type", "")),
        "allele2_designation_type": str(normalized.get("allele2_designation_type", "")),
        "allele1_membership_status": str(normalized.get("allele1_membership_status", "")),
        "allele2_membership_status": str(normalized.get("allele2_membership_status", "")),
        "allele1_mapping_status": str(normalized.get("allele1_mapping_status", "")),
        "allele2_mapping_status": str(normalized.get("allele2_mapping_status", "")),
        "caller_version": row.get("caller_version", ""),
        "database_version": row.get("caller_database_version", row.get("database_version", "")),
        "database_version_basis": row.get("database_version_basis", ""),
        "normalization_database_version": str(normalized.get("normalization_release", "")) or row.get(
            "normalization_database_version", row.get("imgt_hla_version", "")
        ),
        "normalization_release": str(normalized.get("normalization_release", "")),
        "caller_database_release": row.get(
            "caller_database_release", row.get("caller_database_version", row.get("database_version", ""))
        ),
        "input_reference_build": row.get("input_reference_build", row.get("reference_build", "")),
        "container_digest": row.get("container_digest", ""),
        "source_path": row.get("source_path", row.get("source_file", "")),
        "source_sha256": row.get("source_sha256", ""),
    }


def normalize_raw_cc_row(row: dict[str, str], cohort_default: str = "") -> dict[str, str]:
    subject = row.get("subject", row.get("sample", "")).strip()
    modality = normalize_modality(row["modality"])
    gene = normalize_gene(row["gene"])
    raw1, raw2 = _reported_alleles(row)
    normalized = normalize_diploid_call(raw1, raw2, gene)
    pair = normalized.get("pair")
    a1, a2 = pair if pair else ("", "")
    status = "callable" if pair else str(normalized["call_status"])
    return {
        "cohort": row.get("cohort", cohort_default), "subject": subject,
        "superpopulation": row.get("superpopulation", row.get("population", "")),
        "modality": modality, "gene": gene, "method": "ChampionChallenger",
        "allele1_raw": raw1, "allele2_raw": raw2,
        "allele1": a1, "allele2": a2, "call_status": status,
        "no_call_reason": str(normalized.get("no_call_reason", "")),
    }


def normalize_method_row(row: dict[str, str], cohort_default: str = "") -> dict[str, str]:
    normalized = normalize_raw_cc_row({**row, "method": "ChampionChallenger"}, cohort_default)
    normalized["method"] = row.get("method", "").strip()
    if not normalized["method"]:
        raise ValueError("secondary method row has no method")
    return normalized


def explode_candidate_rows(rows: list[dict[str, str]], cohort_default: str = "",
                           reference: "HLAReference | None" = None) -> list[dict[str, str]]:
    """Convert candidate/support rows into one exact call per supporting caller."""
    output = []
    seen = set()
    for row in rows:
        callers = row.get("supporting_callers", row.get("supporting_tools", "")).split(",")
        for caller in filter(None, (value.strip() for value in callers)):
            converted = normalize_caller_row({**row, "caller": caller}, cohort_default, reference)
            key = (converted["cohort"], converted["subject"], converted["modality"],
                   converted["gene"], converted["caller"])
            if key in seen:
                raise ValueError(f"caller appears in multiple candidate pairs at {key}")
            seen.add(key)
            output.append(converted)
    return output
