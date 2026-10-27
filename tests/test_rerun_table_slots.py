"""Rerun-dependent manuscript slots are generated from artifacts, never hand-filled."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_manuscript_tables", ROOT / "scripts/generate_manuscript_tables.py"
)
assert SPEC and SPEC.loader
TABLES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TABLES)


def _performance(method: str, correct: str, callable_: str = "3"):
    return {
        "modality": "wes", "method": method, "analysis_scope": "primary",
        "callable": callable_, "loci": "3", "genotypes_correct": correct,
        "genotype_accuracy": str(int(correct) / 3), "genotype_ci_lo": "0",
        "genotype_ci_hi": "1", "called_only_accuracy": str(int(correct) / int(callable_)),
        "called_only_ci_lo": "0", "called_only_ci_hi": "1",
    }


def test_main_table_adds_corrected_reference_column_for_every_displayed_method():
    performance = [_performance("SimplePluralityLex", "2")]
    corrected = [{
        "modality": "wes", "method": "SimplePluralityLex",
        "agreement_correct": "2", "agreement_loci": "2",
    }]

    rendered = TABLES.main_table(performance, corrected)

    assert "Exact-reference correct" in rendered
    assert "Corrected-reference sensitivity, correct" in rendered
    assert "2/2" in rendered


def test_main_table_fails_if_a_corrected_reference_method_is_missing():
    with pytest.raises(ValueError, match="missing corrected-reference row"):
        TABLES.main_table([_performance("SimplePluralityLex", "2")], [])


def test_singleton_slot_places_completed_and_abstain_rows_side_by_side():
    primary = [_performance("Caller:T1K", "2", "3")]
    primary[0]["analysis_scope"] = "descriptive_comparator"
    abstain = [_performance("Caller:T1K", "1", "2")]
    abstain[0]["analysis_scope"] = "descriptive_comparator"

    rendered = TABLES.singleton_sensitivity_table(primary, abstain)

    assert "Native-declaration correct" in rendered
    assert "Abstain-all correct" in rendered
    assert "T1K" in rendered
    assert "2/3" in rendered and "1/3" in rendered


def test_rerun_ledgers_render_only_aggregate_counts():
    cells = [{
        "subject": "SENSITIVE", "modality": "wes", "caller": "OptiType",
        "difference_class": "call_changed",
    }]
    tasks = [{
        "subject": "SENSITIVE", "modality": "wes", "caller": "OptiType",
        "disposition": "outputs_present",
    }]

    cell_table = TABLES.rerun_cell_comparison_table(cells)
    state_table = TABLES.rerun_state_table(tasks)

    assert "SENSITIVE" not in cell_table + state_table
    assert "OptiType" in cell_table + state_table
    assert "call changed" in cell_table
    assert "outputs present" in state_table


def _cell(subject, caller, stored, rerun, difference="call_changed",
          stored_status="callable", rerun_status="callable"):
    return {
        "subject": subject, "modality": "wes", "gene": "A", "caller": caller,
        "stored_call_status": stored_status, "stored_allele1": stored[0],
        "stored_allele2": stored[1], "rerun_call_status": rerun_status,
        "rerun_allele1": rerun[0], "rerun_allele2": rerun[1],
        "difference_class": difference,
    }


def test_rerun_change_character_classifies_changes_truth_free():
    cells = [
        # SENSITIVE1: HLA-HD alone replaces one allele, toward both other callers.
        _cell("SENSITIVE1", "OptiType", ("A*01:01", "A*02:01"), ("A*01:01", "A*02:01"),
              "identical"),
        _cell("SENSITIVE1", "HLA-HD", ("A*01:01", "A*03:01"), ("A*01:01", "A*02:01")),
        _cell("SENSITIVE1", "T1K", ("A*01:01", "A*02:01"), ("A*01:01", "A*02:01"), "identical"),
        # SENSITIVE2: HLA-HD homozygous to heterozygous; T1K partial to native homozygous.
        _cell("SENSITIVE2", "OptiType", ("A*11:01", "A*24:02"), ("A*11:01", "A*24:02"),
              "identical"),
        _cell("SENSITIVE2", "HLA-HD", ("A*11:01", "A*11:01"), ("A*11:01", "A*24:02")),
        _cell("SENSITIVE2", "T1K", ("", ""), ("A*11:01", "A*11:01"), "noncall_to_callable",
              "partial", "callable"),
    ]
    t1k = [{"subject": "SENSITIVE1", "modality": "wes", "gene": "A",
            "disposition": "complete_heterozygous"},
           {"subject": "SENSITIVE2", "modality": "wes", "gene": "A",
            "disposition": "native_homozygous"}]

    rendered = TABLES.rerun_cell_change_character_table(cells, t1k)
    rows = {line.split(" | ")[1]: line.strip("| ").split(" | ")
            for line in rendered.splitlines()[2:]}

    assert "SENSITIVE" not in rendered
    assert "OptiType" not in rows
    # changed, state, hom->het, het->hom, one, both, group, T1K rule, alone,
    # rerun closer, stored closer (equal matches are the remainder)
    assert rows["HLA-HD"][2:] == ["2", "0", "1", "0", "1", "0", "2", "–", "1", "1", "0"]
    assert rows["T1K"][2:] == ["1", "1", "0", "0", "0", "0", "0", "1", "0", "0", "0"]


def test_rerun_change_character_requires_a_parser_row_for_changed_t1k_cells():
    cells = [_cell("S", "T1K", ("A*01:01", "A*02:01"), ("A*01:01", "A*03:01"))]
    with pytest.raises(ValueError, match="parser audit"):
        TABLES.rerun_cell_change_character_table(cells, [])
