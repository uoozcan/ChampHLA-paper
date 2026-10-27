from __future__ import annotations

import importlib.util
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/import_fimm_caller_predictions.py"


def _load():
    spec = importlib.util.spec_from_file_location("import_fimm_caller_predictions", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


importer = _load()

COLUMNS = ["Method", "Seq_type", "Patient_sample", "Patient",
           "HLA_A_1", "HLA_A_2", "HLA_B_1", "HLA_B_2", "HLA_C_1", "HLA_C_2"]


def _xlsx(path: Path, header: list[str], rows: list[list[str]],
          sheet_name: str = "all_results_merged") -> Path:
    """Build a minimal single-sheet xlsx with inline strings."""
    def cell(col: int, row: int, value: str) -> str:
        ref = f"{chr(ord('A') + col)}{row}"
        if value == "":
            return ""
        escaped = value.replace("&", "&amp;").replace("<", "&lt;")
        return f'<c r="{ref}" t="inlineStr"><is><t>{escaped}</t></is></c>'

    body = []
    for index, values in enumerate([header] + rows, start=1):
        cells = "".join(cell(c, index, v) for c, v in enumerate(values))
        body.append(f'<row r="{index}">{cells}</row>')
    sheet = ('<?xml version="1.0"?><worksheet '
             'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
             f'<sheetData>{"".join(body)}</sheetData></worksheet>')
    workbook = ('<?xml version="1.0"?><workbook '
                'xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                f'<sheets><sheet name="{sheet_name}" sheetId="1" r:id="rId1"/></sheets></workbook>')
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("xl/workbook.xml", workbook)
        archive.writestr("xl/worksheets/sheet1.xml", sheet)
    return path


def _row(method="arcasHLA", seq="WES", specimen="TEST_1_2", patient="TEST_1",
         a=("A*01:01:01", "A*02:01:01"), b=("B*07:02", "B*08:01"),
         c=("C*07:01", "C*07:02")) -> list[str]:
    return [method, seq, specimen, patient, a[0], a[1], b[0], b[1], c[0], c[1]]


def test_workbook_without_a_sample_identifier_is_refused(tmp_path):
    """The exact defect that made the legacy cross-modality analysis circular."""
    path = _xlsx(tmp_path / "stripped.xlsx",
                 [c for c in COLUMNS if c not in {"Patient_sample", "Patient"}],
                 [[r for i, r in enumerate(_row()) if i not in (2, 3)]])
    with pytest.raises(importer.BlockedEvidence, match="no sample identifier column"):
        importer.import_workbook(path)


def test_refusal_writes_nothing_and_exits_two(tmp_path):
    path = _xlsx(tmp_path / "stripped.xlsx",
                 [c for c in COLUMNS if c != "Patient_sample"],
                 [[r for i, r in enumerate(_row()) if i != 2]])
    out = tmp_path / "calls.tsv"
    assert importer.main([str(path), "--output", str(out)]) == 2
    assert not out.exists()


def test_caller_names_are_canonicalised_to_panel_spelling(tmp_path):
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS, [
        _row(method="arcasHLA"), _row(method="OptiType", specimen="TEST_1_3"),
        _row(method="SpecHLA", specimen="TEST_1_4"),
    ])
    calls, _ = importer.import_workbook(path)
    # Panel membership in consensus.py is an exact string match.
    assert {row["caller"] for row in calls} == {"ArcasHLA", "OptiType", "SpecHLA"}


def test_bulk_and_single_cell_rna_share_a_modality_but_not_a_cohort(tmp_path):
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS, [
        _row(seq="BulkRNA", specimen="TEST_1_2"), _row(seq="SCRNA", specimen="TEST_1_2"),
    ])
    calls, _ = importer.import_workbook(path)
    assert {row["modality"] for row in calls} == {"rnaseq"}
    # Distinct cohorts keep build_consensus from pooling the two assays into one vote.
    assert {row["cohort"] for row in calls} == {"FIMM-AML-BulkRNA", "FIMM-AML-SCRNA"}


