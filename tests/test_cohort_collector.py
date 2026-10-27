from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

from champhla_confirmation.panels import GENES, PANELS

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/caller_outputs"
SCRIPT = ROOT / "scripts/collect_cohort_caller_calls.py"


def _load():
    spec = importlib.util.spec_from_file_location("collect_cohort_caller_calls", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


collector = _load()


def _cohort(tmp_path: Path, sample: str = "HG00096",
            callers: tuple[str, ...] = ("hlahd", "optitype", "polysolver", "spechla", "t1k"),
            ) -> Path:
    """Lay out <root>/<sample>/<caller>/<sample>_<caller>.txt from the repo fixtures."""
    root = tmp_path / "caller_root"
    for directory in callers:
        target = root / sample / directory
        target.mkdir(parents=True)
        shutil.copy(FIXTURES / f"HG00096_{directory}.txt",
                    target / f"{sample}_{directory}.txt")
    return root


def _read(path: Path) -> list[dict[str, str]]:
    import csv
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_every_panel_caller_gets_a_row_for_every_gene(tmp_path):
    root = _cohort(tmp_path)
    out = tmp_path / "calls.tsv"
    assert collector.main([str(root), "--cohort", "T", "--modality", "wes",
                           "--output", str(out)]) == 0
    rows = _read(out)
    panel = PANELS["wes"]
    assert len(rows) == len(panel) * len(GENES)
    assert {row["caller"] for row in rows} == set(panel)
    for caller in panel:
        assert {row["gene"] for row in rows if row["caller"] == caller} == set(GENES)


def test_a_caller_with_no_output_is_recorded_not_dropped(tmp_path):
    """SpecHLA's fixture is header-only, the real defect caller_validation was written for."""
    root = _cohort(tmp_path)
    out = tmp_path / "calls.tsv"
    validation = tmp_path / "validation.tsv"
    collector.main([str(root), "--cohort", "T", "--modality", "wes",
                    "--output", str(out), "--validation-output", str(validation)])
    spechla = [row for row in _read(out) if row["caller"] == "SpecHLA"]
    assert len(spechla) == len(GENES)
    assert all(row["call_status"] != "callable" for row in spechla)
    assert all(row["no_call_reason"] == "no_pair_in_caller_output" for row in spechla)
    assert [r for r in _read(validation) if r["caller"] == "SpecHLA"][0]["status"] == "empty"


def test_missing_caller_directory_is_recorded_as_a_no_call(tmp_path):
    root = _cohort(tmp_path, callers=("optitype", "spechla", "t1k", "hlahd"))
    out = tmp_path / "calls.tsv"
    assert collector.main([str(root), "--cohort", "T", "--modality", "wes",
                           "--output", str(out)]) == 0
    poly = [row for row in _read(out) if row["caller"] == "POLYSOLVER"]
    # POLYSOLVER is in PANELS["wes"], so it must still appear, as an explicit no-call.
    assert len(poly) == len(GENES)
    assert all(row["no_call_reason"] == "no_caller_output" for row in poly)
    assert all(row["source_path"] == "" for row in poly)


def test_hlahd_four_token_line_abstains_rather_than_guessing(tmp_path):
    """The fixture's B line carries four alleles, so no two-allele pair is resolvable."""
    root = _cohort(tmp_path)
    out = tmp_path / "calls.tsv"
    collector.main([str(root), "--cohort", "T", "--modality", "wes", "--output", str(out)])
    hlahd = {row["gene"]: row for row in _read(out) if row["caller"] == "HLA-HD"}
    assert hlahd["B"]["call_status"] != "callable"
    assert hlahd["A"]["call_status"] == "callable"
    assert hlahd["A"]["allele1"] and ":" in hlahd["A"]["allele1"]


def test_alleles_are_truncated_to_two_fields(tmp_path):
    root = _cohort(tmp_path)
    out = tmp_path / "calls.tsv"
    collector.main([str(root), "--cohort", "T", "--modality", "wes", "--output", str(out)])
    for row in _read(out):
        for key in ("allele1", "allele2"):
            if row[key]:
                assert row[key].count(":") == 1, row


def test_source_checksum_is_recorded_for_every_parsed_file(tmp_path):
    root = _cohort(tmp_path)
    out = tmp_path / "calls.tsv"
    collector.main([str(root), "--cohort", "T", "--modality", "wes", "--output", str(out)])
    for row in _read(out):
        if row["source_path"]:
            assert len(row["source_sha256"]) == 64


def test_intermediate_per_locus_files_are_not_eligible(tmp_path):
    """HLA-HD emits ~60 per-locus files per sample; picking one yields a partial genotype."""
    root = _cohort(tmp_path, callers=("optitype", "spechla", "t1k"))
    sample_dir = root / "HG00096" / "hlahd" / "HG00096" / "result"
    sample_dir.mkdir(parents=True)
    (sample_dir / "HG00096_A.est.txt").write_text("A\tHLA-A*01:01:01\tHLA-A*29:02:01\n",
                                                  encoding="utf-8")
    found = collector.find_summary(root / "HG00096", "HG00096", "hlahd")
    assert found is None


def test_unknown_modality_is_rejected(tmp_path):
    root = _cohort(tmp_path)
    with pytest.raises(SystemExit):
        collector.main([str(root), "--cohort", "T", "--modality", "scrna",
                        "--output", str(tmp_path / "x.tsv")])
