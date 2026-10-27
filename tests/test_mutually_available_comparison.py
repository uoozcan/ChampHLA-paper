"""SR-007 regression coverage for absent rows and mutually available scoring."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "artifacts/development_characterisation"
    / "caller_mutually_available_comparison.tsv"
)


def rows() -> dict[tuple[str, str], dict[str, str]]:
    with ARTIFACT.open(newline="", encoding="utf-8") as handle:
        return {
            (row["modality"], row["caller"]): row
            for row in csv.DictReader(handle, delimiter="\t")
        }


def _rerun_inputs() -> bool:
    import json
    manifest = ROOT / "data/development/input_manifest.json"
    return json.loads(manifest.read_text(encoding="utf-8")).get(
        "schema_version") == "champhla-development-rerun-inputs-1"


def test_rerun_closes_the_hlahd_fixed_denominator_gap():
    if not _rerun_inputs():
        return
    # the v3.5.0 collector emits every panel caller cell, so HLA-HD RNA-seq has no
    # absent rows to account for
    row = rows()[("rnaseq", "HLA-HD")]
    assert row["fixed_loci"] == row["stored_rows"] == row["mutually_available_loci"] == "118"
    assert row["absent_rows"] == "0" and row["absent_subject_gene"] == ""
    assert row["historical_task_state_for_absent_rows"] == "not_applicable"


def test_na19130_accounts_for_hlahd_fixed_denominator_gap():
    if _rerun_inputs():
        return  # historical stored outputs only; see the test above for the rerun
    row = rows()[("rnaseq", "HLA-HD")]
    assert row["fixed_loci"] == "118"
    assert row["stored_rows"] == row["mutually_available_loci"] == "115"
    assert row["absent_rows"] == "3"
    assert row["absent_subject_gene"] == (
        "NA19130:HLA-A;NA19130:HLA-B;NA19130:HLA-C"
    )
    assert row["consensus_correct_fixed"] == "113"
    assert row["caller_correct_fixed"] == "110"
    assert row["consensus_correct_mutually_available"] == "110"
    assert row["caller_correct_mutually_available"] == "110"
    assert row["consensus_wins_mutually_available"] == "0"
    assert row["consensus_losses_mutually_available"] == "0"
    assert row["historical_task_state_for_absent_rows"] == (
        "unrecoverable_from_stored_artifacts"
    )


def test_reader_facing_text_does_not_invent_historical_task_state():
    main = (ROOT / "manuscripts/benchmark/manuscript.md").read_text(encoding="utf-8")
    supplement = (
        ROOT / "manuscripts/benchmark/supplementary.md"
    ).read_text(encoding="utf-8")
    if _rerun_inputs():
        assert "In the v3.5.0 rerun every panel caller returned a row" in main
        assert "In the v3.5.0 rerun no panel caller row is absent." in supplement
    else:
        assert "On the 115 loci with an HLA-HD row, both" in main
        assert "methods were correct at 110" in main
        assert "failed, produced no retained output or were not" in main
    assert "arcasHLA-only 1/1 vote" in supplement
    assert "cannot distinguish" in supplement
    assert "DEV_MUTUALLY_AVAILABLE_RNASEQ_HLA_HD" in (
        ROOT / "result_registry.tsv"
    ).read_text(encoding="utf-8")
