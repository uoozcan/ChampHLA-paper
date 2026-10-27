from __future__ import annotations

from pathlib import Path

from .io import read_tsv, sha256


REQUIRED = {
    "result_id", "cohort", "modality", "method", "analysis_status", "validity",
    "subjects", "loci", "correct", "accuracy", "artifact_path", "artifact_sha256",
    "abstract_allowed", "claim_boundary",
}
VERSIONED_REQUIRED = {
    "schema_version", "endpoint", "intended_denominator", "acquired_denominator",
    "truth_evaluable_denominator", "callable_denominator", "ci_lo", "ci_hi",
    "interval_method", "raw_p", "adjusted_p", "sensitivity_adjusted_p",
    "inference_family", "family_size", "fitted_status", "development_status",
    "source_artifact_sha256", "record_type", "workflow_session", "workflow_commit",
    "resource_record_count",
    "result_kind", "estimate", "ci_low", "ci_high", "unit", "events",
}
ACTIVE_SCHEMA = "panelhla-result-registry-4"
RECORD_TYPES = {"scientific_result", "single_sample_workflow_smoke", "protocol_change_ledger"}
RESULT_KINDS = {"performance", "concordance", "categorical-summary", "survival-effect",
                "design-limit", "association"}
ANALYSIS_STATUSES = {
    "descriptive_comparator",
    "discovery",
    "exploratory_coequal",
    "exploratory_descriptive",
    "exploratory_diagnostic",
    "exploratory_diagnostic_non_estimable",
    "exploratory_fitted",
    "exploratory_primary",
    "exploratory_sensitivity",
    "exploratory_sensitivity_non_estimable",
    "external_confirmation",
    "historical_invalid",
    "operational_provenance",
    # The frozen extension (decisions/20261013_extension_v350_preregistration_amendment.json):
    # pre-registered on unseen subjects of the same resource, never external confirmation.
    "preregistered_confirmatory",
    "preregistered_descriptive",
    "primary",
    "secondary_sensitivity",
}


def validate_registry(path: str, root: str | None = None) -> list[str]:
    rows = read_tsv(path)
    failures = []
    if not rows:
        return ["result registry is empty"]
    missing = sorted(REQUIRED - set(rows[0]))
    if missing:
        return [f"missing registry columns: {missing}"]
    versioned = "schema_version" in rows[0]
    if versioned:
        missing = sorted(VERSIONED_REQUIRED - set(rows[0]))
        if missing:
            return [f"missing versioned registry columns: {missing}"]
    seen = set()
    base = Path(root) if root else Path(path).resolve().parent
    for row in rows:
        rid = row["result_id"]
        if rid in seen:
            failures.append(f"duplicate result_id: {rid}")
        seen.add(rid)
        if versioned and row["schema_version"] != ACTIVE_SCHEMA:
            failures.append(
                f"unknown or mixed schema_version for {rid}: {row['schema_version']!r}"
            )
        if versioned and row["record_type"] not in RECORD_TYPES:
            failures.append(f"unknown record_type for {rid}: {row['record_type']!r}")
        if versioned and row["result_kind"] not in RESULT_KINDS:
            failures.append(f"unknown result_kind for {rid}: {row['result_kind']!r}")
        if row["analysis_status"] not in ANALYSIS_STATUSES:
            failures.append(
                f"unknown analysis_status for {rid}: {row['analysis_status']!r}"
            )
        artifact = base / row["artifact_path"]
        if not artifact.is_file():
            failures.append(f"missing artifact for {rid}: {artifact}")
        elif sha256(artifact) != row["artifact_sha256"]:
            failures.append(f"artifact checksum mismatch for {rid}")
        if versioned and row["source_artifact_sha256"] != row["artifact_sha256"]:
            failures.append(f"source artifact checksum mismatch for {rid}")
        if row["abstract_allowed"] == "1" and row["validity"] != "valid":
            failures.append(f"invalid result allowed in abstract: {rid}")
        if row["analysis_status"] == "discovery" and row["abstract_allowed"] == "1":
            failures.append(f"discovery result allowed in abstract: {rid}")
    return failures


def render_tables(registry_path: str, output_path: str) -> None:
    rows = read_tsv(registry_path)
    lines = [
        "# Registered ChampHLA results", "",
        "| Result | Cohort | Modality | Method | Status | Validity | Correct / loci | Accuracy | Abstract |",
        "|---|---|---|---|---|---|---:|---:|---|",
    ]
    for row in rows:
        if row["validity"] != "valid":
            # A row whose input is invalid has no admissible performance figure.
            # Rendering one put the project's own banned invalid-WGS numbers into
            # a manuscript fragment, where the claim audit hard-fails on them.
            count = accuracy = "withheld (invalid input)"
        else:
            count = f"{row['correct']} / {row['loci']}" if row["loci"] else "—"
            accuracy = row["accuracy"] or "—"
        lines.append(
            f"| {row['result_id']} | {row['cohort']} | {row['modality']} | {row['method']} | "
            f"{row['analysis_status']} | {row['validity']} | {count} | {accuracy} | "
            f"{'yes' if row['abstract_allowed'] == '1' else 'no'} |"
        )
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
