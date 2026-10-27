#!/usr/bin/env python3
"""Compare complete result registries and flag author-approval stop conditions."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

KEY_FIELDS = (
    "subjects", "loci", "intended_denominator", "acquired_denominator",
    "truth_evaluable_denominator", "callable_denominator", "correct", "accuracy",
    "estimate", "ci_lo", "ci_hi", "ci_low", "ci_high", "raw_p", "adjusted_p",
    "sensitivity_adjusted_p", "endpoint", "method", "fitted_status", "artifact_path",
    "artifact_sha256", "source_artifact_sha256",
)


def _repo_path(path: Path) -> str:
    """Record a registry path relative to the repository, so the delta is checkout-independent."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.name


def read_registry(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if "result_id" not in fields:
        raise ValueError(f"registry lacks result_id: {path}")
    identifiers = [row["result_id"] for row in rows]
    if not all(identifiers) or len(identifiers) != len(set(identifiers)):
        raise ValueError(f"registry has blank or duplicate result_id values: {path}")
    return fields, {row["result_id"]: row for row in rows}


def _number(row: dict[str, str]) -> float | None:
    for field in ("accuracy", "estimate"):
        value = row.get(field, "")
        if value:
            return float(value)
    return None


def _top_methods(rows: dict[str, dict[str, str]], fitted: bool) -> dict[str, list[str]]:
    selected: dict[str, list[tuple[str, float]]] = {}
    for row in rows.values():
        if row.get("endpoint") != "exact_unordered_two_field_genotype_concordance":
            continue
        method = row.get("method", "")
        is_fitted = row.get("fitted_status") == "fitted"
        if fitted != is_fitted:
            continue
        if not fitted and not method.startswith("Caller:"):
            continue
        value = _number(row)
        if value is not None:
            selected.setdefault(row.get("modality", ""), []).append((method, value))
    output = {}
    for modality, values in selected.items():
        maximum = max(value for _, value in values)
        output[modality] = sorted(method for method, value in values if value == maximum)
    return output


def _fitted_conclusion(rows: dict[str, dict[str, str]]) -> dict[str, dict]:
    by_assay: dict[str, dict[str, object]] = {}
    for modality in {row.get("modality", "") for row in rows.values()}:
        exact = [
            row for row in rows.values()
            if row.get("modality") == modality
            and row.get("endpoint") == "exact_unordered_two_field_genotype_concordance"
        ]
        plurality = next((row for row in exact if row.get("method") == "SimplePluralityLex"), None)
        fitted = [row for row in exact if row.get("fitted_status") == "fitted"]
        if not plurality or not fitted:
            continue
        plurality_value = _number(plurality)
        fitted_values = [(row.get("method", ""), _number(row)) for row in fitted]
        fitted_values = [(method, value) for method, value in fitted_values if value is not None]
        if plurality_value is None or not fitted_values:
            continue
        best = max(value for _, value in fitted_values)
        by_assay[modality] = {
            "any_fitted_improves_on_plurality": best > plurality_value,
            "best_fitted_methods": sorted(method for method, value in fitted_values if value == best),
            "best_fitted_estimate": best,
            "plurality_estimate": plurality_value,
        }
    return by_assay


def _direction(value: str) -> str:
    if not value:
        return "missing"
    number = float(value)
    return "positive" if number > 0 else "negative" if number < 0 else "zero"


def _significant(value: str) -> bool | None:
    return float(value) < 0.05 if value else None


def compare(old_path: Path, new_path: Path) -> tuple[list[dict[str, str]], dict]:
    old_fields, old = read_registry(old_path)
    new_fields, new = read_registry(new_path)
    fields = sorted(set(old_fields) | set(new_fields))
    delta_rows = []
    approval_reasons: list[str] = []
    for result_id in sorted(set(old) | set(new)):
        before, after = old.get(result_id), new.get(result_id)
        status = "added" if before is None else "removed" if after is None else "unchanged"
        changed = []
        if before is not None and after is not None:
            changed = [field for field in fields if before.get(field, "") != after.get(field, "")]
            if changed:
                status = "changed"
        row = {
            "result_id": result_id,
            "status": status,
            "changed_fields": ",".join(changed),
        }
        for field in KEY_FIELDS:
            row[f"old_{field}"] = "" if before is None else before.get(field, "")
            row[f"new_{field}"] = "" if after is None else after.get(field, "")
        delta_rows.append(row)
        critical = result_id.startswith(("DEV_CORRECTED_", "DEV_PAIRED_"))
        if status in {"added", "removed"} and critical:
            approval_reasons.append(f"critical registry row {status}: {result_id}")
        if before is not None and after is not None:
            if before.get("endpoint") != after.get("endpoint"):
                approval_reasons.append(f"endpoint changed: {result_id}")
            if result_id.startswith("DEV_PAIRED_") and (
                _direction(before.get("estimate", "")) != _direction(after.get("estimate", ""))
            ):
                approval_reasons.append(f"headline direction changed: {result_id}")
            for field in ("adjusted_p", "sensitivity_adjusted_p"):
                if _significant(before.get(field, "")) != _significant(after.get(field, "")):
                    approval_reasons.append(
                        f"significance interpretation changed ({field}): {result_id}"
                    )

    old_callers, new_callers = _top_methods(old, fitted=False), _top_methods(new, fitted=False)
    old_fitted, new_fitted = _top_methods(old, fitted=True), _top_methods(new, fitted=True)
    old_conclusion, new_conclusion = _fitted_conclusion(old), _fitted_conclusion(new)
    if old_callers != new_callers:
        approval_reasons.append("strongest-caller identity changed")
    if old_fitted != new_fitted:
        approval_reasons.append("fitted-policy ranking changed")
    if old_conclusion != new_conclusion:
        approval_reasons.append("fitted-policy conclusion changed")
    summary = {
        "schema_version": "champhla-result-registry-delta-1",
        "old_registry": _repo_path(old_path),
        "new_registry": _repo_path(new_path),
        "old_rows": len(old),
        "new_rows": len(new),
        "status_counts": {
            status: sum(row["status"] == status for row in delta_rows)
            for status in ("unchanged", "changed", "added", "removed")
        },
        "old_strongest_callers": old_callers,
        "new_strongest_callers": new_callers,
        "old_best_fitted": old_fitted,
        "new_best_fitted": new_fitted,
        "old_fitted_conclusion": old_conclusion,
        "new_fitted_conclusion": new_conclusion,
        "author_approval_required": bool(approval_reasons),
        "author_approval_reasons": sorted(set(approval_reasons)),
    }
    return delta_rows, summary


def write_reports(rows: list[dict[str, str]], summary: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["result_id", "status", "changed_fields"]
    with (output_dir / "result_registry_delta.tsv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (output_dir / "result_registry_delta.json").write_bytes(
        (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode("utf-8")
    )
    counts = summary["status_counts"]
    reasons = summary["author_approval_reasons"]
    lines = [
        "# ChampHLA result-registry delta",
        "",
        f"Old rows: {summary['old_rows']}; new rows: {summary['new_rows']}.",
        "",
        "| Unchanged | Changed | Added | Removed |",
        "|---:|---:|---:|---:|",
        f"| {counts['unchanged']} | {counts['changed']} | {counts['added']} | {counts['removed']} |",
        "",
        "## Author-approval gate",
        "",
        ("STOP: author approval is required before prose is revised."
         if reasons else "No headline-sensitive stop condition was detected."),
    ]
    if reasons:
        lines.extend(["", *[f"- {reason}" for reason in reasons]])
    lines.extend([
        "", "## Ranking checks", "",
        f"- Old strongest callers: `{json.dumps(summary['old_strongest_callers'], sort_keys=True)}`",
        f"- New strongest callers: `{json.dumps(summary['new_strongest_callers'], sort_keys=True)}`",
        f"- Old best fitted: `{json.dumps(summary['old_best_fitted'], sort_keys=True)}`",
        f"- New best fitted: `{json.dumps(summary['new_best_fitted'], sort_keys=True)}`",
        "",
        "The TSV contains one row for every identifier in either registry, including "
        "denominators, callability, estimates, intervals, tests and artifact hashes.",
    ])
    (output_dir / "result_registry_delta.md").write_bytes(
        ("\n".join(lines) + "\n").encode("utf-8")
    )


def approval_matches(summary: dict, registry_path: Path, approval_path: Path) -> bool:
    """True only if a signed author record approves exactly this registry and delta.

    The record pins the SHA-256 of the approved result_registry.tsv and the full list of
    stop reasons, so any later change to a result voids the approval and stops again."""
    if not summary.get("author_approval_required"):
        return True
    if not approval_path.is_file():
        return False
    import hashlib
    record = json.loads(approval_path.read_text(encoding="utf-8"))
    decision = record.get("decision", {})
    return (
        str(record.get("status", "")).startswith("SIGNED")
        and decision.get("approved_registry_sha256")
        == hashlib.sha256(registry_path.read_bytes()).hexdigest()
        and sorted(decision.get("approved_reasons", []))
        == sorted(summary.get("author_approval_reasons", []))
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old_registry", type=Path)
    parser.add_argument("new_registry", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    rows, summary = compare(args.old_registry, args.new_registry)
    write_reports(rows, summary, args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 2 if summary["author_approval_required"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
