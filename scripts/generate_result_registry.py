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
FIMM_FLOW = ROOT / "artifacts" / "fimm_consensus" / "cohort_flow.tsv"
FIMM_CROSS = ROOT / "artifacts" / "fimm_consensus" / "cross_modality" / "cross_modality_agreement.tsv"
FIMM_CONFLICTS = ROOT / "artifacts" / "fimm_consensus" / "cross_modality" / "donor_collapse_conflicts.tsv"
FIMM_DISJOINT = ROOT / "artifacts" / "fimm_consensus" / "cross_modality" / "disjoint_caller_sensitivity.tsv"
FIMM_BB72 = ROOT / "artifacts" / "fimm" / "tierC" / "bb72_metrics.tsv"
FIMM_PANEL_COMPOSITION = {
    "WES": ROOT / "artifacts" / "fimm_consensus" / "FIMM-AML-WES" / "panel3" / "panel_composition.tsv",
    "BULKRNA": ROOT / "artifacts" / "fimm_consensus" / "FIMM-AML-BulkRNA" / "panel3" / "panel_composition.tsv",
    "SCRNA": ROOT / "artifacts" / "fimm_consensus" / "FIMM-AML-SCRNA" / "panel3" / "panel_composition.tsv",
}
VENEX_VALIDATION = ROOT / "artifacts" / "venex" / "caller_validation_summary.tsv"
VENEX_DISSENT = ROOT / "artifacts" / "venex" / "plurality_vs_caller.tsv"
VENEX_COMPOSITION = ROOT / "artifacts" / "venex" / "panel_composition.tsv"
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


