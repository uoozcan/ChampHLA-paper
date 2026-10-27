"""NCI-60 regeneration (decisions/20261026_nci60_v350_regeneration.json): the fail-closed
Adams 2005 parser, the truth-free manifest and the runner's paired-FASTQ route."""
from __future__ import annotations

import csv
import importlib.util
import re
from pathlib import Path

import pytest

from champhla_recovery.nci60 import (
    build_truth, cross_check, parse_cell, parse_token, sample_id, sample_key,
)

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "resources/nci60"
ALLELES = {"A*02:01", "A*24:02", "B*07:02"}


@pytest.mark.parametrize("token, expected", [
    ("0201", ("A*02:01", "")),
    ("020101", ("A*02:01", "")),
    ("02011", ("A*02:01", "")),      # 2005 form: four digits plus a synonymous digit
    ("02a", ("", "unresolved_two_digit_ambiguity")),
    ("0101new", ("", "new_allele")),
    ("03", ("", "unrecognised_token:03")),
    ("A*02:01", ("", "unrecognised_token:A*02:01")),
])
def test_tokens_are_parsed_or_excluded_never_guessed(token, expected):
    assert parse_token(token, "A") == expected


def test_cells_follow_the_signed_rules():
    assert parse_cell("0201, 2402", "A", ALLELES) == {
        "truth_state": "resolved", "allele1": "A*02:01", "allele2": "A*24:02",
        "single_allele": "0", "exclusion_reason": ""}
    single = parse_cell("020101", "A", ALLELES)
    assert (single["allele1"], single["allele2"], single["single_allele"]) == (
        "A*02:01", "A*02:01", "1")
    assert parse_cell("N.R.", "A", ALLELES)["exclusion_reason"] == "not_resolved"
    assert parse_cell("0201, 24a", "A", ALLELES)["truth_state"] == "excluded"
    assert parse_cell("0201, 2402, 0301", "A", ALLELES)["exclusion_reason"].startswith(
        "malformed_cell")
    assert parse_cell("1010", "A", ALLELES)["exclusion_reason"] == "not_in_ipd_3_65_0:A*10:10"


def test_tabulation_must_match_the_article_table():
    raw = {"X": {"A locus": "0201", "B Locus": "0702", "Cw Locus": "07a"}}
    xml = {"X": {"A locus": "0201", "B Locus": "0702", "Cw Locus": "07a"}}
    cross_check(raw, xml)
    xml["X"]["B Locus"] = "0801"
    with pytest.raises(ValueError, match="tabulation"):
        cross_check(raw, xml)


def test_name_keys_join_the_archive_spellings():
    assert sample_key("786-O") == sample_key("786-0")
    assert sample_key("A549/ATCC") == sample_key("A549-ATCC")
    assert sample_key("LOX IMVI") == sample_key("LOX_IMVI")
    assert sample_id("NCI/ADR-RES") == "NCI60_NCIADRRES"


def test_real_table_cross_checks_and_every_locus_has_a_state():
    rows = build_truth(RESOURCES / "nci60_classI_raw.tsv", RESOURCES / "adams2005_PMC555742.xml",
                       ROOT / "resources/ipd_imgt_hla/3.65.0/Allelelist.txt")
    assert len(rows) == 58 * 3
    assert {row["truth_state"] for row in rows} == {"resolved", "excluded"}
    assert all(row["exclusion_reason"] for row in rows if row["truth_state"] == "excluded")
    assert all(row["allele1"] and row["allele2"] for row in rows if row["truth_state"] == "resolved")


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_committed_manifest_is_reproducible_and_truth_free(tmp_path):
    builder = _module("build_nci60_manifest")
    assert builder.main(["--output-tsv", str(tmp_path / "m.tsv"), "--map-tsv",
                         str(tmp_path / "map.tsv"), "--output-json", str(tmp_path / "m.json")]) == 0
    assert (tmp_path / "m.tsv").read_bytes() == (ROOT / "cohorts/nci60_v350_manifest.tsv").read_bytes()
    with (ROOT / "cohorts/nci60_v350_manifest.tsv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    counts = {m: sum(r["modality"] == m for r in rows) for m in ("wes", "rnaseq")}
    assert counts == {"wes": 57, "rnaseq": 58}
    assert "NCI60_UO31" not in {r["sample_id"] for r in rows if r["modality"] == "wes"}
    assert all(re.fullmatch(r"NCI60_[A-Z0-9]+", r["sample_id"]) for r in rows)
    assert all(r["input_format"] == "FASTQ" and r["source_input_md5"] and r["source_index_md5"]
               for r in rows)
    assert {(r["subsample_pairs"], r["subsample_seed"]) for r in rows if r["modality"] == "rnaseq"} == {
        ("50000000", "100")}
    assert not any("allele" in field.lower() for field in rows[0])


def test_runner_supports_paired_fastq_and_declares_polysolver_non_call():
    text = (ROOT / "scripts/roihu_run_development_sample.sbatch").read_text(encoding="utf-8")
    assert "NCI60_[A-Z0-9]+" in text
    assert "sample_id,fastq_1,fastq_2" in text
    assert 'seqtk sample -s"${subsample_seed}"' in text
    assert "none:none" in text
    assert "declared_non_call_fastq_input" in text
    # BAM/CRAM header and assembly checks still guard the 1000 Genomes inputs.
    assert 'samtools quickcheck -v "${input_path}"' in text
    assert "GRCh38DH:GRCh38|GRCh38:GRCh38|GRCh37:GRCh37" in text
