"""SR-021 regression coverage for precise P/G group compatibility reporting."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAR = ROOT / "artifacts" / "development_characterisation"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_all_methods_are_reported_for_each_set_valued_endpoint():
    sources = [
        CHAR / "ambiguity_compatibility.tsv",
        CHAR / "g_group_compatibility.tsv",
        CHAR / "p_group_compatibility.tsv",
    ]
    method_sets = []
    for source in sources:
        rows = read_tsv(source)
        method_sets.append({
            modality: {row["method"] for row in rows if row["modality"] == modality}
            for modality in ("wes", "rnaseq")
        })
    assert method_sets[0] == method_sets[1] == method_sets[2]


def test_c0202_c0210_uses_official_p_group_and_lenient_g_mapping():
    rows = read_tsv(CHAR / "reference_adjudication.tsv")
    c02_rows = [
        row for row in rows
        if "C*02:02" in row["reference"] and "C*02:10" in row["consensus"]
    ]
    assert c02_rows
    assert all(row["g_compatible_under_two_field_mapping"] == "1" for row in c02_rows)
    assert all(row["p_group_equivalent_to_reference"] == "1" for row in c02_rows)


def test_reader_facing_files_use_precise_group_language_and_registry_endpoints():
    manuscript = (ROOT / "manuscripts/benchmark/manuscript.md").read_text(encoding="utf-8")
    supplement = (ROOT / "manuscripts/benchmark/supplementary.md").read_text(encoding="utf-8")
    active = manuscript + "\n" + supplement
    assert "G-equivalent" not in active
    assert "G-compatible under a two-field mapping" in active
    assert "P-group-compatible under a two-field mapping" in active

    registry = read_tsv(ROOT / "result_registry.tsv")
    endpoints = {row["endpoint"] for row in registry}
    assert "g_compatible_under_two_field_mapping_ipd_3_65" in endpoints
    assert "p_group_compatible_under_two_field_mapping_ipd_3_65" in endpoints
