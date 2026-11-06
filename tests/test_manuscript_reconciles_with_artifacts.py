"""Generated manuscript tables and active claims must match corrected artifacts."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscripts" / "benchmark" / "manuscript.md"
SUPPLEMENT = ROOT / "manuscripts" / "benchmark" / "supplementary.md"
GENERATOR = ROOT / "scripts" / "generate_manuscript_tables.py"


def load_generator():
    spec = importlib.util.spec_from_file_location("generated_tables", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def block(text: str, name: str) -> str:
    match = re.search(
        rf"<!-- BEGIN GENERATED {re.escape(name)} -->\n(.*?)\n<!-- END GENERATED {re.escape(name)} -->",
        text, re.S,
    )
    assert match, f"missing generated block {name}"
    return match.group(1)


def test_main_table_is_exact_generator_output():
    module = load_generator()
    rows = module.read(ROOT / "artifacts" / "development_corrected" / "method_performance.tsv")
    # The generator prints the corrected-reference column beside the exact endpoint
    # (decisions/20261013_corrected_reference_presentation.json) when it exists.
    sensitivity = ROOT / "artifacts" / "development_characterisation" / "reference_agreement_sensitivity.tsv"
    reference = module.read(sensitivity) if sensitivity.is_file() else None
    p_group = ROOT / "artifacts" / "development_characterisation" / "exact_locus_p_group_agreement_posthoc.tsv"
    assert block(MANUSCRIPT.read_text(encoding="utf-8"), "MAIN TABLE") == module.main_table(
        rows, reference, module.read(p_group) if p_group.is_file() else None)


def test_supplement_tables_are_exact_generator_outputs():
    module = load_generator()
    corrected = ROOT / "artifacts" / "development_corrected"
    characterised = ROOT / "artifacts" / "development_characterisation"
    expected = {
        "COHORT TABLE": module.cohort_table(module.read(characterised / "cohort_summary.tsv")),
        "TRUTH FLOW TABLE": module.truth_flow_table(module.read(characterised / "truth_flow.tsv")),
        "EXCLUSION TABLE": module.exclusion_table(
            module.read(characterised / "truth_exclusion_by_gene_population.tsv")
        ),
        "COMPATIBILITY TABLE": module.compatibility_table(
            module.read(characterised / "ambiguity_compatibility.tsv"),
            module.read(characterised / "g_group_compatibility.tsv"),
            module.read(characterised / "p_group_compatibility.tsv"),
        ),
        "PERFORMANCE TABLE": module.performance_table(module.read(corrected / "method_performance.tsv")),
        "COMPARISON TABLE": module.comparison_table(module.read(corrected / "secondary_method_results.tsv")),
        "DETECTABILITY TABLE": module.detectability_table(
            module.read(ROOT / "artifacts" / "development_limits" / "detectability.tsv")
        ),
        "TRUTH SELECTION TABLE": module.truth_selection_table(
            module.read(characterised / "truth_selection_compatibility.tsv")
        ),
        "TRUTH SELECTION PROFILE TABLE": module.truth_selection_profile_table(
            module.read(characterised / "truth_selection_profile.tsv")
        ),
        "FAMILY SENSITIVITY TABLE": module.family_sensitivity_table(
            module.read(corrected / "secondary_method_results.tsv")
        ),
        "ADJUDICATION TABLE": module.adjudication_table(
            module.read(characterised / "reference_adjudication.tsv"),
            module.read(characterised / "reference_adjudication_flagged_loci_posthoc.tsv"),
        ),
        "REFERENCE AGREEMENT TABLE": module.reference_agreement_table(
            module.read(characterised / "reference_agreement_sensitivity.tsv")
        ),
        "FLAGGED LOCI EVIDENCE TABLE": module.flagged_loci_evidence_table(
            module.read(characterised / "flagged_loci_evidence_posthoc.tsv")
        ),
        "LEAVE ONE CALLER OUT TABLE": module.leave_one_caller_out_table(
            module.read(characterised / "leave_one_caller_out_posthoc.tsv")
        ),
        "REFERENCE SUBSTITUTION TABLE": module.reference_substitution_table(
            module.read(characterised / "reference_substitution_posthoc.tsv")
        ),
        "REFERENCE AGREEMENT PHI TABLE": module.reference_agreement_phi_table(
            module.read(characterised / "reference_agreement_error_phi.tsv"),
            module.read(characterised / "caller_error_correlation.tsv"),
        ),
        "REFERENCE AGREEMENT CORRECTION TABLE": module.reference_agreement_correction_table(
            module.read(characterised / "reference_agreement_vote_correction.tsv")
        ),
        "STRATIFIED TABLE": module.stratified_table(module.read(characterised / "stratified_primary_results.tsv")),
        "MISSINGNESS TABLE": module.missingness_table(module.read(characterised / "caller_missingness.tsv")),
        "SUPPORT TABLE": module.support_table(module.read(characterised / "support_stratified_concordance.tsv")),
        "CORRELATION TABLE": module.correlation_table(
            module.read(characterised / "caller_error_correlation.tsv")
        ),
        "COMPUTE SMOKE TABLE": module.compute_smoke_table(
            module.read(ROOT / "artifacts" / "compute_smoke_benchmark.tsv")
        ),
    }
    text = SUPPLEMENT.read_text(encoding="utf-8")
    for name, generated in expected.items():
        assert block(text, name) == generated


def test_no_quantitative_wgs_result_or_invalid_headline_is_active():
    text = MANUSCRIPT.read_text(encoding="utf-8") + SUPPLEMENT.read_text(encoding="utf-8")
    for value in ("365/390", "306/321", "364/390", "303/321", "79/411", "205/411"):
        assert value not in text
    for directory in (ROOT / "artifacts" / "development_corrected",
                      ROOT / "artifacts" / "development_characterisation",
                      ROOT / "artifacts" / "development_limits"):
        for path in directory.glob("*.tsv"):
            assert "\twgs\t" not in f"\n{path.read_text(encoding='utf-8')}\n"


def test_compute_smoke_claims_preserve_actual_input_and_scope():
    text = MANUSCRIPT.read_text(encoding="utf-8") + SUPPLEMENT.read_text(encoding="utf-8")
    normalised = " ".join(text.split())
    assert "WGS-derived mate-aware HLA BAM" in normalised
    assert "does not estimate WES runtime" in normalised
    assert "not monetary" in normalised
    assert "resource use of that run remain unavailable" in normalised


def test_every_cited_repository_path_exists():
    pattern = re.compile(r"`([a-zA-Z_][a-zA-Z0-9_./-]*/[a-zA-Z0-9_./-]+)`")
    missing = []
    for document in (MANUSCRIPT, SUPPLEMENT):
        for cited in sorted(set(pattern.findall(document.read_text(encoding="utf-8")))):
            if not (ROOT / cited).exists():
                missing.append(f"{document.name}: {cited}")
    assert missing == []