def test_artefact_and_separate_cohort_rows_are_excluded_and_counted(tmp_path):
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS, [
        _row(), _row(specimen="align_pair", patient="align_pair"),
        _row(specimen="VX_TEST_2", patient="VX_TEST"),
    ])
    calls, flow = importer.import_workbook(path)
    counts = {row["stage"]: row["count"] for row in flow}
    assert counts["excluded_artefact_identifier"] == 1
    assert counts["excluded_separate_venex_cohort"] == 1
    assert counts["rows_imported"] == 1
    assert not any("align_pair" in row["subject"] or row["subject"].startswith("VX_")
                   for row in calls)


def test_row_conservation_is_three_loci_per_imported_row(tmp_path):
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS,
                 [_row(specimen=f"TEST_1_{i}") for i in range(5)])
    calls, flow = importer.import_workbook(path)
    counts = {row["stage"]: row["count"] for row in flow}
    assert len(calls) == counts["rows_imported"] * 3 == 15
    assert all(row["replicates"] == 1 for row in calls)


def test_agreeing_replicates_collapse_to_one_call(tmp_path):
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS, [_row(), _row()])
    calls, flow = importer.import_workbook(path)
    counts = {row["stage"]: row["count"] for row in flow}
    assert len(calls) == 3                       # one per locus, not two
    assert counts["replicate_agreements"] == 3
    assert all(row["replicates"] == 2 for row in calls)
    assert all(row["call_status"] == "callable" for row in calls)


def test_conflicting_replicates_become_a_no_call(tmp_path):
    """A caller cannot cast two votes, and picking one genotype would invent a result."""
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS, [
        _row(a=("A*01:01", "A*02:01")),
        _row(a=("A*03:01", "A*11:01")),
    ])
    calls, flow = importer.import_workbook(path)
    counts = {row["stage"]: row["count"] for row in flow}
    a_row = [row for row in calls if row["gene"] == "A"][0]
    assert a_row["call_status"] == "no_call"
    assert a_row["no_call_reason"] == "replicate_conflict"
    assert not a_row["allele1"] and not a_row["allele2"]
    assert counts["replicate_conflicts"] == 1
    # B and C agreed, so they survive as ordinary calls.
    assert all(row["call_status"] == "callable" for row in calls if row["gene"] != "A")


def test_no_match_token_is_a_no_call_not_invalid_data(tmp_path):
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS,
                 [_row(a=("no_match", "no_match"))])
    calls, flow = importer.import_workbook(path)
    a_row = [row for row in calls if row["gene"] == "A"][0]
    assert a_row["call_status"] == "missing"
    assert {row["stage"]: row["count"] for row in flow}["locus_cells_no_match_token"] == 2


def test_numeric_allele_cell_fails_rather_than_being_cleaned_away(tmp_path):
    """89 WES rows in the real workbook carry a bare integer from a column shift."""
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS, [_row(a=("525", ""))])
    calls, flow = importer.import_workbook(path)
    a_row = [row for row in calls if row["gene"] == "A"][0]
    assert a_row["call_status"] == "invalid"
    assert not a_row["allele1"]
    assert {row["stage"]: row["count"] for row in flow}["locus_cells_numeric_artefact"] == 1


def test_donor_is_carried_through_for_the_secondary_pairing(tmp_path):
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS,
                 [_row(specimen="TEST_1_2", patient="TEST_1"),
                  _row(specimen="TEST_1_5", patient="TEST_1")])
    calls, _ = importer.import_workbook(path)
    assert {row["donor"] for row in calls} == {"TEST_1"}
    assert {row["subject"] for row in calls} == {"TEST_1_2", "TEST_1_5"}


def test_alleles_are_truncated_to_two_fields(tmp_path):
    path = _xlsx(tmp_path / "w.xlsx", COLUMNS, [_row()])
    calls, _ = importer.import_workbook(path)
    for row in calls:
        for key in ("allele1", "allele2"):
            if row[key]:
                assert row[key].count(":") == 1, row
