from __future__ import annotations

from collections import Counter

from .io import read_json, read_tsv, sha256, write_json


EXPOSED_ROLES = frozenset({"development_exposed", "evaluation_exposed"})


def validate_benchmark_resource_protocol(protocol_path: str, roster_path: str,
                                         exposure_path: str,
                                         output_path: str | None = None) -> dict:
    protocol = read_json(protocol_path)
    rosters = read_tsv(roster_path)
    exposure = read_tsv(exposure_path)
    configured = protocol["extension_rosters"]
    selected = [row for row in rosters if row.get("modality") in {"wes", "rnaseq"}]
    counts = Counter(row["modality"] for row in selected)
    duplicates = [key for key, count in Counter(
        (row["subject"].strip().upper(), row["modality"]) for row in selected
    ).items() if count != 1]
    exposed = {
        row.get("canonical_subject", row.get("subject", "")).strip().upper()
        for row in exposure if row.get("exposure_role") in EXPOSED_ROLES
    }
    overlaps = sorted({row["subject"].strip().upper() for row in selected} & exposed)
    failures = []
    expected = {"wes": int(configured["wes_subjects"]),
                "rnaseq": int(configured["rnaseq_subjects"])}
    if dict(counts) != expected:
        failures.append(f"roster counts differ: observed={dict(counts)} expected={expected}")
    if duplicates:
        failures.append(f"duplicate subject/modality rows: {duplicates[:10]}")
    if overlaps:
        failures.append(f"development/evaluation overlap: {overlaps[:10]}")
    if "wgs" in protocol.get("modalities", []) or protocol.get("wgs_accuracy_allowed"):
        failures.append("protocol permits WGS accuracy")
    result = {
        "schema_version": "panelhla-benchmark-resource-protocol-audit-1",
        "valid": not failures,
        "failures": failures,
        "selected_subjects_by_modality": dict(sorted(counts.items())),
        "development_extension_overlap": overlaps,
        "wgs_rows_in_source_roster": sum(row.get("modality") == "wgs" for row in rosters),
        "wgs_rows_selected": 0,
        "protocol_sha256": sha256(protocol_path),
        "roster_sha256": sha256(roster_path),
        "exposure_ledger_sha256": sha256(exposure_path),
        "truth_join_permitted": not failures,
    }
    if output_path:
        write_json(output_path, result)
    return result
