"""Publication and data-contract tests for the restructured figure set."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
GENERATOR = ROOT / "scripts" / "generate_figures.py"
MANIFEST = FIGURES / "figure_manifest.json"
MAIN_NAMES = (
    "figure1_study_design_truth_flow",
    "figure2_primary_performance",
    "figure3_paired_differences",
    "figure4_caller_error_dependence",
)
SUPPLEMENTARY_NAMES = (
    "supplementary_figure_s1_call_states",
    "supplementary_figure_s2_threshold_tradeoff",
    "supplementary_figure_s3_support_profiles",
    "supplementary_figure_s4_truth_sensitivity",
    "supplementary_figure_s5_champion_challenger",
)
# decisions/20261105_patient_cohorts_removed.json removed the three cohort figures.
EXPLORATORY_NAMES = ()
# Supplementary Figure S6 is generated only from the v3.5.0 rerun cell ledger.
RERUN_LEDGER = ROOT / "provenance/development_rerun_v350/truth_free_collection/stored_vs_rerun_cells.tsv"
RERUN_NAMES = (
    ("supplementary_figure_s6_rerun_cell_changes",) if RERUN_LEDGER.is_file() else ()
)
SUPPLEMENTARY_NAMES += RERUN_NAMES
NAMES = MAIN_NAMES + SUPPLEMENTARY_NAMES
LEGACY_NAMES = NAMES
MANIFEST_ORDER = MAIN_NAMES + SUPPLEMENTARY_NAMES[:5] + EXPLORATORY_NAMES + RERUN_NAMES
MAGENTA = "#AA3377"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest() -> dict:
    if not MANIFEST.is_file():
        pytest.skip("figure manifest not generated")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _figure(figure_id: str) -> dict:
    return next(item for item in _manifest()["figures"] if item["figure_id"] == figure_id)


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


@pytest.mark.parametrize("name", MANIFEST_ORDER)
def test_no_type3_font(name: str):
    path = FIGURES / f"{name}.pdf"
    if not path.is_file():
        pytest.skip("figure not generated")
    assert b"/Type3" not in path.read_bytes()


@pytest.mark.parametrize("name", MANIFEST_ORDER)
def test_font_is_embedded(name: str):
    path = FIGURES / f"{name}.pdf"
    if not path.is_file():
        pytest.skip("figure not generated")
    assert b"/FontFile2" in path.read_bytes()


def test_generator_pins_truetype_output():
    text = GENERATOR.read_text(encoding="utf-8")
    assert '"pdf.fonttype": 42' in text
    assert '"ps.fonttype": 42' in text


def test_generator_never_sets_text_below_seven_points():
    text = GENERATOR.read_text(encoding="utf-8")
    explicit_sizes = [float(value) for value in re.findall(r"fontsize=(\d+(?:\.\d+)?)", text)]
    assert explicit_sizes
    assert min(explicit_sizes) >= 7


def test_every_figure_ships_vector_and_raster():
    for name in EXPLORATORY_NAMES:
        for suffix in ("pdf", "svg", "png"):
            path = FIGURES / f"{name}.{suffix}"
            assert path.is_file() and path.stat().st_size > 0
    for name in NAMES:
        for suffix in ("pdf", "svg", "png", "tiff"):
            path = FIGURES / f"{name}.{suffix}"
            assert path.is_file() and path.stat().st_size > 0


def test_tiffs_are_lzw_compressed_to_submission_size():
    for name in LEGACY_NAMES:
        path = FIGURES / f"{name}.tiff"
        assert path.stat().st_size < 12 * 1024 * 1024, f"{name}.tiff appears uncompressed"


def test_error_matrix_pdf_remains_vector_sized():
    path = FIGURES / "figure4_caller_error_dependence.pdf"
    assert path.stat().st_size < 1024 * 1024, "error matrix was rasterized into the PDF"


def test_manifest_is_complete_and_hashes_every_source_and_output():
    manifest = _manifest()
    assert manifest["schema_version"] == "panelhla-figure-manifest-1"
    assert [item["figure_id"] for item in manifest["figures"]] == [
        "Figure 1", "Figure 2", "Figure 3", "Figure 4",
        "Supplementary Figure S1", "Supplementary Figure S2",
        "Supplementary Figure S3", "Supplementary Figure S4",
        "Supplementary Figure S5",
    ] + (["Supplementary Figure S6"] if RERUN_LEDGER.is_file() else [])
    for source in manifest["source_artifacts"].values():
        assert _sha256(ROOT / source["path"]) == source["sha256"]
    for name, item in zip(MANIFEST_ORDER, manifest["figures"], strict=True):
        for suffix, expected in item["output_sha256"].items():
            assert _sha256(FIGURES / f"{name}.{suffix}") == expected


def test_style_contract_and_all_percentage_axes_stop_at_100():
    manifest = _manifest()
    style = manifest["style_contract"]
    assert style["main_width_mm"] == 180
    assert style["minimum_font_points"] >= 7
    assert style["percentage_upper_bound"] == 100
    assert style["significance_colour"] == MAGENTA
    assert style["exploratory_formats"] == ["pdf", "svg", "png"]
    assert style["exploratory_raster_dpi"] == 300
    assert style["render_profiles"]["exploratory_300dpi_three_format"] == {
        "formats": ["pdf", "svg", "png"], "raster_dpi": 300,
    }
    for item in manifest["figures"]:
        for key, limits in item["axis_limits"].items():
            if key in {"concordance", "callability", "percentage"}:
                assert limits[-1] == 100
            if key == "percentage_upper":
                assert limits == 100


def test_all_figures_use_publication_render_profile():
    """Every remaining figure is publication-grade."""
    for item in _manifest()["figures"]:
        assert item["render_profile"] == "publication_600dpi_four_format"
        assert set(item["output_sha256"]) == {"pdf", "svg", "png", "tiff"}

def test_figure1_flow_counts_are_generated_from_truth_flow():
    rows = _rows(ROOT / "artifacts/development_characterisation/truth_flow.tsv")
    figure = _figure("Figure 1")
    for modality in ("wes", "rnaseq"):
        assay = [row for row in rows if row["modality"] == modality]
        expected = {row["truth_state"]: int(row["loci"]) for row in assay}
        expected["requested"] = int(assay[0]["requested_loci"])
        expected["truth_source_present"] = expected["requested"] - expected["absent"]
        assert figure["flow_counts"][modality] == expected


def test_figure2_has_both_metrics_counts_and_fixed_role_order():
    figure = _figure("Figure 2")
    assert figure["metrics"] == ["genotype_accuracy", "callability"]
    assert figure["count_columns"] == ["genotypes_correct/loci", "callable/loci"]
    for modality, methods in figure["displayed_methods"].items():
        assert methods[:2] == ["SimplePluralityLex", "BestSingleTool_nestedCV"]
        callers = [method.split(":", 1)[-1] for method in methods[2:]]
        assert callers == sorted(callers), modality


def test_figure3_contains_only_applicable_source_rows_in_family_order():
    rows = _rows(ROOT / "artifacts/development_corrected/secondary_method_results.tsv")
    figure = _figure("Figure 3")
    assert figure["right_columns"] == ["wins/losses", "signflip_holm_adjusted_p"]
    assert figure["significance_colour"] == MAGENTA
    for modality in ("wes", "rnaseq"):
        plotted = figure["displayed_methods"][modality]
        assert all(plotted[family] for family in plotted)
        flattened = {method for methods in plotted.values() for method in methods}
        source = {row["comparator"] for row in rows if row["modality"] == modality}
        assert flattened == source


FIGURE3_LEGEND_NAMES = {
    "SimpleStrictMajority": "strict-majority",
    "SimpleTwoThirdsConsensus": "two-thirds consensus",
}


def _disclosed_in_figure3_legend(modality: str, comparator: str) -> bool:
    text = (ROOT / "manuscripts/benchmark/manuscript.md").read_text(encoding="utf-8")
    legend = text.split("**Figure 3.", 1)[1].split("**Figure 4.", 1)[0]
    assay = {"wes": "WES", "rnaseq": "RNA-seq"}[modality]
    return any(assay in line and FIGURE3_LEGEND_NAMES.get(comparator, comparator) in line
               and "governing sign-flip test" in line for line in legend.splitlines())


def test_adjusted_interval_significance_is_coherent_with_holm():
    rows = _rows(ROOT / "artifacts/development_corrected/secondary_method_results.tsv")
    for row in rows:
        lower = float(row["simultaneous_ci_lo_points"])
        upper = float(row["simultaneous_ci_hi_points"])
        excludes_zero = lower > 0 or upper < 0
        # decisions/20261009_signflip_governs.json: the subject sign-flip test governs
        # significance and Figure 3 marks it. The CR1 cluster-t is a sensitivity test;
        # Holm's step-down can call it significant while the single-step simultaneous
        # interval still covers zero (v3.5.0 rerun, WES versus two-thirds consensus).
        if excludes_zero != (row["signflip_holm_significant"] == "1"):
            # A disagreement is allowed only for a descriptive comparator whose bar excludes
            # zero while the governing test is nonsignificant, and the legend must say so.
            assert row["inference_family"] == "descriptive_comparator"
            assert excludes_zero and row["signflip_holm_significant"] == "0"
            assert _disclosed_in_figure3_legend(row["modality"], row["comparator"])
        if int(row["wins"]) == int(row["losses"]) == 0:
            assert float(row["delta_points"]) == 0
            assert lower == upper == 0
            assert float(row["holm_adjusted_p"]) == 1


def test_figure4_reproduces_both_error_correlation_definitions():
    rows = _rows(ROOT / "artifacts/development_characterisation/caller_error_correlation.tsv")
    figure = _figure("Figure 4")
    for modality in ("wes", "rnaseq"):
        observed = figure["matrix_values"][modality]
        expected = [
            {
                "caller1": row["caller1"], "caller2": row["caller2"],
                "fixed_denominator_phi": float(row["error_phi"]),
                "mutually_callable_phi": float(row["mutually_callable_error_phi"]),
            }
            for row in rows if row["modality"] == modality
        ]
        assert observed == expected
        assert all(0 <= value <= 1 for item in observed
                   for value in (item["fixed_denominator_phi"], item["mutually_callable_phi"]))


def test_s1_call_state_counts_partition_each_denominator():
    figure = _figure("Supplementary Figure S1")
    for modality in ("wes", "rnaseq"):
        for row in figure["state_counts"][modality]:
            assert sum(row[state] for state in
                       ("callable", "partial", "missing", "absent", "invalid")) == row["loci"]


def test_s2_coincident_rnaseq_thresholds_are_explicit_and_not_jittered():
    figure = _figure("Supplementary Figure S2")
    assert figure["identical_points_not_jittered"] is True
    points = {row["method"]: row for row in figure["threshold_points"]["rnaseq"]}
    strict = points["SimpleStrictMajority"]
    two_thirds = points["SimpleTwoThirdsConsensus"]
    assert strict["callability"] == two_thirds["callability"]
    assert strict["concordance"] == two_thirds["concordance"]
    source = GENERATOR.read_text(encoding="utf-8")
    assert 'xytext=(0, -17)' in source
    assert 'va="top"' in source


def test_s3_suppresses_every_sparse_profile_and_keeps_zero_support_off_scale():
    rows = _rows(ROOT / "artifacts/development_characterisation/support_stratified_concordance.tsv")
    contract = _figure("Supplementary Figure S3")["profile_contract"]
    for modality in ("wes", "rnaseq"):
        assay = [row for row in rows if row["modality"] == modality]
        expected_shown = {row["support_profile"] for row in assay
                          if row["support_defined"] == "1" and int(row["loci"]) >= 5}
        expected_suppressed = {row["support_profile"] for row in assay
                               if row["support_defined"] == "1" and int(row["loci"]) < 5}
        expected_outside = {row["support_profile"] for row in assay
                            if row["support_defined"] == "0"}
        assert set(contract[modality]["displayed"]) == expected_shown
        assert set(contract[modality]["suppressed"]) == expected_suppressed
        assert set(contract[modality]["outside_scale"]) == expected_outside
        assert not (expected_shown & expected_suppressed)
    assert _figure("Supplementary Figure S3")["zero_support_outside_scale"] is True


def test_s4_keeps_truth_endpoints_separate_and_records_denominators():
    figure = _figure("Supplementary Figure S4")
    assert figure["different_denominators_not_connected"] is True
    assert figure["endpoint_display_titles"] == {
        "Exact two-field": "Exact\ntwo-field",
        "Ambiguity-compatible": "Ambiguity-\ncompatible",
        "G-compatible (two-field mapping)": "G-compatible\n(two-field map)",
        "P-group-compatible (two-field mapping)": "P-compatible\n(two-field map)",
    }
    assert all(max(map(len, title.splitlines())) <= 16
               for title in figure["endpoint_display_titles"].values())
    expected = {
        "wes": {
            "Exact two-field": [153],
            "Ambiguity-compatible": [335],
            "G-compatible (two-field mapping)": [333],
            "P-group-compatible (two-field mapping)": [333],
        },
        "rnaseq": {
            "Exact two-field": [118],
            "Ambiguity-compatible": [263],
            "G-compatible (two-field mapping)": [261],
            "P-group-compatible (two-field mapping)": [261],
        },
    }
    for modality, endpoints in expected.items():
        for endpoint, denominators in endpoints.items():
            assert figure["endpoint_contract"][modality][endpoint]["denominators"] == denominators


def test_s5_is_the_non_patient_champion_challenger_flow():
    figure = _figure("Supplementary Figure S5")
    assert figure["caption_key"] == "champion_challenger_flow"
    assert figure["panels"] == ["decision_flow"]
    assert "result_ids" not in figure

def test_magenta_is_reserved_for_significance():
    text = GENERATOR.read_text(encoding="utf-8")
    assert text.count(MAGENTA) == 1, "literal significance colour used outside its definition"
    assert 'colour = MAGENTA if significant else GREY' in text
    assert text.count("MAGENTA") == 4, "significance colour is used outside its contract"


def test_no_figure_hardcodes_a_whole_genome_rate():
    text = GENERATOR.read_text(encoding="utf-8")
    code = "\n".join(line for line in text.splitlines()
                     if not line.strip().startswith("#"))
    for banned in ("80.4", "17.0", "0.399", "0.494"):
        assert banned not in code


def test_assay_order_and_display_spelling_are_consistent():
    text = GENERATOR.read_text(encoding="utf-8")
    assert 'ASSAYS = ("wes", "rnaseq")' in text
    assert '("rnaseq", "wes")' not in text
    assert '"ArcasHLA": "arcasHLA"' in text
    for name in ("manuscript", "supplementary"):
        body = (ROOT / "manuscripts" / "benchmark" / f"{name}.md").read_text(
            encoding="utf-8")
        assert "ArcasHLA" not in body
