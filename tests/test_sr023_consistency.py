from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "manuscripts" / "benchmark" / "manuscript.md"
SUPPLEMENT = ROOT / "manuscripts" / "benchmark" / "supplementary.md"


def rows(path: Path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_identity_counts_distinguish_pre_and_post_withholding():
    text = MAIN.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    manifest = ROOT / "data" / "development" / "input_manifest.json"
    if json.loads(manifest.read_text(encoding="utf-8")).get(
            "schema_version") == "champhla-development-rerun-inputs-1":
        # v3.5.0 rerun roster: NA07000 RNA-seq is excluded; its withholding is historical
        assert "106 RNA-seq subjects (318 loci), 105 of whom also occurred in the WES roster" in flat
        assert "101 subjects shared all six alleles and four shared five" in flat
        assert "the analysed sample list excludes it" in flat
        assert "including them gave 113/120 (Supplementary S7, analysis-choice summary)" in flat
        return
    assert "Before identity withholding, all 106 RNA-seq subjects" in flat
    assert "105 remained in both after NA07000 RNA-seq was withheld" in flat
    assert "97 subjects shared all six alleles, seven shared five, one shared four" in flat
    assert "give 113/120 (Supplementary S7, analysis-choice summary)" in flat


def test_phi_bootstrap_count_is_consistent():
    correlation = rows(ROOT / "artifacts/development_characterisation/caller_error_correlation.tsv")
    assert {r["error_phi_bootstrap_iterations"] for r in correlation} == {"100000"}
    text = SUPPLEMENT.read_text(encoding="utf-8")
    assert "percentile bootstrap intervals (100,000 resamples)" in text
    assert "percentile bootstrap intervals (10,000 resamples)" not in text


def test_fully_callable_methods_share_identical_intervals():
    for row in rows(ROOT / "artifacts/development_corrected/method_performance.tsv"):
        if row["callable"] == row["loci"]:
            assert row["called_only_ci_lo"] == row["genotype_ci_lo"], row["method"]
            assert row["called_only_ci_hi"] == row["genotype_ci_hi"], row["method"]


def test_s12_uses_exact_intervals_and_explains_calibration_denominator():
    discordance = rows(ROOT / "artifacts/restored_analyses/discordance_taxonomy.tsv")
    assert {r["interval_method"] for r in discordance} == {"clopper_pearson_exact"}
    calibration = rows(ROOT / "artifacts/restored_analyses/caller_calibration.tsv")
    hla_hd = next(r for r in calibration if r["assay"] == "rnaseq" and r["caller"] == "HLA-HD")
    assert (hla_hd["scored_loci"], hla_hd["callable_loci"]) == ("109", "115")
    assert hla_hd["note"] == "6 callable loci lacked a preserved calibrated probability"
    section = SUPPLEMENT.read_text(encoding="utf-8").split("## S12.", 1)[1]
    assert "Intervals are exact Clopper–Pearson 95% intervals" in section
    assert "six of 115 callable HLA-HD RNA-seq loci" in section
    assert "| RNA-seq | HLA-HD | 109/115 |" in section


def test_main_table_collapses_identical_rnaseq_threshold_rules():
    text = MAIN.read_text(encoding="utf-8")
    block = text.split("<!-- BEGIN GENERATED MAIN TABLE -->", 1)[1].split(
        "<!-- END GENERATED MAIN TABLE -->", 1
    )[0]
    assert "| RNA-seq | Strict majority |" in block
    assert "| RNA-seq | Two-thirds consensus |" not in block
    assert "strict majority and\ntwo-thirds consensus are mathematically identical" in block


def test_fimm_locus_row_units_are_explicit():
    """SR-023 (8): the 7,179 rows are caller-level, the composition table counts
    specimen-assay-gene loci; the text must name both units."""
    text = " ".join((MAIN.read_text(encoding="utf-8")
                     + SUPPLEMENT.read_text(encoding="utf-8")).split())
    if "7,179" in text:
        assert "7,179 caller-level locus rows (one per specimen, assay, caller and gene)" in text
        assert "one specimen–assay–gene locus" in text
    assert "4,416" not in text
