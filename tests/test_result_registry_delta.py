"""Registry-delta reporting and author stop-condition tests."""
from __future__ import annotations

import importlib.util
from pathlib import Path

from champhla_confirmation.io import write_tsv


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "compare_result_registry", ROOT / "scripts/compare_result_registry.py"
)
assert SPEC and SPEC.loader
DELTA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DELTA)


def _row(result_id: str, modality: str, method: str, estimate: str,
         fitted: str = "not_fitted", adjusted: str = "1") -> dict[str, str]:
    return {
        "result_id": result_id, "modality": modality, "method": method,
        "endpoint": ("paired_concordance_difference_percentage_points"
                     if "PAIRED" in result_id else
                     "exact_unordered_two_field_genotype_concordance"),
        "accuracy": "" if "PAIRED" in result_id else estimate,
        "estimate": estimate, "fitted_status": fitted, "adjusted_p": adjusted,
        "sensitivity_adjusted_p": adjusted, "loci": "10", "callable_denominator": "9",
        "artifact_sha256": "a", "source_artifact_sha256": "a",
    }


def _registries(tmp_path: Path) -> tuple[Path, Path]:
    old, new = tmp_path / "old.tsv", tmp_path / "new.tsv"
    rows = [
        _row("DEV_CORRECTED_WES_SIMPLEPLURALITYLEX", "wes", "SimplePluralityLex", "0.9"),
        _row("DEV_CORRECTED_WES_CALLER_A", "wes", "Caller:A", "0.9"),
        _row("DEV_CORRECTED_WES_CALLER_B", "wes", "Caller:B", "0.8"),
        _row("DEV_CORRECTED_WES_FIT", "wes", "Fit", "0.9", "fitted"),
        _row("DEV_PAIRED_WES_CALLER_A", "wes", "ChampHLA minus A", "0", adjusted="1"),
    ]
    write_tsv(old, rows)
    write_tsv(new, rows)
    return old, new


def test_identical_registries_do_not_trigger_stop(tmp_path: Path):
    old, new = _registries(tmp_path)
    rows, summary = DELTA.compare(old, new)
    assert not summary["author_approval_required"]
    assert summary["status_counts"]["unchanged"] == 5
    DELTA.write_reports(rows, summary, tmp_path / "report")
    assert (tmp_path / "report/result_registry_delta.tsv").is_file()
    assert "No headline-sensitive" in (
        tmp_path / "report/result_registry_delta.md"
    ).read_text(encoding="utf-8")


def test_delta_records_checkout_independent_registry_paths(tmp_path: Path):
    old, new = _registries(tmp_path)
    _, summary = DELTA.compare(old, new)
    # Outside the repository only the file name is kept; inside, the repo-relative path.
    assert summary["old_registry"] == "old.tsv"
    assert summary["new_registry"] == "new.tsv"
    assert DELTA._repo_path(ROOT / "result_registry.tsv") == "result_registry.tsv"


def test_direction_ranking_and_significance_changes_trigger_stop(tmp_path: Path):
    old, new = _registries(tmp_path)
    rows = []
    import csv
    with new.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    for row in rows:
        if row["result_id"] == "DEV_CORRECTED_WES_CALLER_B":
            row["accuracy"] = row["estimate"] = "0.95"
        if row["result_id"] == "DEV_PAIRED_WES_CALLER_A":
            row["estimate"] = "-1"
            row["adjusted_p"] = "0.01"
    write_tsv(new, rows)
    delta, summary = DELTA.compare(old, new)
    assert summary["author_approval_required"]
    reasons = " ".join(summary["author_approval_reasons"])
    assert "strongest-caller identity changed" in reasons
    assert "headline direction changed" in reasons
    assert "significance interpretation changed" in reasons
    assert any(row["status"] == "changed" for row in delta)


def test_author_approval_is_bound_to_the_exact_registry_and_reasons(tmp_path: Path):
    import hashlib
    import json
    registry = tmp_path / "result_registry.tsv"
    registry.write_bytes(b"result_id\nA\n")
    summary = {"author_approval_required": True, "author_approval_reasons": ["b", "a"]}
    approval = tmp_path / "approval.json"
    assert not DELTA.approval_matches(summary, registry, approval)  # no record
    record = {"status": "SIGNED - test", "decision": {
        "approved_registry_sha256": hashlib.sha256(registry.read_bytes()).hexdigest(),
        "approved_reasons": ["a", "b"]}}
    approval.write_text(json.dumps(record), encoding="utf-8")
    assert DELTA.approval_matches(summary, registry, approval)
    # any change to a result voids the approval
    registry.write_bytes(b"result_id\nB\n")
    assert not DELTA.approval_matches(summary, registry, approval)
    registry.write_bytes(b"result_id\nA\n")
    assert not DELTA.approval_matches(
        {**summary, "author_approval_reasons": ["a", "b", "c"]}, registry, approval)
    approval.write_text(json.dumps({**record, "status": "PROPOSED"}), encoding="utf-8")
    assert not DELTA.approval_matches(summary, registry, approval)
    # nothing to approve passes without a record
    assert DELTA.approval_matches({"author_approval_required": False}, registry,
                                  tmp_path / "absent.json")
