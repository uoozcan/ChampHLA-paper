from __future__ import annotations

import csv
import json
from collections import defaultdict
from itertools import product
from pathlib import Path

from champhla_confirmation.io import canonical_allele

from .io import sha256, write_json, write_tsv


GENES = ("A", "B", "C")
MODALITIES = ("wgs", "wes", "rnaseq")


def _unique_two_field(value: str, gene: str) -> str:
    options = set()
    for raw in value.strip().split("/"):
        token = raw.strip()
        if not token:
            continue
        if "*" not in token:
            token = f"{gene}*{token}"
        options.add(canonical_allele(token, gene))
    if len(options) != 1:
        raise ValueError(f"ambiguous two-field allele {gene} {value!r}")
    return next(iter(options))


def _two_field_options(value: str, gene: str) -> set[str]:
    options = set()
    for raw in value.strip().split("/"):
        token = raw.strip()
        if not token:
            continue
        if "*" not in token:
            token = f"{gene}*{token}"
        options.add(canonical_allele(token, gene))
    return options


def candidate_genotype_pairs(first: str, second: str, gene: str) -> set[tuple[str, str]]:
    """Enumerate set-valued truth without selecting a preferred ambiguity branch."""
    left, right = _two_field_options(first, gene), _two_field_options(second, gene)
    return {tuple(sorted(pair)) for pair in product(left, right)}


def _read_2014(path: str) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter=" ", skipinitialspace=True))


def audit_two_field_resolution(source: str) -> dict[tuple[str, str], dict[str, str | int]]:
    """Explain whether each source subject/gene has one exact two-field pair."""
    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in _read_2014(source):
        subject = row.get("id", "").strip().upper()
        if subject:
            records[subject].append(row)
    audit: dict[tuple[str, str], dict[str, str | int]] = {}
    for subject, subject_rows in records.items():
        for gene in GENES:
            pairs = set()
            reasons = set()
            for row in subject_rows:
                try:
                    pairs.add(tuple(sorted((_unique_two_field(row[gene], gene),
                                            _unique_two_field(row[f"{gene}.1"], gene)))))
                except KeyError as exc:
                    reasons.add(f"missing_source_column:{exc.args[0]}")
                except ValueError as exc:
                    reasons.add(str(exc))
            # A resolved duplicate must never conceal an ambiguous or malformed
            # duplicate.  Every source row contributes to the locus-level truth
            # status, so any parse failure excludes the exact endpoint.
            if reasons:
                status = "excluded"
                reason = "; ".join(sorted(reasons))
            elif len(pairs) == 1:
                status, reason = "resolved", ""
            elif len(pairs) > 1:
                status, reason = "excluded", "conflicting_source_records"
            else:
                status = "excluded"
                reason = "; ".join(sorted(reasons)) or "unresolved_source_value"
            audit[(subject, gene)] = {
                "status": status, "reason": reason,
                "source_record_count": len(subject_rows),
            }
    return audit


