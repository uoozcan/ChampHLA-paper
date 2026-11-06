"""Generate the active result registry from corrected development artifacts."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "artifacts" / "development_corrected" / "method_performance.tsv"
PAIRED = ROOT / "artifacts" / "development_corrected" / "secondary_method_results.tsv"
HG00096_RERUN = ROOT / "artifacts" / "development_characterisation" / "hg00096_rerun_comparison.tsv"
HG00096_RELEASES = (ROOT / "artifacts" / "development_characterisation"
                    / "hg00096_wes_release_comparison.tsv")
HG00096_RNA_RELEASE = (ROOT / "artifacts" / "development_characterisation"
                       / "hg00096_rna_release_comparison.tsv")
FROZEN_NESTEDCV = ROOT / "artifacts" / "development_corrected" / "frozen_nestedcv_legacy.tsv"
IDENTITY = ROOT / "artifacts" / "development_characterisation" / "identity_check.tsv"
IDENTITY_EFFECT = (ROOT / "artifacts" / "development_characterisation"
                   / "identity_withheld_effect.tsv")
SINGLETON_SOURCE = ROOT / "artifacts" / "development_sensitivity_abstain" / "method_performance.tsv"
SINGLETON_PAIRED = (ROOT / "artifacts" / "development_sensitivity_abstain"
                    / "secondary_method_results.tsv")
AMBIGUITY = ROOT / "artifacts" / "development_characterisation" / "ambiguity_compatibility.tsv"
AMBIGUITY_PAIRED = ROOT / "artifacts" / "development_characterisation" / "ambiguity_paired_results.tsv"
G_GROUP = ROOT / "artifacts" / "development_characterisation" / "g_group_compatibility.tsv"
P_GROUP = ROOT / "artifacts" / "development_characterisation" / "p_group_compatibility.tsv"
PROTOCOL_LEDGER = ROOT / "artifacts" / "protocol_change_ledger.tsv"
REPRESENTABILITY = ROOT / "artifacts" / "development_characterisation" / "caller_truth_representability_summary.tsv"
MUTUALLY_AVAILABLE = (
    ROOT / "artifacts" / "development_characterisation"
    / "caller_mutually_available_comparison.tsv"
)
OUTPUT = ROOT / "result_registry.tsv"
DECISION = ROOT / "decisions" / "20260924_publication_remediation.json"
COMPUTE = ROOT / "artifacts" / "compute_smoke_benchmark.tsv"
SCHEMA = "panelhla-result-registry-4"
RESTORED = ROOT / "artifacts" / "restored_analyses"
LIMITS = ROOT / "artifacts" / "development_limits"
ERROR_PHI = ROOT / "artifacts" / "development_characterisation" / "caller_error_correlation.tsv"
SELECTION = ROOT / "artifacts" / "development_characterisation" / "truth_selection_compatibility.tsv"
TIE_BREAK = ROOT / "artifacts" / "development_characterisation" / "tie_break_sensitivity.tsv"
SINGLE_ALLELE = ROOT / "artifacts" / "development_characterisation" / "single_allele_zygosity.tsv"
ADJUDICATION = ROOT / "artifacts" / "development_characterisation"
NOMENCLATURE = (ROOT / "artifacts" / "development_characterisation"
                / "nomenclature_discordance_audit.tsv")
SELECTION_PROFILE = (ROOT / "artifacts" / "development_characterisation"
                     / "truth_selection_profile.tsv")
TRUTH_EXCLUSION = (ROOT / "artifacts" / "development_characterisation"
                   / "truth_exclusion_by_gene_population.tsv")
FIELDS = [
    "result_id", "record_type", "cohort", "modality", "method", "analysis_status", "validity",
    "subjects", "loci", "correct", "accuracy", "artifact_path", "artifact_sha256",
    "abstract_allowed", "claim_boundary",
    "schema_version", "endpoint", "intended_denominator", "acquired_denominator",
    "truth_evaluable_denominator", "callable_denominator", "ci_lo", "ci_hi",
    "interval_method", "raw_p", "adjusted_p", "sensitivity_adjusted_p",
    "inference_family", "family_size", "fitted_status", "development_status",
    "workflow_session", "workflow_commit", "resource_record_count",
    "result_kind", "estimate", "ci_low", "ci_high", "unit", "events",
    "source_artifact_sha256",
]


def sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def slug(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def genotype_interval_method(row: dict[str, str]) -> str:
    """The genotype interval's method: exact Clopper-Pearson where the estimate is
    0% or 100% (evaluation._boundary_safe), otherwise the stated bootstrap."""
    boundary = (row.get("boundary_intervals") or "").split(",")
    return "clopper_pearson_exact" if "genotype" in boundary else row["interval_method"]

def exploratory_row(
    *, result_id: str, cohort: str, modality: str, method: str,
    analysis_status: str, endpoint: str, artifact: Path, result_kind: str,
    estimate: str = "", ci_low: str = "", ci_high: str = "", unit: str = "",
    subjects: str = "", loci: str = "", correct: str = "",
    intended: str = "", acquired: str = "", callable_n: str = "",
    interval_method: str = "", claim_boundary: str,
) -> dict[str, str]:
    artifact_hash = sha256(artifact)
    return {
        "result_id": result_id, "record_type": "scientific_result",
        "cohort": cohort, "modality": modality, "method": method,
        "analysis_status": analysis_status, "validity": "valid",
        "subjects": subjects, "loci": loci, "correct": correct, "accuracy": "",
        "artifact_path": artifact.relative_to(ROOT).as_posix(),
        "artifact_sha256": artifact_hash, "abstract_allowed": "0",
        "claim_boundary": claim_boundary, "schema_version": SCHEMA,
        "endpoint": endpoint, "intended_denominator": intended,
        "acquired_denominator": acquired, "truth_evaluable_denominator": "",
        "callable_denominator": callable_n, "ci_lo": ci_low, "ci_hi": ci_high,
        "interval_method": interval_method, "raw_p": "", "adjusted_p": "",
        "sensitivity_adjusted_p": "", "inference_family": "",
        "family_size": "", "fitted_status": "not_fitted",
        "development_status": "post_hoc_exploratory",
        "workflow_session": "", "workflow_commit": "",
        "resource_record_count": "", "source_artifact_sha256": artifact_hash,
        "result_kind": result_kind, "estimate": estimate, "ci_low": ci_low,
        "ci_high": ci_high, "unit": unit, "events": "",
    }


def append_restored_rows(rows: list[dict[str, str]]) -> None:
    """Register the analyses restored from the earlier drafts (gap review B1-B4).

    The artifacts are written by scripts/restored_analyses.py from the frozen
    joined development table; they are post hoc and never abstract-eligible.
    """
    boundary = ("Post hoc descriptive analysis restored from the earlier ChampHLA drafts, "
                "recomputed on the study-run calls (decisions/20261106_posthoc_round3_"
                "amendment.json); development loci only; not external validation")
    for item in read_rows(RESTORED / "discordance_taxonomy.tsv"):
        if item["loci"] == "0":
            continue
        rows.append(exploratory_row(
            result_id=f"DEV_DISCORDANCE_{slug(item['assay'])}_{slug(item['category'])}",
            cohort="1000G-development-unique-truth", modality=item["assay"],
            method="ChampHLA-Consensus by truth-free agreement class",
            analysis_status="exploratory_descriptive",
            endpoint=f"discordance_{item['category']}",
            artifact=RESTORED / "discordance_taxonomy.tsv", result_kind="performance",
            estimate=item["consensus_concordance_percent"],
            ci_low=item["ci_low_percent"], ci_high=item["ci_high_percent"],
            unit="percent", loci=item["loci"], correct=item["consensus_correct"],
            acquired=item["assay_loci"], interval_method=item["interval_method"],
            claim_boundary=boundary,
        ))
    for item in read_rows(RESTORED / "cross_assay_agreement.tsv"):
        for label, column in (("WES", "wes_consensus_correct"),
                              ("RNASEQ", "rnaseq_consensus_correct"),
                              ("POOLED", "pooled_vote_correct")):
            rows.append(exploratory_row(
                result_id=f"DEV_CROSS_ASSAY_{slug(item['stratum'])}_{label}",
                cohort="1000G-development-unique-truth", modality="wes+rnaseq",
                method=("pooled WES and RNA-seq plurality vote" if label == "POOLED"
                        else f"ChampHLA-Consensus ({label})"),
                analysis_status="exploratory_descriptive",
                endpoint=f"cross_assay_{item['stratum']}",
                artifact=RESTORED / "cross_assay_agreement.tsv", result_kind="performance",
                estimate=item[{"WES": "wes_percent", "RNASEQ": "rnaseq_percent",
                               "POOLED": "pooled_percent"}[label]],
                unit="percent", loci=item["loci"], correct=item[column],
                claim_boundary=boundary + "; cross-assay agreement is not independent truth",
            ))
    for item in read_rows(RESTORED / "per_gene_caller_concordance.tsv"):
        rows.append(exploratory_row(
            result_id=(f"DEV_PER_GENE_{slug(item['assay'])}_{slug(item['method'])}_"
                       f"{slug(item['gene'])}"),
            cohort="1000G-development-unique-truth", modality=item["assay"],
            method=item["method"], analysis_status="exploratory_descriptive",
            endpoint=f"exact_concordance_gene_{item['gene']}",
            artifact=RESTORED / "per_gene_caller_concordance.tsv", result_kind="performance",
            estimate=item["concordance_percent"], ci_low=item["wilson_low_percent"],
            ci_high=item["wilson_high_percent"], unit="percent", loci=item["loci"],
            correct=item["correct"], callable_n=item["called"], interval_method="wilson",
            claim_boundary=boundary,
        ))
    for item in read_rows(RESTORED / "caller_calibration.tsv"):
        if item["scored_loci"] == "0":
            continue
        for metric in ("brier", "ece"):
            row = exploratory_row(
                result_id=f"DEV_CALIBRATION_{slug(item['assay'])}_{slug(item['caller'])}_{metric.upper()}",
                cohort="1000G-development-unique-truth", modality=item["assay"],
                method=item["caller"], analysis_status="exploratory_fitted",
                endpoint=f"calibration_{metric}",
                artifact=RESTORED / "caller_calibration.tsv", result_kind="performance",
                estimate=item[metric], unit="score", loci=item["scored_loci"],
                callable_n=item["callable_loci"],
                claim_boundary=("Post hoc descriptive analysis restored from the earlier "
                                "ChampHLA drafts; archived calls, because the study-run calls "
                                "have no calibrated probabilities; probabilities were "
                                "calibrated against earlier development labels, so this is "
                                "exploratory"),
            )
            row["fitted_status"] = "exploratory_fitted"
            rows.append(row)


def append_limits_rows(rows: list[dict[str, str]]) -> None:
    """What the design could detect, the oracle ceiling and caller-error dependence."""
    detect = LIMITS / "detectability.tsv"
    for item in read_rows(detect):
        rows.append(exploratory_row(
            result_id=(f"DEV_DETECTABILITY_{item['modality'].upper()}_"
                       f"{slug(item['comparator'])}"),
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method=f"ChampHLA-Consensus vs {item['comparator']}",
            analysis_status="exploratory_diagnostic",
            endpoint="smallest_significant_difference_with_no_losses",
            artifact=detect, result_kind="design-limit",
            estimate=item["smallest_detectable_points_no_losses"], unit="percentage_points",
            subjects=item["discordant_subjects"], loci=item["loci"],
            correct=item["all_win_subjects_needed_holm_worst_case"],
            claim_boundary=(
                "Exact sign-flip test, Holm worst rank in the comparison's family; correct "
                "holds the all-win subjects needed, subjects the observed discordant "
                "subjects; a property of the design, not an effect estimate"),
        ))
    headroom = LIMITS / "headroom.tsv"
    for item in read_rows(headroom):
        modality = item["modality"]
        for name, value, denominator in (
                ("ORACLE", item["oracle_correct"], item["loci"]),
                ("RECOVERABLE", item["recoverable_by_any_caller"], item["consensus_errors"]),
                ("UNREACHABLE", item["unreachable_by_any_caller"], item["consensus_errors"])):
            rows.append(exploratory_row(
                result_id=f"DEV_HEADROOM_{modality.upper()}_{name}",
                cohort="1000G-development-unique-truth", modality=modality,
                method="oracle choosing any panel caller output",
                analysis_status="exploratory_diagnostic",
                endpoint=f"oracle_headroom_{name.lower()}", artifact=headroom,
                result_kind="categorical-summary", estimate=value, unit="count",
                loci=denominator, correct=value,
                claim_boundary=("Oracle bound with truth knowledge, not an implementable "
                                "method; loci is the fixed denominator (ORACLE) or the "
                                "consensus errors (RECOVERABLE, UNREACHABLE)"),
            ))
    correlations = read_rows(ERROR_PHI)
    for item in correlations:
        rows.append(exploratory_row(
            result_id=(f"DEV_ERROR_PHI_{item['modality'].upper()}_{slug(item['caller1'])}_"
                       f"{slug(item['caller2'])}"),
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method=f"{item['caller1']} and {item['caller2']}",
            analysis_status="exploratory_diagnostic",
            endpoint="pairwise_caller_error_phi", artifact=ERROR_PHI,
            result_kind="association", estimate=item["error_phi"], unit="phi",
            ci_low=item["error_phi_ci_lo"], ci_high=item["error_phi_ci_hi"],
            interval_method=item["error_phi_interval_method"],
            loci=item["loci"], claim_boundary=(
                "Fixed-denominator caller-error phi; a shared no-call counts as a joint "
                "error; descriptive dependence, not causal"),
        ))
    for modality in ("wes", "rnaseq"):
        part = [r for r in correlations if r["modality"] == modality]
        for name, field in (("ALL", "error_phi"), ("MUTUALLY_CALLABLE",
                                                   "mutually_callable_error_phi")):
            values = sorted(float(r[field]) for r in part)
            middle = len(values) // 2
            median = (values[middle] if len(values) % 2
                      else (values[middle - 1] + values[middle]) / 2)
            rows.append(exploratory_row(
                result_id=f"DEV_ERROR_PHI_{modality.upper()}_RANGE_{name}",
                cohort="1000G-development-unique-truth", modality=modality,
                method="all caller pairs in the panel",
                analysis_status="exploratory_diagnostic",
                endpoint=f"pairwise_caller_error_phi_{name.lower()}", artifact=ERROR_PHI,
                result_kind="association", estimate=f"{median:.6f}", unit="phi",
                ci_low=f"{values[0]:.6f}", ci_high=f"{values[-1]:.6f}",
                interval_method="median with minimum and maximum over caller pairs",
                subjects=str(len(values)), claim_boundary=(
                    "Summary over caller pairs (subjects holds the pair count); "
                    "descriptive dependence, not causal"),
            ))


def append_truth_selection_rows(rows: list[dict[str, str]]) -> None:
    """Retained (resolved) against excluded (ambiguous) reference loci."""
    for item in read_rows(SELECTION):
        rows.append(exploratory_row(
            result_id=(f"DEV_TRUTH_SELECTION_{item['modality'].upper()}_"
                       f"{item['stratum'].upper()}_{slug(item['method'])}"),
            cohort="1000G-development-candidate-truth", modality=item["modality"],
            method=item["method"], analysis_status="exploratory_sensitivity",
            endpoint=f"two_field_candidate_compatibility_{item['stratum']}_reference_loci",
            artifact=SELECTION, result_kind="concordance",
            estimate=item["compatibility_concordance"], unit="proportion",
            ci_low=item["ci_lo"], ci_high=item["ci_hi"],
            interval_method=item["interval_method"],
            subjects=item["subjects"], loci=item["loci"], correct=item["compatible"],
            claim_boundary=("Resolved loci are the exact-endpoint loci (compatibility equals "
                            "exact concordance); ambiguous loci were excluded from it and "
                            "are scored leniently against every allowed candidate pair"),
        ))
    for item in read_rows(SELECTION_PROFILE):
        for name, field in (("CEU_YRI", "ceu_ceph_or_yri_loci"),
                            ("CALLER_UNANIMOUS", "caller_unanimous_loci")):
            rows.append(exploratory_row(
                result_id=(f"DEV_TRUTH_SELECTION_PROFILE_{item['modality'].upper()}_"
                           f"{item['stratum'].upper()}_{name}"),
                cohort="1000G-development-candidate-truth", modality=item["modality"],
                method="truth-free stratum profile", analysis_status="exploratory_diagnostic",
                endpoint=f"truth_selection_{name.lower()}_loci", artifact=SELECTION_PROFILE,
                result_kind="categorical-summary", estimate=item[field], unit="count",
                subjects=item["subjects"], loci=item["loci"], correct=item[field],
                claim_boundary=("CEU_YRI counts loci from the CEPH (CEU) or YRI HapMap "
                                "samples; CALLER_UNANIMOUS counts loci where at least two "
                                "panel callers were callable and all agreed"),
            ))


def append_tie_break_rows(rows: list[dict[str, str]]) -> None:
    """ChampHLA-Consensus with exact ties sent to the last-sorting pair instead."""
    for item in read_rows(TIE_BREAK):
        for name, field in (("TIED_LOCI", "tied_loci"), ("LAST_PAIR", "correct_last_pair")):
            rows.append(exploratory_row(
                result_id=f"DEV_TIEBREAK_{item['modality'].upper()}_{name}",
                cohort="1000G-development-unique-truth", modality=item["modality"],
                method="ChampHLA-Consensus, reverse tie-break" if name == "LAST_PAIR"
                else "ChampHLA-Consensus", analysis_status="exploratory_sensitivity",
                endpoint=("exact_unordered_two_field_genotype_concordance"
                          if name == "LAST_PAIR" else "loci_with_tied_top_votes"),
                artifact=TIE_BREAK, result_kind="concordance" if name == "LAST_PAIR"
                else "categorical-summary",
                estimate=(f"{int(item[field]) / int(item['loci']):.6f}" if name == "LAST_PAIR"
                          else item[field]),
                unit="proportion" if name == "LAST_PAIR" else "count",
                loci=item["loci"], correct=item[field],
                claim_boundary=("Tie-break sensitivity on the exact-endpoint loci; the primary "
                                "rule sends ties to the first-sorting pair"),
            ))


def append_single_allele_rows(rows: list[dict[str, str]]) -> None:
    """Single-allele caller rows at exact loci against the reference zygosity."""
    for item in read_rows(SINGLE_ALLELE):
        if item["caller"] != "all":
            continue
        rows.append(exploratory_row(
            result_id=f"DEV_SINGLE_ALLELE_{item['modality'].upper()}_REFERENCE_HOMOZYGOUS",
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method="all panel callers", analysis_status="exploratory_diagnostic",
            endpoint="single_allele_rows_at_reference_homozygous_loci", artifact=SINGLE_ALLELE,
            result_kind="categorical-summary", estimate=item["reference_homozygous"],
            unit="count", loci=item["single_allele_rows"],
            correct=item["reference_homozygous"],
            claim_boundary=("loci counts caller rows reporting one allele at exact-endpoint "
                            "loci; correct counts those where the reference genotype is "
                            "homozygous"),
        ))


def append_adjudication_rows(rows: list[dict[str, str]]) -> None:
    """Second-typing adjudication (decisions/20261009_reference_adjudication.json)
    and its post hoc flagged-value analysis (..._posthoc.json)."""
    classes = ADJUDICATION / "reference_adjudication.tsv"
    if not classes.is_file():
        return
    adjudication = read_rows(classes)
    for modality in ("wes", "rnaseq"):
        part = [r for r in adjudication if r["modality"] == modality]
        for name, label in (("UNAVAILABLE", "second typing unavailable"),
                            ("MATCHES_REFERENCE", "second typing matches reference"),
                            ("MATCHES_CONSENSUS", "second typing matches consensus"),
                            ("MATCHES_NEITHER", "second typing matches neither")):
            count = sum(r["adjudication"] == label for r in part)
            rows.append(exploratory_row(
                result_id=f"DEV_ADJUDICATION_{modality.upper()}_{name}",
                cohort="1000G-development-unique-truth", modality=modality,
                method="ChampHLA-Consensus error loci", analysis_status="exploratory_diagnostic",
                endpoint="second_typing_adjudication_class", artifact=classes,
                result_kind="categorical-summary", estimate=str(count), unit="count",
                loci=str(len(part)), correct=str(count),
                claim_boundary=("Second typing (Abi-Rached 2018, same exomes) adjudicates "
                                "consensus error loci; signed parsing rule"),
            ))
    agreement = ADJUDICATION / "reference_typing_agreement.tsv"
    for item in read_rows(agreement):
        if item["gene"] != "all" or item["loci"] == "0":
            continue
        rows.append(exploratory_row(
            result_id=f"DEV_REFERENCE_TYPINGS_AGREE_{item['modality'].upper()}",
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method="2014 reference vs second typing", analysis_status="exploratory_diagnostic",
            endpoint="reference_typing_agreement", artifact=agreement,
            result_kind="categorical-summary", estimate=item["typings_agree"], unit="count",
            loci=item["second_typing_available"], correct=item["typings_agree"],
            claim_boundary="Loci where the second typing was available under the signed rule",
        ))
    sensitivity = ADJUDICATION / "reference_agreement_sensitivity.tsv"
    for item in read_rows(sensitivity):
        if item["agreement_loci"] == "0":
            continue
        loci, correct = int(item["agreement_loci"]), int(item["agreement_correct"])
        rows.append(exploratory_row(
            result_id=(f"DEV_REFERENCE_AGREEMENT_{item['modality'].upper()}_"
                       f"{slug(item['method'])}"),
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method=item["method"], analysis_status="exploratory_sensitivity",
            endpoint="exact_concordance_on_loci_where_both_typings_agree",
            artifact=sensitivity, result_kind="concordance",
            estimate=f"{correct / loci:.6f}", unit="proportion",
            loci=str(loci), correct=str(correct),
            claim_boundary="Method-independent subset: both reference typings agree",
        ))
    substitution = ADJUDICATION / "reference_substitution_posthoc.tsv"
    for item in read_rows(substitution):
        loci, correct = int(item["loci"]), int(item["substituted_correct"])
        rows.append(exploratory_row(
            result_id=(f"DEV_REFERENCE_SUBSTITUTION_{item['modality'].upper()}_"
                       f"{slug(item['method'])}"),
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method=item["method"], analysis_status="exploratory_sensitivity",
            endpoint="posthoc_exact_concordance_with_corrected_values_substituted",
            artifact=substitution, result_kind="concordance",
            estimate=f"{correct / loci:.6f}", unit="proportion",
            loci=str(loci), correct=str(correct),
            claim_boundary=("POST HOC (decisions/20261105_reference_presentation_amendment."
                            "json); flagged values derive from the same exome data, so this "
                            "is not independent and does not rank methods"),
        ))
    round2 = "POST HOC (decisions/20261105_posthoc_round2_amendment.json); "
    p_group = ADJUDICATION / "exact_locus_p_group_agreement_posthoc.tsv"
    for item in read_rows(p_group):
        loci, correct = int(item["loci"]), int(item["p_group_agreement"])
        rows.append(exploratory_row(
            result_id=f"DEV_P_GROUP_AGREEMENT_{item['modality'].upper()}_{slug(item['method'])}",
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method=item["method"], analysis_status="exploratory_sensitivity",
            endpoint="posthoc_p_group_agreement_with_2014_type",
            artifact=p_group, result_kind="concordance",
            estimate=f"{correct / loci:.6f}", unit="proportion",
            loci=str(loci), correct=str(correct),
            claim_boundary=round2 + "lenient two-field P-group mapping; not the primary endpoint",
        ))
    leave_one_out = ADJUDICATION / "leave_one_caller_out_posthoc.tsv"
    for item in read_rows(leave_one_out):
        for name, method, correct, called in (
                ("PLURALITY", "plurality", item["plurality_correct"], ""),
                ("STRICT", "strict majority", item["strict_majority_correct"],
                 item["strict_majority_callable"])):
            rows.append(exploratory_row(
                result_id=(f"DEV_LEAVE_ONE_OUT_{item['modality'].upper()}_"
                           f"{slug(item['left_out'])}_{name}"),
                cohort="1000G-development-unique-truth", modality=item["modality"],
                method=f"{method} leaving out {item['left_out']}",
                analysis_status="exploratory_sensitivity",
                endpoint="posthoc_exact_concordance_leaving_one_caller_out",
                artifact=leave_one_out, result_kind="concordance",
                estimate=f"{int(correct) / int(item['loci']):.6f}", unit="proportion",
                loci=item["loci"], correct=correct, callable_n=called,
                claim_boundary=round2 + "describes dependence on one caller; changes no panel",
            ))
    evidence = ADJUDICATION / "flagged_loci_evidence_posthoc.tsv"
    evidence_rows = read_rows(evidence)
    for name, field, value, description in (
            ("ERLICH_GIVES_VOTE", "erlich_2011", "vote", "454 typing gives the vote's type"),
            ("TRUSIGHT_GIVES_VOTE", "trusight_buchkovich_2017", "vote",
             "TruSight typing gives the vote's type"),
            ("P_GROUP_DIFFERS", "p_group_equal", "0", "2014 type and vote differ in P group")):
        count = sum(row[field] == value for row in evidence_rows)
        rows.append(exploratory_row(
            result_id=f"DEV_FLAGGED_LOCI_{name}",
            cohort="1000G-development-unique-truth", modality="wes",
            method="published typing at flagged vote-error loci",
            analysis_status="exploratory_diagnostic",
            endpoint=f"posthoc_flagged_loci_{name.lower()}", artifact=evidence,
            result_kind="categorical-summary", estimate=str(count), unit="count",
            loci=str(len(evidence_rows)), correct=str(count),
            claim_boundary=round2 + description + "; checked only at flagged loci",
        ))
    headroom = ADJUDICATION / "reference_agreement_headroom.tsv"
    for item in read_rows(headroom):
        rows.append(exploratory_row(
            result_id=f"DEV_REFERENCE_AGREEMENT_{item['modality'].upper()}_ORACLE",
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method="oracle choosing any panel caller output",
            analysis_status="exploratory_sensitivity",
            endpoint="oracle_correct_on_loci_where_both_typings_agree", artifact=headroom,
            result_kind="categorical-summary", estimate=item["oracle_correct"], unit="count",
            loci=item["loci"], correct=item["oracle_correct"],
            claim_boundary="Oracle bound on the subset where both reference typings agree",
        ))
    # decisions/20261009_reference_adjudication.json, reporting commitment 1: phi on
    # the same subset is reported whatever its direction (SR-001).
    agreement_phi = ADJUDICATION / "reference_agreement_error_phi.tsv"
    phi_rows = [item for item in read_rows(agreement_phi) if item["loci"] != "0"]
    phi_boundary = ("Fixed-denominator caller-error phi on the loci where both reference "
                    "typings agree; the subset is conditioned on a further exome-based "
                    "caller, so it is descriptive and estimated on few errors")
    for item in phi_rows:
        rows.append(exploratory_row(
            result_id=(f"DEV_REFERENCE_AGREEMENT_PHI_{item['modality'].upper()}_"
                       f"{slug(item['caller1'])}_{slug(item['caller2'])}"),
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method=f"{item['caller1']} and {item['caller2']}",
            analysis_status="exploratory_sensitivity",
            endpoint="pairwise_caller_error_phi_on_loci_where_both_typings_agree",
            artifact=agreement_phi, result_kind="association",
            estimate=item["error_phi"], unit="phi", loci=item["loci"],
            correct=item["both_wrong"], claim_boundary=phi_boundary + "; correct holds the "
            "loci both callers got wrong",
        ))
    for modality in ("wes", "rnaseq"):
        values = sorted(float(r["error_phi"]) for r in phi_rows if r["modality"] == modality)
        middle = len(values) // 2
        median = (values[middle] if len(values) % 2
                  else (values[middle - 1] + values[middle]) / 2)
        rows.append(exploratory_row(
            result_id=f"DEV_REFERENCE_AGREEMENT_PHI_{modality.upper()}_RANGE",
            cohort="1000G-development-unique-truth", modality=modality,
            method="all caller pairs in the panel", analysis_status="exploratory_sensitivity",
            endpoint="pairwise_caller_error_phi_on_loci_where_both_typings_agree",
            artifact=agreement_phi, result_kind="association",
            estimate=f"{median:.6f}", unit="phi",
            ci_low=f"{values[0]:.6f}", ci_high=f"{values[-1]:.6f}",
            interval_method="median with minimum and maximum over caller pairs",
            subjects=str(len(values)), claim_boundary=(
                "Summary over caller pairs (subjects holds the pair count); " + phi_boundary),
        ))
    correction = ADJUDICATION / "reference_agreement_vote_correction.tsv"
    for item in read_rows(correction):
        if item["loci"] == "0":
            continue
        rows.append(exploratory_row(
            result_id=(f"DEV_REFERENCE_AGREEMENT_{item['modality'].upper()}_VOTE_CORRECTS_"
                       f"{slug(item['caller'])}"),
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method=f"ChampHLA-Consensus at {item['caller']} errors",
            analysis_status="exploratory_sensitivity",
            endpoint="vote_correct_at_caller_errors_on_loci_where_both_typings_agree",
            artifact=correction, result_kind="categorical-summary",
            estimate=item["vote_correct_at_caller_errors"], unit="count",
            loci=item["caller_errors"], correct=item["vote_correct_at_caller_errors"],
            claim_boundary=("loci holds the caller's errors on the loci where both reference "
                            "typings agree (a missing call scores incorrect); correct holds "
                            "those at which the vote is correct"),
        ))
    posthoc = ADJUDICATION / "reference_adjudication_flagged_posthoc.tsv"
    for item in read_rows(posthoc):
        for name, field, denominator in (
                ("FLAGGED_DISCORDANT", "flagged_loci_consensus_discordant", "flagged_loci"),
                ("FLAGGED_EQUALS_CONSENSUS", "flagged_typing_equals_consensus",
                 "flagged_loci_consensus_discordant")):
            rows.append(exploratory_row(
                result_id=f"DEV_ADJUDICATION_POSTHOC_{item['modality'].upper()}_{name}",
                cohort="1000G-development-unique-truth", modality=item["modality"],
                method="asterisk-flagged second typing", analysis_status="exploratory_diagnostic",
                endpoint=f"posthoc_{name.lower()}", artifact=posthoc,
                result_kind="categorical-summary", estimate=item[field], unit="count",
                loci=item[denominator], correct=item[field],
                claim_boundary=("POST HOC (decisions/20261009_reference_adjudication_posthoc."
                                "json); the asterisk marks a typing the source kept after "
                                "manual verification against the earlier published type "
                                "(decisions/20261012_second_typing_asterisk_documented.json)"),
            ))


def append_round3_rows(rows: list[dict[str, str]]) -> None:
    """Rows from decisions/20261106_posthoc_round3_amendment.json (B2-B4, B7, B8)."""
    round3 = "POST HOC (decisions/20261106_posthoc_round3_amendment.json); "
    cohort = "1000G-development-unique-truth"
    counts = ADJUDICATION / "error_dependence_counts_posthoc.tsv"
    for item in read_rows(counts):
        rows.append(exploratory_row(
            result_id=(f"DEV_ERROR_COUNTS_{item['modality'].upper()}_{slug(item['scope'])}_"
                       f"{slug(item['caller1'])}_{slug(item['caller2'])}"),
            cohort=cohort, modality=item["modality"],
            method=f"{item['caller1']} and {item['caller2']}",
            analysis_status="exploratory_diagnostic", endpoint=f"joint_errors_{item['scope']}",
            artifact=counts, result_kind="categorical-summary", estimate=item["both_wrong"],
            unit="count", loci=item["loci"], correct=item["both_wrong"],
            claim_boundary=round3 + (
                f"expected if independent {item['expected_both_wrong_if_independent']}; "
                f"same wrong genotype {item['both_wrong_same_genotype']}; phi "
                f"{item['error_phi'] or 'undefined'}; descriptive dependence, not causal"),
        ))
    naive = ADJUDICATION / "naive_baselines_posthoc.tsv"
    for item in read_rows(naive):
        for scope in ("exact", "set_valued", "excluded"):
            loci, correct = int(item[f"{scope}_loci"]), int(item[f"{scope}_correct"])
            rows.append(exploratory_row(
                result_id=(f"DEV_NAIVE_{item['modality'].upper()}_{slug(item['baseline'])}_"
                           f"{slug(scope)}"),
                cohort=cohort, modality=item["modality"],
                method=item["baseline"].replace("_", " "),
                analysis_status="exploratory_descriptive",
                endpoint=f"naive_baseline_{scope}", artifact=naive, result_kind="concordance",
                estimate=f"{correct / loci:.6f}", unit="proportion",
                loci=str(loci), correct=str(correct),
                claim_boundary=round3 + "leave-one-subject-out baseline using no reads; "
                                        "descriptive, not a comparator",
            ))
    intersection = ADJUDICATION / "set_valued_intersection_posthoc.tsv"
    for item in read_rows(intersection):
        if not (item["method"] == "SimplePluralityLex" or item["method"].startswith("Caller:")):
            continue
        for scope in ("set_valued", "excluded"):
            loci = int(item[f"{scope}_intersection_loci"])
            correct = int(item[f"{scope}_intersection_compatible"])
            rows.append(exploratory_row(
                result_id=(f"DEV_INTERSECTION_{item['modality'].upper()}_{slug(scope)}_"
                           f"{slug(item['method'])}"),
                cohort="1000G-development-set-valued-truth", modality=item["modality"],
                method=item["method"], analysis_status="exploratory_sensitivity",
                endpoint=f"set_valued_compatibility_intersected_rows_{scope}",
                artifact=intersection, result_kind="concordance",
                estimate=f"{correct / loci:.6f}", unit="proportion",
                loci=str(loci), correct=str(correct),
                claim_boundary=round3 + "duplicate reference rows intersected instead of "
                                        "united; sensitivity only",
            ))
    gap = ADJUDICATION / "g_over_p_gap_posthoc.tsv"
    for item in read_rows(gap):
        rows.append(exploratory_row(
            result_id=f"DEV_G_OVER_P_GAP_{item['modality'].upper()}_{slug(item['caller'])}",
            cohort="1000G-development-set-valued-truth", modality=item["modality"],
            method=item["caller"], analysis_status="exploratory_diagnostic",
            endpoint="g_compatible_not_p_compatible", artifact=gap,
            result_kind="categorical-summary", estimate=item["g_compatible_not_p_compatible"],
            unit="count", correct=item["of_which_null_suffix"],
            claim_boundary=round3 + "correct column counts loci whose call carries a null "
                                    "(N) suffix",
        ))
    historical = RERUN_PROVENANCE / "historical_result_registry_pre_v350.tsv"
    archived = next(r for r in read_rows(historical)
                    if r["result_id"] == "DEV_CORRECTED_WES_CALLER_POLYSOLVER")
    rows.append(exploratory_row(
        result_id="DEV_ARCHIVED_WES_CALLER_POLYSOLVER", cohort=cohort, modality="wes",
        method="Caller:POLYSOLVER", analysis_status="exploratory_descriptive",
        endpoint="exact_concordance_archived_outputs", artifact=historical,
        result_kind="concordance", estimate=archived["accuracy"], unit="proportion",
        loci=archived["loci"], correct=archived["correct"],
        claim_boundary=round3 + "archived outputs of an unrecorded deployment; provenance, "
                                "not a study-run result",
    ))
    relatedness = ADJUDICATION / "relatedness_pairs_posthoc.tsv"
    clustered = ADJUDICATION / "family_clustered_signflip_posthoc.tsv"
    if relatedness.is_file() and clustered.is_file():
        tests = read_rows(clustered)
        for item in read_rows(relatedness):
            pairs = sum(int(item[k]) for k in ("parent_offspring", "siblings",
                                               "second_order", "third_order"))
            rows.append(exploratory_row(
                result_id=f"DEV_RELATED_PAIRS_{item['modality'].upper()}",
                cohort=cohort, modality=item["modality"],
                method="public IGSR pedigree (20130606_g1k.ped)",
                analysis_status="exploratory_diagnostic", endpoint="related_subject_pairs",
                artifact=relatedness, result_kind="categorical-summary", estimate=str(pairs),
                unit="count", subjects=item["subjects"],
                claim_boundary=round3 + "first- to third-degree pairs among retained "
                                        f"subjects; {item['family_clusters']} family clusters; "
                                        "truth-free",
            ))
            members = [t for t in tests if t["modality"] == item["modality"]]
            rows.append(exploratory_row(
                result_id=f"DEV_FAMILY_CLUSTERED_{item['modality'].upper()}_VERDICTS_CHANGED",
                cohort=cohort, modality=item["modality"],
                method="sign-flip clustered by pedigree family",
                analysis_status="exploratory_sensitivity",
                endpoint="signflip_holm_verdicts_changed_by_family_clustering",
                artifact=clustered, result_kind="categorical-summary",
                estimate=str(sum(int(t["verdict_changed"]) for t in members)), unit="count",
                loci=str(len(members)),
                claim_boundary=round3 + f"{len(members)} comparisons; same seeds and Holm "
                                        "families as the primary analysis",
            ))
    allele = ADJUDICATION / "allele_level_vote_posthoc.tsv"
    for item in read_rows(allele):
        loci, correct = int(item["loci"]), int(item["allele_vote_correct"])
        rows.append(exploratory_row(
            result_id=f"DEV_ALLELE_LEVEL_VOTE_{item['modality'].upper()}",
            cohort=cohort, modality=item["modality"], method="allele-level vote",
            analysis_status="exploratory_sensitivity", endpoint="exact_concordance",
            artifact=allele, result_kind="concordance", estimate=f"{correct / loci:.6f}",
            unit="proportion", loci=str(loci), correct=str(correct),
            claim_boundary=round3 + "labelled post hoc row, not a candidate primary",
        ))
    tradeoff = ADJUDICATION / "vote_abstention_tradeoff_posthoc.tsv"
    for item in read_rows(tradeoff):
        rows.append(exploratory_row(
            result_id=(f"DEV_ABSTENTION_{item['modality'].upper()}_SUPPORT_"
                       f"{item['minimum_support']}"),
            cohort=cohort, modality=item["modality"],
            method=f"ChampHLA-Consensus abstaining below support {item['minimum_support']}",
            analysis_status="exploratory_descriptive", endpoint="callability_tradeoff",
            artifact=tradeoff, result_kind="concordance",
            estimate=f"{int(item['correct']) / int(item['loci']):.6f}", unit="proportion",
            loci=item["loci"], correct=item["correct"], callable_n=item["called"],
            claim_boundary=round3 + "every threshold reported; a callability trade-off, "
                                    "not a candidate rule",
        ))


def append_nomenclature_rows(rows: list[dict[str, str]]) -> None:
    """Consensus error loci whose truth and predicted alleles are all current 3.65.0."""
    audit = [r for r in read_rows(NOMENCLATURE) if r["method"] == "SimplePluralityLex"]
    for modality in ("wes", "rnaseq"):
        part = [r for r in audit if r["modality"] == modality]
        current = sum(
            all(m == "current_release" for m in r["truth_membership_3_65"].split(";"))
            and r["call_status"] == "callable"
            and all(m == "current_release" for m in r["prediction_membership_3_65"].split(";"))
            for r in part)
        rows.append(exploratory_row(
            result_id=f"DEV_NOMENCLATURE_{modality.upper()}_CONSENSUS_ERRORS_CURRENT",
            cohort="1000G-development-unique-truth", modality=modality,
            method="ChampHLA-Consensus", analysis_status="exploratory_diagnostic",
            endpoint="error_loci_with_all_alleles_current_ipd_3_65", artifact=NOMENCLATURE,
            result_kind="categorical-summary", estimate=str(current), unit="count",
            loci=str(len(part)), correct=str(current),
            callable_n=str(sum(r["call_status"] == "callable" for r in part)),
            claim_boundary=("loci counts consensus error loci; correct counts callable ones "
                            "whose truth and predicted alleles are all current 3.65.0 "
                            "designations; release membership only, not database vintage"),
        ))


def append_truth_retention_rows(rows: list[dict[str, str]]) -> None:
    """Population retention after excluding source-absent truth rows."""
    grouped: dict[tuple[str, str], dict[str, int]] = {}
    for item in read_rows(TRUTH_EXCLUSION):
        key = (item["modality"], item["population"])
        states = grouped.setdefault(key, {})
        states[item["truth_state"]] = states.get(item["truth_state"], 0) + int(item["loci"])
    for (modality, population), states in sorted(grouped.items()):
        resolved = states.get("resolved", 0)
        source_present = resolved + states.get("ambiguous", 0) + states.get("invalid", 0)
        if source_present == 0:
            continue
        rows.append(exploratory_row(
            result_id=f"DEV_TRUTH_RETENTION_{modality.upper()}_{slug(population)}",
            cohort="1000G-development", modality=modality,
            method=f"2014 public truth representation, {population}",
            analysis_status="exploratory_diagnostic",
            endpoint="exact_truth_retention_among_source_present_loci",
            artifact=TRUTH_EXCLUSION, result_kind="concordance",
            estimate=f"{resolved / source_present:.6f}", unit="proportion",
            loci=str(source_present), correct=str(resolved), intended=str(source_present),
            acquired=str(source_present), callable_n=str(resolved),
            claim_boundary=("Population-specific property of the 2014 truth representation "
                            "after pooling HLA-A, -B and -C; not a biological population "
                            "accuracy estimate"),
        ))


def append_hg00096_rerun_rows(rows: list[dict[str, str]]) -> None:
    """Stored development calls vs a September 2026 workflow re-run on HG00096."""
    comparison = [r for r in read_rows(HG00096_RERUN) if r["rerun"] != "not_rerun"]
    for modality in ("wes", "rnaseq"):
        part = [r for r in comparison if r["modality"] == modality]
        agree = sum(r["agree"] == "1" for r in part)
        rows.append(exploratory_row(
            result_id=f"DEV_HG00096_RERUN_{modality.upper()}", cohort="1000G-development",
            modality=modality, method="stored caller calls vs workflow re-run",
            analysis_status="exploratory_diagnostic",
            endpoint="caller_gene_call_agreement", artifact=HG00096_RERUN,
            result_kind="categorical-summary", estimate=str(agree), unit="count",
            loci=str(len(part)), correct=str(agree), subjects="1",
            claim_boundary=("One subject; the WES re-run used an HLA-region pre-extract "
                            "rather than the whole exome; reproducibility evidence, not accuracy"),
        ))
    releases = read_rows(HG00096_RELEASES)
    for release in ("v3_3_0", "v3_4_0"):
        agree = sum(r[f"agree_{release}"] == "1" for r in releases)
        rows.append(exploratory_row(
            result_id=f"DEV_HG00096_WES_{release.upper()}_WHOLE_EXOME",
            cohort="1000G-development", modality="wes",
            method=f"stored caller calls vs workflow release {release[1:].replace('_', '.')}",
            analysis_status="exploratory_diagnostic",
            endpoint="caller_gene_call_agreement", artifact=HG00096_RELEASES,
            result_kind="categorical-summary", estimate=str(agree), unit="count",
            loci=str(len(releases)), correct=str(agree), subjects="1",
            claim_boundary=("One subject, whole-exome CRAM; reproducibility evidence, not "
                            "accuracy; 3.3.0 lost reads on HLA and chr6 alt contigs"),
        ))
    genes = sorted({r["gene"] for r in releases})
    unanimous = sum(len({r["v3_4_0"] for r in releases if r["gene"] == g}) == 1 for g in genes)
    rows.append(exploratory_row(
        result_id="DEV_HG00096_WES_V3_4_0_CALLERS_UNANIMOUS_GENES",
        cohort="1000G-development", modality="wes",
        method="workflow release 3.4.0, all WES panel callers",
        analysis_status="exploratory_diagnostic",
        endpoint="genes_with_identical_calls_from_every_panel_caller", artifact=HG00096_RELEASES,
        result_kind="categorical-summary", estimate=str(unanimous), unit="count",
        loci=str(len(genes)), correct=str(unanimous), subjects="1",
        claim_boundary="One subject; agreement among callers, not accuracy",
    ))
    rna = read_rows(HG00096_RNA_RELEASE)
    agree = sum(r["agree_v3_4_0_bam"] == "1" for r in rna)
    rows.append(exploratory_row(
        result_id="DEV_HG00096_RNASEQ_V3_4_0_GEUVADIS_BAM",
        cohort="1000G-development", modality="rnaseq",
        method="stored caller calls vs workflow release 3.4.0 on the Geuvadis BAM",
        analysis_status="exploratory_diagnostic",
        endpoint="caller_gene_call_agreement", artifact=HG00096_RNA_RELEASE,
        result_kind="categorical-summary", estimate=str(agree), unit="count",
        loci=str(len(rna)), correct=str(agree), subjects="1",
        claim_boundary=("One subject; the input format the extension stages for RNA-seq; "
                        "reproducibility evidence, not accuracy"),
    ))


def append_frozen_nestedcv_rows(rows: list[dict[str, str]]) -> None:
    """Replaced frozen selector, reported once (decisions/20261009_nestedcv_refit.json)."""
    for item in read_rows(FROZEN_NESTEDCV):
        loci, correct = int(item["loci"]), int(item["correct"])
        rows.append(exploratory_row(
            result_id=f"DEV_FROZEN_NESTEDCV_LEGACY_{item['modality'].upper()}",
            cohort="1000G-development-unique-truth", modality=item["modality"],
            method="BestSingleTool_nestedCV (frozen legacy predictions, replaced)",
            analysis_status="exploratory_fitted",
            endpoint="exact_unordered_two_field_genotype_concordance",
            artifact=FROZEN_NESTEDCV, result_kind="concordance",
            estimate=f"{correct / loci:.6f}", unit="proportion",
            loci=str(loci), correct=str(correct), claim_boundary=(
                "Historical predictions fitted under superseded labels and call states; "
                "replaced by the refit and not part of any inference family"),
        ))


def append_identity_rows(rows: list[dict[str, str]]) -> None:
    """Sample-identity QC (decisions/20261008_identity_check_na07000.json)."""
    checks = read_rows(IDENTITY)
    boundary = ("Truth-free sample-identity quality control added after development results "
                "were known; counts of subjects or subject-assays, not accuracy evidence")
    compared = [row for row in checks if row["genes_compared"] == "3"]
    for shared in sorted({row["alleles_shared"] for row in compared}, key=int):
        count = sum(row["alleles_shared"] == shared for row in compared)
        rows.append(exploratory_row(
            result_id=f"DEV_IDENTITY_SHARED_{shared}_OF_6", cohort="1000G-development",
            modality="wes+rnaseq", method="WES vs RNA-seq plurality genotype",
            analysis_status="exploratory_diagnostic",
            endpoint=f"subjects_sharing_{shared}_of_6_alleles", artifact=IDENTITY,
            result_kind="categorical-summary", estimate=str(count), unit="count",
            subjects=str(count), acquired=str(len(compared)), claim_boundary=boundary,
        ))
    primary = {row["modality"]: row for row in read_rows(SOURCE)
               if row["method"] == "SimplePluralityLex"}
    for item in read_rows(IDENTITY_EFFECT):
        modality = item["modality"]
        loci = int(primary[modality]["loci"]) + int(item["withheld_retained_loci"])
        correct = (int(primary[modality]["genotypes_correct"])
                   + int(item["withheld_consensus_correct"]))
        rows.append(exploratory_row(
            result_id=f"DEV_IDENTITY_WITHHELD_{modality.upper()}", cohort="1000G-development",
            modality=modality, method="SimplePluralityLex on withheld inputs",
            analysis_status="exploratory_sensitivity", endpoint="withheld_input_exact_concordance",
            artifact=IDENTITY_EFFECT, result_kind="categorical-summary",
            estimate=item["withheld_consensus_correct"], unit="count",
            loci=item["withheld_retained_loci"], correct=item["withheld_consensus_correct"],
            claim_boundary="Withheld identity-failure input scored for transparency only",
        ))
        rows.append(exploratory_row(
            result_id=f"DEV_IDENTITY_WITH_WITHHELD_{modality.upper()}_SIMPLEPLURALITYLEX",
            cohort="1000G-development", modality=modality,
            method="SimplePluralityLex including withheld inputs",
            analysis_status="exploratory_sensitivity",
            endpoint="exact_unordered_two_field_genotype_concordance_including_withheld",
            artifact=IDENTITY_EFFECT, result_kind="concordance",
            estimate=f"{correct / loci:.6f}", unit="proportion", loci=str(loci),
            correct=str(correct), claim_boundary=(
                "Sensitivity: primary endpoint with the identity-failure input included; "
                "not the reported primary result"),
        ))
    absent = sum(row[f"{modality}_in_assay_manifest"] == "0"
                 for row in checks for modality in ("wes", "rnaseq"))
    rows.append(exploratory_row(
        result_id="DEV_IDENTITY_NOT_IN_ASSAY_MANIFEST", cohort="1000G-development",
        modality="wes+rnaseq", method="official assay manifest membership",
        analysis_status="exploratory_diagnostic", endpoint="subject_assays_absent_from_manifest",
        artifact=IDENTITY, result_kind="categorical-summary", estimate=str(absent),
        unit="count", claim_boundary=boundary,
    ))
    append_historical_identity_rows(rows)


RERUN_PROVENANCE = ROOT / "provenance" / "development_rerun_v350"
# The NA07000 identity finding was made on the historical stored outputs; the v3.5.0
# rerun applies it in its signed roster, so the rerun has nothing left to withhold.
# These rows are carried from the archived pre-rerun registry, against archived copies
# of their artifacts, so the finding stays citable as historical provenance.
HISTORICAL_IDENTITY_ROWS = {
    "DEV_IDENTITY_SHARED_1_OF_6": "identity_check.tsv",
    "DEV_IDENTITY_WITHHELD_RNASEQ": "identity_withheld_effect.tsv",
    "DEV_IDENTITY_WITH_WITHHELD_RNASEQ_SIMPLEPLURALITYLEX": "identity_withheld_effect.tsv",
}


def append_historical_identity_rows(rows: list[dict[str, str]]) -> None:
    import json
    manifest = ROOT / "data" / "development" / "input_manifest.json"
    if json.loads(manifest.read_text(encoding="utf-8")).get(
        "schema_version") != "champhla-development-rerun-inputs-1":
        return
    present = {row["result_id"] for row in rows}
    historical = {row["result_id"]: row for row in read_rows(
        RERUN_PROVENANCE / "historical_result_registry_pre_v350.tsv")}
    for result_id, artifact_name in HISTORICAL_IDENTITY_ROWS.items():
        if result_id in present:
            raise SystemExit(f"historical identity row collides with a current row: {result_id}")
        archived = RERUN_PROVENANCE / "historical_artifacts" / artifact_name
        source = dict(historical[result_id])
        if sha256(archived) != source["artifact_sha256"]:
            raise SystemExit(f"archived historical artifact differs from its registry row: {archived}")
        source["artifact_path"] = archived.relative_to(ROOT).as_posix()
        source["claim_boundary"] = (
            "Historical stored outputs before the v3.5.0 rerun; the signed rerun roster "
            "excludes this RNA-seq input. " + source.get("claim_boundary", "")
        ).strip()
        rows.append(source)


def append_singleton_sensitivity_rows(rows: list[dict[str, str]]) -> None:
    """Abstain-all scoring reported beside the primary native-declaration scoring
    (decisions/20261008_singleton_native_homozygosity.json)."""
    boundary = (
        "Singleton sensitivity: every single-allele caller output abstains, including "
        "caller-native homozygous declarations; reported beside the primary scoring"
    )
    performance_hash = sha256(SINGLETON_SOURCE)
    for row in read_rows(SINGLETON_SOURCE):
        rows.append({
            "result_id": f"DEV_SINGLETON_ABSTAIN_{row['modality'].upper()}_{slug(row['method'])}",
            "cohort": "1000G-development-unique-truth", "modality": row["modality"],
            "method": row["method"], "analysis_status": "secondary_sensitivity",
            "validity": "valid", "subjects": row["subjects"], "loci": row["loci"],
            "correct": row["genotypes_correct"], "accuracy": row["genotype_accuracy"],
            "artifact_path": SINGLETON_SOURCE.relative_to(ROOT).as_posix(),
            "artifact_sha256": performance_hash, "abstract_allowed": "0",
            "claim_boundary": boundary, "schema_version": SCHEMA,
            "endpoint": "exact_unordered_two_field_genotype_concordance",
            "intended_denominator": row["loci"], "acquired_denominator": row["rows_present"],
            "truth_evaluable_denominator": row["loci"], "callable_denominator": row["callable"],
            "ci_lo": row["genotype_ci_lo"], "ci_hi": row["genotype_ci_hi"],
            "interval_method": genotype_interval_method(row), "raw_p": "", "adjusted_p": "",
            "sensitivity_adjusted_p": "", "inference_family": "", "family_size": "",
            "fitted_status": "fitted" if row["analysis_scope"] == "exploratory_fitted" else "not_fitted",
            "development_status": "retrospective_development",
            "source_artifact_sha256": performance_hash,
        })
    paired_hash = sha256(SINGLETON_PAIRED)
    for row in read_rows(SINGLETON_PAIRED):
        rows.append({
            "result_id": f"DEV_SINGLETON_ABSTAIN_PAIRED_{row['modality'].upper()}_{slug(row['comparator'])}",
            "cohort": "1000G-development-unique-truth", "modality": row["modality"],
            "method": f"ChampHLA-Consensus minus {row['comparator']}",
            "analysis_status": "secondary_sensitivity", "validity": "valid",
            "subjects": row["clusters"], "loci": row["loci"],
            "correct": "", "accuracy": row["delta_points"],
            "artifact_path": SINGLETON_PAIRED.relative_to(ROOT).as_posix(),
            "artifact_sha256": paired_hash, "abstract_allowed": "0",
            "claim_boundary": boundary + ("; p values from the exact subject sign-flip "
                                          "test (Holm); cluster-t Holm p and interval descriptive"),
            "schema_version": SCHEMA,
            "endpoint": "paired_concordance_difference_percentage_points",
            "intended_denominator": row["loci"], "acquired_denominator": row["loci"],
            "truth_evaluable_denominator": row["loci"], "callable_denominator": "",
            "ci_lo": row["simultaneous_ci_lo_points"], "ci_hi": row["simultaneous_ci_hi_points"],
            # decisions/20261009_signflip_governs.json: raw_p and adjusted_p are the
            # governing exact sign-flip test; sensitivity_adjusted_p holds the
            # descriptive CR1 cluster-t Holm p, whose interval is ci_lo/ci_hi.
            "interval_method": row["inference_method"], "raw_p": row["signflip_p_value"],
            "adjusted_p": row["signflip_holm_adjusted_p"],
            "sensitivity_adjusted_p": row["holm_adjusted_p"],
            "inference_family": row["inference_family"], "family_size": row["family_size"],
            "fitted_status": "fitted" if row["inference_family"] == "exploratory_fitted" else "not_fitted",
            "development_status": "retrospective_development",
            "source_artifact_sha256": paired_hash,
        })



def append_ambiguity_paired_rows(rows: list[dict[str, str]]) -> None:
    artifact_hash = sha256(AMBIGUITY_PAIRED)
    for row in read_rows(AMBIGUITY_PAIRED):
        rows.append({
            "result_id": (
                f"DEV_AMBIGUITY_PAIRED_{row['modality'].upper()}_"
                f"{slug(row['comparator'])}"
            ),
            "cohort": "1000G-development-set-valued-truth",
            "modality": row["modality"],
            "method": f"ChampHLA-Consensus minus {row['comparator']}",
            "analysis_status": "secondary_sensitivity",
            "validity": "valid",
            "subjects": row["clusters"],
            "loci": row["loci"],
            "correct": "",
            "accuracy": row["delta_points"],
            "artifact_path": AMBIGUITY_PAIRED.relative_to(ROOT).as_posix(),
            "artifact_sha256": artifact_hash,
            "abstract_allowed": "0",
            "claim_boundary": (
                "Locus-weighted paired difference in set-valued two-field "
                "compatibility; subject-cluster sign-flip test with Holm adjustment "
                "within assay and declared comparator family; sensitivity only"
            ),
            "schema_version": SCHEMA,
            "endpoint": "paired_set_valued_compatibility_difference_percentage_points",
            "intended_denominator": row["loci"],
            "acquired_denominator": row["loci"],
            "truth_evaluable_denominator": row["loci"],
            "callable_denominator": row["comparator_coverage"],
            "ci_lo": "",
            "ci_hi": "",
            "interval_method": "exact_subject_signflip_holm",
            "raw_p": row["signflip_p_value"],
            "adjusted_p": row["signflip_holm_adjusted_p"],
            "sensitivity_adjusted_p": "",
            "inference_family": row["inference_family"],
            "family_size": row["family_size"],
            "fitted_status": (
                "fitted" if row["inference_family"] == "exploratory_fitted"
                else "not_fitted"
            ),
            "development_status": "retrospective_development",
            "source_artifact_sha256": artifact_hash,
        })


def append_round4_rows(rows: list[dict[str, str]]) -> None:
    """Rows from decisions/20261106_posthoc_round4_amendment.json (C1, run stability)."""
    round4 = ("POST HOC (decisions/20261106_posthoc_round4_amendment.json); archived outputs "
              "and study runs scored with the current rule at the current exact loci; ")
    cohort = "1000G-development-unique-truth"
    per_method = ADJUDICATION / "run_stability_posthoc.tsv"
    for item in read_rows(per_method):
        loci, correct = int(item["loci"]), int(item["archived_correct"])
        rows.append(exploratory_row(
            result_id=f"DEV_RUN_STABILITY_{item['modality'].upper()}_{slug(item['method'])}",
            cohort=cohort, modality=item["modality"], method=item["method"],
            analysis_status="exploratory_descriptive", endpoint="archived_output_exact_correct",
            artifact=per_method, result_kind="concordance",
            estimate=f"{correct / loci:.6f}", unit="proportion",
            loci=str(loci), correct=str(correct),
            claim_boundary=round4 + (
                f"study runs {item['study_run_correct']}/{loci}, change {item['change']}; "
                "two runs of one deployment, not a reproducibility estimate"),
        ))
    summary = ADJUDICATION / "run_stability_summary_posthoc.tsv"
    for item in read_rows(summary):
        modality = item["modality"]
        rows.append(exploratory_row(
            result_id=f"DEV_RUN_STABILITY_{modality.upper()}_VOTE_CALLS_CHANGED",
            cohort=cohort, modality=modality, method="ChampHLA-Consensus",
            analysis_status="exploratory_descriptive", endpoint="vote_calls_changed_between_runs",
            artifact=summary, result_kind="categorical-summary",
            estimate=item["vote_calls_changed"], unit="count", loci=item["loci"],
            correct=item["vote_calls_changed"],
            claim_boundary=round4 + (
                f"vote {item['vote_archived_correct']} archived and "
                f"{item['vote_study_run_correct']} study-run correct loci"),
        ))
        rows.append(exploratory_row(
            result_id=f"DEV_RUN_STABILITY_{modality.upper()}_LARGEST_CALLER_CHANGE",
            cohort=cohort, modality=modality, method=item["largest_change_caller"],
            analysis_status="exploratory_descriptive",
            endpoint="largest_caller_change_between_runs", artifact=summary,
            result_kind="categorical-summary", estimate=item["largest_caller_change"],
            unit="count", loci=item["loci"], correct=item["largest_caller_change"],
            claim_boundary=round4 + "absolute change in correct loci; descriptive",
        ))
        rows.append(exploratory_row(
            result_id=f"DEV_RUN_STABILITY_{modality.upper()}_LEADING_CALLER",
            cohort=cohort, modality=modality,
            method=(f"archived {item['leading_caller_archived']}; "
                    f"study runs {item['leading_caller_study_run']}"),
            analysis_status="exploratory_descriptive", endpoint="leading_caller_by_run",
            artifact=summary, result_kind="categorical-summary",
            estimate=item["leading_caller_study_run_correct"], unit="count",
            loci=item["loci"], correct=item["leading_caller_study_run_correct"],
            claim_boundary=round4 + (
                f"archived leader {item['leading_caller_archived_correct']}/{item['loci']}; "
                "ties go to the alphabetically last caller; descriptive"),
        ))


def append_round5_rows(rows: list[dict[str, str]]) -> None:
    """Rows from decisions/20261106_roihu_descriptions_round5.json (R1-R4), truth-free."""
    round5 = ("ROUND 5 (decisions/20261106_roihu_descriptions_round5.json); truth-free "
              "description of the 236 study runs, measured once on CSC Roihu; ")
    cohort = "1000G-development"

    def spread_row(result_id, modality, method, endpoint, artifact, item, field, unit, note,
                   n):
        return exploratory_row(
            result_id=result_id, cohort=cohort, modality=modality, method=method,
            analysis_status="exploratory_descriptive", endpoint=endpoint, artifact=artifact,
            result_kind="categorical-summary", estimate=item[f"{field}_median"],
            ci_low=item[f"{field}_min"], ci_high=item[f"{field}_max"], unit=unit,
            subjects=str(n), interval_method="range across runs",
            claim_boundary=round5 + note)

    deployment = ADJUDICATION / "round5_caller_deployment.tsv"
    for item in read_rows(deployment):
        if item["caller"] != "T1K":
            continue
        runs = item["runs"] if item["t1k_index_in_task_logs"].endswith("/hla_dna.fa") else "0"
        rows.append(exploratory_row(
            result_id=f"DEV_DEPLOYMENT_{item['modality'].upper()}_T1K_DNA_INDEX_RUNS",
            cohort=cohort, modality=item["modality"], method="T1K",
            analysis_status="exploratory_descriptive", endpoint="t1k_index_in_task_logs",
            artifact=deployment, result_kind="categorical-summary", estimate=runs,
            unit="count", subjects=item["runs"],
            claim_boundary=round5 + "runs whose T1K task logs name the genomic (DNA) index "
                                    "hla_dna.fa; R1"))
    inputs = ADJUDICATION / "round5_input_read_depth_summary.tsv"
    if inputs.is_file():
        for item in read_rows(inputs):
            modality, n = item["modality"], int(item["inputs"])
            rows.append(spread_row(
                f"DEV_INPUT_{modality.upper()}_READ_LENGTH", modality, "input alignments",
                "median_read_length_over_class_i_exons_2_3", inputs, item, "read_length", "bp",
                f"per-input median read length; layouts {item['layouts']}; R2", n))
            rows.append(spread_row(
                f"DEV_INPUT_{modality.upper()}_EXON_DEPTH", modality, "input alignments",
                "mean_depth_over_class_i_exons_2_3", inputs, item, "exon_depth", "mean depth",
                "per-input mean depth over HLA-A, -B and -C exons 2 and 3 on primary chromosome "
                f"6 of each file's build ({item['detected_builds']}), before read rescue; R2", n))
    rescue = ADJUDICATION / "round5_rescue_totals.tsv"
    for item in read_rows(rescue):
        for field in ("selected_records", "realigned_pairs", "output_records"):
            rows.append(spread_row(
                f"DEV_RESCUE_WES_{field.upper()}", "wes", "RESCUE_HLA_READS",
                f"rescue_{field}_per_run", rescue, item, field, "count",
                f"per-run counts from the rescue tables; total {item[f'{field}_total']}; the "
                "tables record no read class; R3", int(item["runs"])))
    cost = ADJUDICATION / "round5_run_cost.tsv"
    failed: dict[str, int] = {}
    for item in read_rows(cost):
        modality, caller = item["modality"], item["caller"]
        failed[modality] = failed.get(modality, 0) + int(item["failed_task_attempts"])
        note = ("execution traces of the final launch of each run; cached tasks keep the "
                "measurements of the launch that ran them; R4")
        rows.append(spread_row(
            f"DEV_RUN_COST_{modality.upper()}_{slug(caller)}_CPU_HOURS", modality, caller,
            "cpu_hours_per_run", cost, item, "cpu_hours", "CPU hours",
            "realtime x %cpu summed over the caller's tasks; " + note, int(item["runs"])))
        rows.append(spread_row(
            f"DEV_RUN_COST_{modality.upper()}_{slug(caller)}_PEAK_RSS", modality, caller,
            "peak_rss_per_run", cost, item, "peak_rss_gib", "GiB",
            "largest task peak_rss; " + note, int(item["runs"])))
    for modality, count in sorted(failed.items()):
        rows.append(exploratory_row(
            result_id=f"DEV_RUN_COST_{modality.upper()}_FAILED_TASK_ATTEMPTS", cohort=cohort,
            modality=modality, method="all tasks", analysis_status="exploratory_descriptive",
            endpoint="failed_task_attempts", artifact=cost, result_kind="categorical-summary",
            estimate=str(count), unit="count",
            claim_boundary=round5 + "failed or aborted task attempts in the final launch of "
                                    "each run; earlier launches are not in the traces; R4"))


def append_protocol_change_ledger_row(rows: list[dict[str, str]]) -> None:
    changes = read_rows(PROTOCOL_LEDGER)
    artifact_hash = sha256(PROTOCOL_LEDGER)
    rows.append({
        "result_id": "PROTOCOL_CHANGE_LEDGER_20261013",
        "record_type": "protocol_change_ledger",
        "cohort": "1000G-development",
        "modality": "mixed",
        "method": "protocol governance",
        "analysis_status": "operational_provenance",
        "validity": "valid",
        "subjects": "",
        "loci": "",
        "correct": "",
        "accuracy": "",
        "artifact_path": PROTOCOL_LEDGER.relative_to(ROOT).as_posix(),
        "artifact_sha256": artifact_hash,
        "abstract_allowed": "0",
        "claim_boundary": (
            "Dated direction-and-size ledger of post hoc protocol changes, "
            "verdict effects and prior truth exposure; not a performance result"
        ),
        "schema_version": SCHEMA,
        "endpoint": "protocol_change_ledger",
        "intended_denominator": "",
        "acquired_denominator": str(len(changes)),
        "truth_evaluable_denominator": "",
        "callable_denominator": "",
        "ci_lo": "",
        "ci_hi": "",
        "interval_method": "",
        "raw_p": "",
        "adjusted_p": "",
        "sensitivity_adjusted_p": "",
        "inference_family": "",
        "family_size": "",
        "fitted_status": "not_applicable",
        "development_status": "post_hoc_audit",
        "source_artifact_sha256": artifact_hash,
        "result_kind": "categorical-summary",
        "estimate": str(len(changes)),
        "unit": "protocol_changes",
    })




def append_mutually_available_rows(rows: list[dict[str, str]]) -> None:
    artifact_hash = sha256(MUTUALLY_AVAILABLE)
    for item in read_rows(MUTUALLY_AVAILABLE):
        rows.append({
            "result_id": (
                f"DEV_MUTUALLY_AVAILABLE_{item['modality'].upper()}_"
                f"{slug(item['caller'])}"
            ),
            "cohort": "1000G-development-unique-truth",
            "modality": item["modality"],
            "method": item["caller"],
            "analysis_status": "secondary_sensitivity",
            "validity": "valid",
            "subjects": "",
            "loci": item["mutually_available_loci"],
            "correct": item["caller_correct_mutually_available"],
            "accuracy": (
                str(
                    int(item["caller_correct_mutually_available"])
                    / int(item["mutually_available_loci"])
                )
                if int(item["mutually_available_loci"])
                else ""
            ),
            "artifact_path": MUTUALLY_AVAILABLE.relative_to(ROOT).as_posix(),
            "artifact_sha256": artifact_hash,
            "abstract_allowed": "0",
            "claim_boundary": (
                "Historical exact endpoint restricted to loci with a stored caller row; "
                "absent-row task execution state is unrecoverable until the v3.5.0 rerun"
            ),
            "schema_version": SCHEMA,
            "endpoint": "exact_concordance_mutually_available_stored_rows",
            "intended_denominator": item["fixed_loci"],
            "acquired_denominator": item["stored_rows"],
            "truth_evaluable_denominator": item["mutually_available_loci"],
            "callable_denominator": item["mutually_available_loci"],
            "ci_lo": "",
            "ci_hi": "",
            "interval_method": "descriptive_complete_enumeration",
            "raw_p": "",
            "adjusted_p": "",
            "sensitivity_adjusted_p": "",
            "inference_family": "",
            "family_size": "",
            "fitted_status": "not_fitted",
            "development_status": "retrospective_development",
            "source_artifact_sha256": artifact_hash,
            "result_kind": "concordance",
            "estimate": (
                str(
                    int(item["caller_correct_mutually_available"])
                    / int(item["mutually_available_loci"])
                )
                if int(item["mutually_available_loci"])
                else ""
            ),
            "unit": "proportion",
            "events": item["caller_correct_mutually_available"],
        })


def append_representability_rows(rows: list[dict[str, str]]) -> None:
    artifact_hash = sha256(REPRESENTABILITY)
    for item in read_rows(REPRESENTABILITY):
        rows.append({
            "result_id": (
                f"DEV_NATIVE_REPRESENTABILITY_{item['modality'].upper()}_"
                f"{slug(item['caller'])}"
            ),
            "cohort": "1000G-development-unique-truth",
            "modality": item["modality"],
            "method": item["caller"],
            "analysis_status": "secondary_sensitivity",
            "validity": "valid",
            "subjects": "",
            "loci": item["loci"],
            "correct": item["representable_loci"],
            "accuracy": item["representability"],
            "artifact_path": REPRESENTABILITY.relative_to(ROOT).as_posix(),
            "artifact_sha256": artifact_hash,
            "abstract_allowed": "0",
            "claim_boundary": (
                "Membership in checksum-verified current-deployment native allele "
                "list for the intended assay panel; not reconstruction of the "
                "historical caller database and not proof an allele was callable"
            ),
            "schema_version": SCHEMA,
            "endpoint": "current_native_list_exact_truth_representability",
            "intended_denominator": item["loci"],
            "acquired_denominator": item["loci"],
            "truth_evaluable_denominator": item["loci"],
            "callable_denominator": "",
            "ci_lo": "",
            "ci_hi": "",
            "interval_method": "complete_membership_enumeration",
            "raw_p": "",
            "adjusted_p": "",
            "sensitivity_adjusted_p": "",
            "inference_family": "",
            "family_size": "",
            "fitted_status": "not_fitted",
            "development_status": "retrospective_bounded_sensitivity",
            "source_artifact_sha256": artifact_hash,
            "result_kind": "performance",
            "estimate": item["representability"],
            "unit": "proportion",
            "events": item["representable_loci"],
        })



EXTENSION = ROOT / "artifacts" / "extension"
EXTENSION_ROSTER = ROOT / "cohorts" / "frozen_initial_rosters.tsv"
EXTENSION_BOUNDARY = (
    "Pre-registered test (decisions/20261013_extension_v350_preregistration_amendment.json) "
    "on the frozen subject-disjoint extension roster of the same 1000 Genomes resource and "
    "2014 reference typing; reported regardless of direction; not independent external "
    "validation and no equivalence claim"
)


def extension_confirmation_modalities() -> set[str]:
    """Assays whose frozen roster rows are eligible for primary confirmation; the RNA-seq
    roster missed its locked minimum, so its rows are descriptive (frozen_initial_rosters)."""
    eligible = set()
    with EXTENSION_ROSTER.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["modality"] in {"wes", "rnaseq"} and row["primary_confirmation_eligible"] == "1":
                eligible.add(row["modality"])
    return eligible


def append_extension_rows(rows: list[dict[str, str]]) -> None:
    """EXT_* rows from the one-time extension evaluation; absent until it has run."""
    performance_path = EXTENSION / "method_performance.tsv"
    paired_path = EXTENSION / "secondary_method_results.tsv"
    if not performance_path.is_file():
        return
    if not paired_path.is_file() or not (EXTENSION / "unblinding_manifest.json").is_file():
        raise SystemExit("incomplete extension evaluation: performance without paired "
                         "results or unblinding manifest")
    confirmatory = extension_confirmation_modalities()
    performance_hash = sha256(performance_path)
    for row in read_rows(performance_path):
        method, modality = row["method"], row["modality"]
        primary = method == "SimplePluralityLex"
        if primary:
            status = ("preregistered_confirmatory" if modality in confirmatory
                      else "preregistered_descriptive")
        else:
            status = "descriptive_comparator" if method.startswith("Caller:") \
                else "preregistered_descriptive"
        rows.append({
            "result_id": f"EXT_{modality.upper()}_{slug(method)}",
            "cohort": "1000G-2014-unseen-extension", "modality": modality, "method": method,
            "analysis_status": status, "validity": "valid",
            "subjects": row["subjects"], "loci": row["loci"],
            "correct": row["genotypes_correct"], "accuracy": row["genotype_accuracy"],
            "artifact_path": performance_path.relative_to(ROOT).as_posix(),
            "artifact_sha256": performance_hash,
            "abstract_allowed": "1" if status == "preregistered_confirmatory" else "0",
            "claim_boundary": EXTENSION_BOUNDARY, "schema_version": SCHEMA,
            "endpoint": "exact_unordered_two_field_genotype_concordance",
            "intended_denominator": row["loci"], "acquired_denominator": row["rows_present"],
            "truth_evaluable_denominator": row["loci"], "callable_denominator": row["callable"],
            "ci_lo": row["genotype_ci_lo"], "ci_hi": row["genotype_ci_hi"],
            "interval_method": genotype_interval_method(row), "raw_p": "", "adjusted_p": "",
            "sensitivity_adjusted_p": "", "inference_family": "", "family_size": "",
            "fitted_status": "not_fitted", "development_status": "preregistered_extension",
            "source_artifact_sha256": performance_hash,
        })
    paired_hash = sha256(paired_path)
    for row in read_rows(paired_path):
        modality = row["modality"]
        rows.append({
            "result_id": f"EXT_PAIRED_{modality.upper()}_{slug(row['comparator'])}",
            "cohort": "1000G-2014-unseen-extension", "modality": modality,
            "method": f"ChampHLA-Consensus minus {row['comparator']}",
            "analysis_status": ("preregistered_confirmatory" if modality in confirmatory
                                else "preregistered_descriptive"),
            "validity": "valid", "subjects": row["clusters"], "loci": row["loci"],
            "correct": "", "accuracy": row["delta_points"],
            "artifact_path": paired_path.relative_to(ROOT).as_posix(),
            "artifact_sha256": paired_hash, "abstract_allowed": "0",
            "claim_boundary": EXTENSION_BOUNDARY + "; governing exact subject sign-flip test "
                              "(Holm); cluster-t Holm p and interval descriptive",
            "schema_version": SCHEMA,
            "endpoint": "paired_concordance_difference_percentage_points",
            "intended_denominator": row["loci"], "acquired_denominator": row["loci"],
            "truth_evaluable_denominator": row["loci"], "callable_denominator": "",
            "ci_lo": row["simultaneous_ci_lo_points"], "ci_hi": row["simultaneous_ci_hi_points"],
            "interval_method": row["inference_method"], "raw_p": row["signflip_p_value"],
            "adjusted_p": row["signflip_holm_adjusted_p"],
            "sensitivity_adjusted_p": row["holm_adjusted_p"],
            "inference_family": row["inference_family"], "family_size": row["family_size"],
            "fitted_status": "not_fitted", "development_status": "preregistered_extension",
            "source_artifact_sha256": paired_hash,
        })


def main() -> int:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        performance = list(csv.DictReader(handle, delimiter="\t"))
    source_hash = sha256(SOURCE)
    rows = []
    for row in performance:
        method = row["method"]
        rows.append({
            "result_id": f"DEV_CORRECTED_{row['modality'].upper()}_{slug(method)}",
            "cohort": "1000G-development-unique-truth",
            "modality": row["modality"], "method": method,
            "analysis_status": row["analysis_scope"], "validity": "valid",
            "subjects": row["subjects"], "loci": row["loci"],
            "correct": row["genotypes_correct"], "accuracy": row["genotype_accuracy"],
            "artifact_path": SOURCE.relative_to(ROOT).as_posix(),
            "artifact_sha256": source_hash,
            "abstract_allowed": "1" if row["analysis_scope"] == "primary" else "0",
            "claim_boundary": (
                "Retrospective development evidence on uniquely resolved 2014 public-truth "
                "loci; fixed denominator; no external-validity or equivalence claim"
            ),
            "schema_version": SCHEMA,
            "endpoint": "exact_unordered_two_field_genotype_concordance",
            "intended_denominator": row["loci"], "acquired_denominator": row["rows_present"],
            "truth_evaluable_denominator": row["loci"],
            "callable_denominator": row["callable"],
            "ci_lo": row["genotype_ci_lo"], "ci_hi": row["genotype_ci_hi"],
            "interval_method": genotype_interval_method(row), "raw_p": "", "adjusted_p": "",
            "sensitivity_adjusted_p": "", "inference_family": "", "family_size": "",
            "fitted_status": "fitted" if row["analysis_scope"] == "exploratory_fitted" else "not_fitted",
            "development_status": "retrospective_development",
            "source_artifact_sha256": source_hash,
        })
    with PAIRED.open(newline="", encoding="utf-8") as handle:
        paired = list(csv.DictReader(handle, delimiter="\t"))
    paired_hash = sha256(PAIRED)
    for row in paired:
        rows.append({
            "result_id": f"DEV_PAIRED_{row['modality'].upper()}_{slug(row['comparator'])}",
            "cohort": "1000G-development-unique-truth", "modality": row["modality"],
            "method": f"ChampHLA-Consensus minus {row['comparator']}",
            "analysis_status": row["inference_family"], "validity": "valid",
            "subjects": row["clusters"], "loci": row["loci"],
            "correct": "", "accuracy": row["delta_points"],
            "artifact_path": PAIRED.relative_to(ROOT).as_posix(),
            "artifact_sha256": paired_hash, "abstract_allowed": "0",
            "claim_boundary": ("Locus-weighted paired development difference; clustered by "
                               "subject; p values from the exact subject sign-flip test "
                               "(Holm); cluster-t Holm p and interval descriptive"),
            "schema_version": SCHEMA,
            "endpoint": "paired_concordance_difference_percentage_points",
            "intended_denominator": row["loci"], "acquired_denominator": row["loci"],
            "truth_evaluable_denominator": row["loci"], "callable_denominator": "",
            "ci_lo": row["simultaneous_ci_lo_points"],
            "ci_hi": row["simultaneous_ci_hi_points"],
            # decisions/20261009_signflip_governs.json: raw_p and adjusted_p are the
            # governing exact sign-flip test; sensitivity_adjusted_p holds the
            # descriptive CR1 cluster-t Holm p, whose interval is ci_lo/ci_hi.
            "interval_method": row["inference_method"], "raw_p": row["signflip_p_value"],
            "adjusted_p": row["signflip_holm_adjusted_p"],
            "sensitivity_adjusted_p": row["holm_adjusted_p"],
            "inference_family": row["inference_family"], "family_size": row["family_size"],
            "fitted_status": "fitted" if row["inference_family"] == "exploratory_fitted" else "not_fitted",
            "development_status": "retrospective_development",
            "source_artifact_sha256": paired_hash,
        })
    for endpoint, path in (
        ("ambiguity_compatible_two_field", AMBIGUITY),
        ("g_compatible_under_two_field_mapping_ipd_3_65", G_GROUP),
        ("p_group_compatible_under_two_field_mapping_ipd_3_65", P_GROUP),
    ):
        artifact_hash = sha256(path)
        with path.open(newline="", encoding="utf-8") as handle:
            compatibility = list(csv.DictReader(handle, delimiter="\t"))
        for row in compatibility:
            rows.append({
                "result_id": f"DEV_{slug(endpoint)}_{row['modality'].upper()}_{slug(row['method'])}",
                "cohort": "1000G-development-set-valued-truth", "modality": row["modality"],
                "method": row["method"], "analysis_status": "secondary_sensitivity",
                "validity": "valid", "subjects": row["subjects"], "loci": row["loci"],
                "correct": row["compatible"], "accuracy": row["compatibility_concordance"],
                "artifact_path": path.relative_to(ROOT).as_posix(),
                "artifact_sha256": artifact_hash, "abstract_allowed": "0",
                "claim_boundary": (
                    "Set-valued compatibility under a two-field mapping; "
                    "not an exact P/G-group call and not exact primary concordance"
                ),
                "schema_version": SCHEMA, "endpoint": endpoint,
                "intended_denominator": row["loci"], "acquired_denominator": row["loci"],
                "truth_evaluable_denominator": row["loci"],
                "callable_denominator": row["callable"], "ci_lo": row["ci_lo"],
                "ci_hi": row["ci_hi"],
                "interval_method": "subject_cluster_percentile_bootstrap",
                "raw_p": "", "adjusted_p": "", "sensitivity_adjusted_p": "",
                "inference_family": "", "family_size": "",
                "fitted_status": "fitted" if row["method"] != "SimplePluralityLex" and not row["method"].startswith("Caller:") else "not_fitted",
                "development_status": "retrospective_development",
                "source_artifact_sha256": artifact_hash,
            })
    rows.append({
        "result_id": "HISTORICAL_WGS_QUARANTINED", "cohort": "historical",
        "modality": "wgs", "method": "all historical methods",
        "analysis_status": "historical_invalid", "validity": "invalid",
        "subjects": "", "loci": "", "correct": "", "accuracy": "",
        "artifact_path": DECISION.relative_to(ROOT).as_posix(),
        "artifact_sha256": sha256(DECISION), "abstract_allowed": "0",
        "claim_boundary": "Input-invalid historical WGS analysis; quantitative results withheld",
        "schema_version": SCHEMA, "endpoint": "quarantined",
        "intended_denominator": "", "acquired_denominator": "",
        "truth_evaluable_denominator": "", "callable_denominator": "", "ci_lo": "",
        "ci_hi": "", "interval_method": "", "raw_p": "", "adjusted_p": "",
        "sensitivity_adjusted_p": "", "inference_family": "", "family_size": "",
        "fitted_status": "", "development_status": "historical_invalid",
        "source_artifact_sha256": sha256(DECISION),
    })
    if not COMPUTE.is_file():
        raise SystemExit(f"missing compute-smoke registry: {COMPUTE}")
    with COMPUTE.open(newline="", encoding="utf-8") as handle:
        compute_rows = list(csv.DictReader(handle, delimiter="\t"))
    compute_hash = sha256(COMPUTE)
    routes = {}
    for row in compute_rows:
        routes.setdefault(row["assay_route"], []).append(row)
    for route, records in sorted(routes.items()):
        callers = [row for row in records if row["workflow_role"] == "caller"]
        first = records[0]
        rows.append({
            "result_id": f"COMPUTE_SMOKE_{slug(route)}",
            "record_type": "single_sample_workflow_smoke",
            "cohort": "HG00096-current-workflow-smoke", "modality": route,
            "method": "raw-read workflow operational smoke run",
            "analysis_status": "operational_provenance", "validity": "valid",
            "subjects": "1", "loci": "", "correct": "", "accuracy": "",
            "artifact_path": COMPUTE.relative_to(ROOT).as_posix(),
            "artifact_sha256": compute_hash, "abstract_allowed": "0",
            "claim_boundary": (
                "Current one-sample operational measurement only; not historical "
                "development-cohort resource use, monetary cost, or cohort scaling"
            ),
            "schema_version": SCHEMA, "endpoint": "workflow_resource_smoke",
            "intended_denominator": str(len(callers)),
            "acquired_denominator": str(len(callers)),
            "truth_evaluable_denominator": "", "callable_denominator": "",
            "ci_lo": "", "ci_hi": "", "interval_method": "", "raw_p": "",
            "adjusted_p": "", "sensitivity_adjusted_p": "", "inference_family": "",
            "family_size": "", "fitted_status": "not_applicable",
            "development_status": "current_operational_smoke",
            "source_artifact_sha256": compute_hash,
            "workflow_session": first["session_uuid"],
            "workflow_commit": first["workflow_commit"],
            "resource_record_count": str(len(records)),
        })
    append_singleton_sensitivity_rows(rows)
    append_ambiguity_paired_rows(rows)
    append_identity_rows(rows)
    append_frozen_nestedcv_rows(rows)
    append_hg00096_rerun_rows(rows)
    append_truth_retention_rows(rows)
    append_limits_rows(rows)
    append_truth_selection_rows(rows)
    append_nomenclature_rows(rows)
    append_tie_break_rows(rows)
    append_single_allele_rows(rows)
    append_adjudication_rows(rows)
    append_round3_rows(rows)
    append_round4_rows(rows)
    append_round5_rows(rows)
    append_protocol_change_ledger_row(rows)
    append_mutually_available_rows(rows)
    append_representability_rows(rows)
    append_restored_rows(rows)
    append_extension_rows(rows)
    for row in rows:
        row.setdefault("record_type", "scientific_result")
        row.setdefault("workflow_session", "")
        row.setdefault("workflow_commit", "")
        row.setdefault("resource_record_count", "")
        row.setdefault("result_kind", (
            "categorical-summary" if row["record_type"] == "single_sample_workflow_smoke"
            else "performance"
        ))
        row.setdefault("estimate", row.get("accuracy", ""))
        row.setdefault("ci_low", row.get("ci_lo", ""))
        row.setdefault("ci_high", row.get("ci_hi", ""))
        row.setdefault("unit", (
            "percentage_points" if "difference_percentage_points" in row.get("endpoint", "")
            else "proportion"
        ))
        row.setdefault("events", "")
    rows.sort(key=lambda row: row["result_id"])
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"generated {len(rows)} active registry rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