def append_exploratory_rows(rows: list[dict[str, str]]) -> None:
    flow_hash_boundary = (
        "Aggregate FIMM cohort flow only; no real specimen or donor identifiers; "
        "exploratory and not accuracy evidence"
    )
    for item in read_rows(FIMM_FLOW):
        count = item["count"]
        rows.append(exploratory_row(
            result_id=f"FIMM_PANEL_FLOW_{slug(item['stage'])}",
            cohort="FIMM_AML_MDS", modality="mixed",
            method="three-caller ChampHLA exploratory application",
            analysis_status="exploratory_descriptive", endpoint=f"cohort_flow_{item['stage']}",
            artifact=FIMM_FLOW, result_kind="categorical-summary", estimate=count,
            unit="count", loci=count if item["stage"].startswith("locus_") else "",
            acquired=count, claim_boundary=flow_hash_boundary,
        ))

    pair_labels = {
        ("FIMM-AML-BulkRNA", "FIMM-AML-WES"): "BULKRNA_WES",
        ("FIMM-AML-SCRNA", "FIMM-AML-WES"): "SCRNA_WES",
        ("FIMM-AML-BulkRNA", "FIMM-AML-SCRNA"): "BULKRNA_SCRNA",
    }
    for item in read_rows(FIMM_CROSS):
        if item["gene"] != "ALL":
            continue
        label = pair_labels[(item["left_cohort"], item["right_cohort"])]
        specimen = item["pairing"] == "specimen"
        contested = item["eligibility"] == "contested_both"
        eligibility_id = "_CONTESTED" if contested else ""
        suffix = "" if specimen else "_SENSITIVITY"
        estimable = int(item["overlap"]) > 0
        status = "exploratory_coequal" if specimen else "exploratory_sensitivity"
        if not estimable:
            status += "_non_estimable"
        eligibility_boundary = (
            "both assays had complete plurality calls and at least two valid callers"
            if contested else
            "both assays had complete plurality calls regardless of valid-caller count"
        )
        boundary = (
            "Exact unordered two-field cross-modality agreement without HLA truth; "
            f"eligibility required {eligibility_boundary}; "
            "the all-callable and contested-both definitions are coequal exploratory views; "
            "shared callers induce correlated agreement"
        )
        if not specimen:
            boundary += (
                "; donor collapse is sensitivity-only and excludes longitudinal conflicts "
                f"({item['left_donor_loci_dropped_as_conflict']} left, "
                f"{item['right_donor_loci_dropped_as_conflict']} right)"
            )
        rows.append(exploratory_row(
            result_id=(f"FIMM_PANEL_{item['pairing'].upper()}{eligibility_id}_"
                       f"{label}_EXACT_PAIR{suffix}"),
            cohort="FIMM_AML_MDS", modality=label.lower(),
            method="SimplePluralityLex three-caller panel",
            analysis_status=status,
            endpoint=f"{item['eligibility']}_exact_unordered_two_field_pair_agreement",
            artifact=FIMM_CROSS, result_kind="concordance",
            estimate=item["estimate"] if estimable else "",
            ci_low=item["ci_lo"] if estimable else "",
            ci_high=item["ci_hi"] if estimable else "", unit="proportion",
            loci=item["overlap"], correct=item["agreement"], intended=item["overlap"],
            acquired=item["overlap"], callable_n=item["overlap"],
            interval_method="Wilson 95%" if estimable else "not estimable",
            claim_boundary=boundary,
        ))

    for item in read_rows(FIMM_DISJOINT):
        label = pair_labels[(item["left_cohort"], item["right_cohort"])]
        rows.append(exploratory_row(
            result_id=f"FIMM_PANEL_DISJOINT_{label}_NON_ESTIMABLE",
            cohort="FIMM_AML_MDS", modality=label.lower(),
            method="caller-disjoint sensitivity",
            analysis_status="exploratory_sensitivity_non_estimable",
            endpoint="caller_disjoint_exact_pair_agreement", artifact=FIMM_DISJOINT,
            result_kind="concordance", unit="proportion", loci="0", correct="0",
            intended="0", acquired="0", callable_n="0",
            claim_boundary=f"Non-estimable with zero overlap: {item['reason']}",
        ))

    for item in read_rows(FIMM_CONFLICTS):
        count = item["donor_locus_conflicts"]
        assay = item["cohort"].replace("FIMM-AML-", "").upper()
        rows.append(exploratory_row(
            result_id=f"FIMM_PANEL_{slug(assay)}_LONGITUDINAL_CONFLICTS",
            cohort="FIMM_AML_MDS", modality=assay.lower(),
            method="conservative donor collapse", analysis_status="exploratory_diagnostic",
            endpoint="longitudinal_conflict_exclusion", artifact=FIMM_CONFLICTS,
            result_kind="categorical-summary", estimate=count, unit="donor-loci",
            loci=count, acquired=count,
            claim_boundary="Conflict count removed by donor collapse; explains optimistic donor-level sensitivity",
        ))

    for assay, path in FIMM_PANEL_COMPOSITION.items():
        panel_rows = read_rows(path)
        denominator = sum(int(item["loci"]) for item in panel_rows)
        for item in panel_rows:
            callers = item["callable_tools"]
            rows.append(exploratory_row(
                result_id=f"FIMM_PANEL_{assay}_CALLABLE_CALLERS_{callers}",
                cohort="FIMM_AML_MDS", modality=assay.lower(),
                method="three-caller ChampHLA exploratory application",
                analysis_status="exploratory_diagnostic", endpoint="callable_caller_composition",
                artifact=path, result_kind="categorical-summary", estimate=item["share"],
                unit="proportion", loci=item["loci"], intended=str(denominator),
                acquired=str(denominator), callable_n=item["loci"],
                claim_boundary=(
                    f"Count and share of locus rows with {callers} valid callers; "
                    "zero is missing-call and one is single-caller evidence, not voting"
                ),
            ))

    metric_parts = {
        "sensitivity": ("tp", "fn"), "specificity": ("tn", "fp"),
        "ppv": ("tp", "fp"), "npv": ("tn", "fn"),
        "accuracy": ("tp_tn", "all"),
    }
    for item in read_rows(FIMM_BB72):
        tp, tn, fp, fn = (int(item[field]) for field in ("tp", "tn", "fp", "fn"))
        if item["metric"] == "accuracy":
            successes, denominator = tp + tn, tp + tn + fp + fn
        else:
            success_field, other_field = metric_parts[item["metric"]]
            successes = int(item[success_field])
            denominator = successes + int(item[other_field])
        mapping = "A02" if item["mapping"] == "A*02" else "A02_A68_A69"
        reported_metric = "agreement" if item["metric"] == "accuracy" else item["metric"]
        rows.append(exploratory_row(
            result_id=f"FIMM_BB72_{slug(item['modality'])}_{mapping}_{slug(reported_metric)}",
            cohort="FIMM_AML_MDS", modality=item["modality"],
            method=f"SimplePluralityLex versus BB7.2 ({item['mapping']})",
            analysis_status=("exploratory_primary" if mapping == "A02" else
                             "exploratory_sensitivity"),
            endpoint=f"bb72_serogroup_{reported_metric}", artifact=FIMM_BB72,
            result_kind="performance", estimate=item["estimate"], ci_low=item["ci_lo"],
            ci_high=item["ci_hi"], unit="proportion", subjects=item["informative"],
            loci=str(denominator), correct=str(successes), intended=item["flow_records_total"],
            acquired=str(int(item["informative"]) + int(item["excluded"])),
            callable_n=item["informative"], interval_method="Wilson 95%",
            claim_boundary=(
                "BB7.2 serogroup agreement only, not allele-level HLA accuracy; "
                f"confusion matrix TP={tp}, TN={tn}, FP={fp}, FN={fn}; "
                f"{item['informative']} informative of {item['flow_records_total']} flow records"
            ),
        ))

    for item in read_rows(VENEX_VALIDATION):
        rows.append(exploratory_row(
            result_id=f"VENEX_WES_{slug(item['caller'])}_{slug(item['status'])}",
            cohort="VENEX_WES", modality="wes", method=item["caller"],
            analysis_status="exploratory_diagnostic", endpoint="caller_output_availability",
            artifact=VENEX_VALIDATION, result_kind="categorical-summary",
            estimate=item["samples"], unit="samples", subjects=item["samples"],
            intended=item["cohort_samples"], acquired=item["samples"],
            claim_boundary="Native caller output availability/failure status; no HLA truth and no accuracy claim",
        ))

    for label, cohort_dir in (("WES", "FIMM-AML-WES"), ("BULKRNA", "FIMM-AML-BulkRNA"),
                              ("SCRNA", "FIMM-AML-SCRNA")):
        dissent = ROOT / "artifacts" / "fimm_consensus" / cohort_dir / "panel3" / "plurality_vs_caller.tsv"
        for item in read_rows(dissent):
            denominator = item["contested_mutually_callable_loci"]
            estimable = int(denominator) > 0
            rows.append(exploratory_row(
                result_id=f"FIMM_PANEL_{label}_{slug(item['caller'])}_CONTESTED_DISSENT",
                cohort=cohort_dir, modality=label.lower(), method=item["caller"],
                analysis_status=("exploratory_diagnostic" if estimable else
                                 "exploratory_diagnostic_non_estimable"),
                endpoint="contested_locus_plurality_dissent", artifact=dissent,
                result_kind="categorical-summary",
                estimate=item["contested_dissent_rate"] if estimable else "",
                ci_low=item["contested_dissent_ci_lo"] if estimable else "",
                ci_high=item["contested_dissent_ci_hi"] if estimable else "",
                unit="proportion", loci=denominator, correct=item["contested_dissents"],
                intended=denominator, acquired=denominator, callable_n=denominator,
                interval_method="Wilson 95%" if estimable else "not estimable",
                claim_boundary=(
                    "Within-panel contested-locus dissent from a plurality that includes "
                    "this caller; aggregate only; not error against truth"),
            ))

    for item in read_rows(VENEX_DISSENT):
        denominator = item["contested_mutually_callable_loci"]
        estimable = int(denominator) > 0
        rows.append(exploratory_row(
            result_id=f"VENEX_WES_{slug(item['caller'])}_CONTESTED_DISSENT",
            cohort="VENEX_WES", modality="wes", method=item["caller"],
            analysis_status=("exploratory_diagnostic" if estimable else
                             "exploratory_diagnostic_non_estimable"),
            endpoint="contested_locus_plurality_dissent", artifact=VENEX_DISSENT,
            result_kind="categorical-summary",
            estimate=item["contested_dissent_rate"] if estimable else "",
            ci_low=item["contested_dissent_ci_lo"] if estimable else "",
            ci_high=item["contested_dissent_ci_hi"] if estimable else "",
            unit="proportion", loci=denominator, correct=item["contested_dissents"],
            intended=denominator, acquired=denominator, callable_n=denominator,
            interval_method="Wilson 95%" if estimable else "not estimable",
            claim_boundary=(
                "Within-panel contested-locus dissent from a plurality that includes this caller; "
                "not error against truth" if estimable else
                "Non-estimable because the caller produced zero mutually callable loci"
            ),
        ))

    for item in read_rows(VENEX_COMPOSITION):
        rows.append(exploratory_row(
            result_id=f"VENEX_WES_CALLABLE_CALLERS_{item['callable_tools']}",
            cohort="VENEX_WES", modality="wes", method="ChampHLA WES panel",
            analysis_status="exploratory_diagnostic", endpoint="callable_caller_composition",
            artifact=VENEX_COMPOSITION, result_kind="categorical-summary",
            estimate=item["share"], unit="proportion", loci=item["loci"],
            intended="258", acquired="258", callable_n=item["loci"],
            claim_boundary="Effective caller-panel composition only; no independent HLA truth",
        ))


def append_restored_rows(rows: list[dict[str, str]]) -> None:
    """Register the analyses restored from the earlier drafts (gap review B1-B4).

    The artifacts are written by scripts/restored_analyses.py from the frozen
    joined development table; they are post hoc and never abstract-eligible.
    """
    boundary = ("Post hoc descriptive analysis restored from the earlier ChampHLA drafts; "
                "development loci only; not external validation")
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
                claim_boundary=(boundary + "; probabilities were calibrated against earlier "
                                "development labels, so this is exploratory"),
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
    append_protocol_change_ledger_row(rows)
    append_mutually_available_rows(rows)
    append_representability_rows(rows)
    append_exploratory_rows(rows)
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