def prepare_locked_truth(source: str, truth_output: str, registry_output: str,
                         manifest_output: str) -> dict:
    source_hash = sha256(source)
    parsed: dict[str, list[tuple[dict[str, tuple[str, str]], dict[str, str], str]]] = defaultdict(list)
    for row in _read_2014(source):
        subject = row.get("id", "").strip().upper()
        if not subject:
            continue
        pairs = {}
        errors = {}
        for gene in GENES:
            try:
                pair = sorted((_unique_two_field(row[gene], gene),
                               _unique_two_field(row[f"{gene}.1"], gene)))
                pairs[gene] = (pair[0], pair[1])
            except (KeyError, ValueError) as exc:
                errors[gene] = str(exc)
        parsed[subject].append((pairs, errors, row.get("sbgroup", "").strip()))

    truth_rows = []
    registry_rows = []
    conflicts = 0
    for subject in sorted(parsed):
        resolved = {}
        subject_conflict = False
        for gene in GENES:
            unique = {entry[0][gene] for entry in parsed[subject] if gene in entry[0]}
            gene_errors = {entry[1][gene] for entry in parsed[subject] if gene in entry[1]}
            if len(unique) == 1 and not gene_errors:
                resolved[gene] = next(iter(unique))
            elif len(unique) > 1 or (unique and gene_errors):
                subject_conflict = True
        if subject_conflict:
            conflicts += 1
        eligible = bool(resolved)
        complete = len(resolved) == len(GENES)
        population = next((entry[2] for entry in parsed[subject] if entry[2]), "")
        registry_rows.append({
            "subject": subject,
            "population": population,
            "primary_eligible": int(eligible),
            "complete_truth_available": int(complete),
            "exact_truth_loci": len(resolved),
            "source_record_count": len(parsed[subject]),
            "eligibility_reason": "" if eligible else "duplicate_conflict" if subject_conflict else "unresolved_or_ambiguous",
            "truth_source_sha256": source_hash,
        })
        if not eligible:
            continue
        for modality in MODALITIES:
            for gene in sorted(resolved):
                truth_rows.append({
                    "cohort": "1000G-2014-unseen",
                    "subject": subject,
                    "modality": modality,
                    "gene": gene,
                    "truth_allele1": resolved[gene][0],
                    "truth_allele2": resolved[gene][1],
                    "truth_status": "callable",
                    "truth_source": "2014 1000 Genomes laboratory HLA typing",
                    "source_sha256": source_hash,
                })

    write_tsv(truth_output, truth_rows, [
        "cohort", "subject", "modality", "gene", "truth_allele1", "truth_allele2",
        "truth_status", "truth_source", "source_sha256",
    ])
    write_tsv(registry_output, registry_rows, [
        "subject", "population", "primary_eligible", "complete_truth_available",
        "exact_truth_loci", "source_record_count", "eligibility_reason", "truth_source_sha256",
    ])
    result = {
        "schema_version": "locked-1000g-truth-1",
        "source_sha256": source_hash,
        "source_subjects": len(parsed),
        "eligible_any_exact_locus_subjects": sum(int(row["primary_eligible"]) for row in registry_rows),
        "eligible_complete_subjects": sum(int(row["complete_truth_available"]) for row in registry_rows),
        "duplicate_conflicts": conflicts,
        "truth_rows": len(truth_rows),
        "truth_output_sha256": sha256(truth_output),
        "registry_output_sha256": sha256(registry_output),
        "primary_truth": True,
        "inferred_2018_truth_allowed": False,
    }
    write_json(manifest_output, result)
    return result


def prepare_ambiguity_aware_truth(source: str, output: str, manifest_output: str) -> dict:
    """Preserve every valid two-field truth candidate for compatibility scoring."""
    source_hash = sha256(source)
    records: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in _read_2014(source):
        subject = row.get("id", "").strip().upper()
        if subject:
            records[subject].append(row)
    output_rows = []
    status_counts = defaultdict(int)
    for subject in sorted(records):
        population = next((row.get("sbgroup", "").strip() for row in records[subject]
                           if row.get("sbgroup", "").strip()), "")
        for gene in GENES:
            candidates: set[tuple[str, str]] = set()
            errors = []
            for row in records[subject]:
                try:
                    candidates.update(candidate_genotype_pairs(row[gene], row[f"{gene}.1"], gene))
                except (KeyError, ValueError) as exc:
                    errors.append(str(exc))
            status = "resolved" if len(candidates) == 1 else "ambiguous" if candidates else "invalid"
            status_counts[status] += 1
            encoded = json.dumps([list(pair) for pair in sorted(candidates)], separators=(",", ":"))
            for modality in MODALITIES:
                output_rows.append({
                    "cohort": "1000G-2014-candidate-truth", "subject": subject,
                    "population": population, "modality": modality, "gene": gene,
                    "truth_status": status, "truth_candidate_pairs_json": encoded,
                    "candidate_pair_count": len(candidates),
                    "parse_errors": " | ".join(sorted(set(errors))),
                    "truth_source": "2014 1000 Genomes laboratory HLA typing",
                    "source_sha256": source_hash,
                })
    fields = [
        "cohort", "subject", "population", "modality", "gene", "truth_status",
        "truth_candidate_pairs_json", "candidate_pair_count", "parse_errors",
        "truth_source", "source_sha256",
    ]
    write_tsv(output, output_rows, fields)
    result = {
        "schema_version": "set-valued-1000g-truth-1",
        "source_sha256": source_hash,
        "subjects": len(records),
        "subject_gene_status_counts": dict(sorted(status_counts.items())),
        "rows": len(output_rows),
        "output_sha256": sha256(output),
        "caller_outputs_used": False,
    }
    write_json(manifest_output, result)
    return result
