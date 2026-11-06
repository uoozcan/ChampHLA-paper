"""Generate the protocol-change ledger required by SR-019."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIMARY = ROOT / "artifacts" / "development_corrected" / "primary_modality_results.tsv"
OUTPUT = ROOT / "artifacts" / "protocol_change_ledger.tsv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


HISTORICAL_COUNTS = ("142", "143", "113", "113")
INPUT_MANIFEST = ROOT / "data" / "development" / "input_manifest.json"
RERUN_INPUT_SCHEMA = "champhla-development-rerun-inputs-1"


def rerun_inputs_active() -> bool:
    import json
    if not INPUT_MANIFEST.is_file():
        return False
    manifest = json.loads(INPUT_MANIFEST.read_text(encoding="utf-8"))
    return manifest.get("schema_version") == RERUN_INPUT_SCHEMA


def main() -> int:
    current = {row["modality"]: row for row in read_rows(PRIMARY)}
    counts = (
        current["wes"]["guarded_correct"],
        current["wes"]["plurality_correct"],
        current["rnaseq"]["guarded_correct"],
        current["rnaseq"]["plurality_correct"],
    )
    # The historical rows describe the stored outputs and stay fixed. On the historical
    # inputs the current artifact must still reproduce them; once the v3.5.0 rerun is the
    # primary evidence (decisions/20261013_workflow_rerun_primary.json) its counts are
    # read from the artifact into the rerun row instead of being typed.
    rerun = rerun_inputs_active()
    if not rerun and counts != HISTORICAL_COUNTS:
        raise SystemExit("current frozen-primary/vote counts drifted; update the ledger deliberately")
    endpoint_label = "Historical stored-output endpoint" if rerun else "Current endpoint"
    if rerun:
        wes, rna = current["wes"], current["rnaseq"]
        rerun_size = (
            f"v3.5.0 rerun endpoint: guarded {wes['guarded_correct']}/{wes['loci']} versus "
            f"plurality {wes['plurality_correct']}/{wes['loci']} WES; guarded "
            f"{rna['guarded_correct']}/{rna['loci']} versus plurality "
            f"{rna['plurality_correct']}/{rna['loci']} RNA-seq; historical 142/143 and "
            "112/112 remain checksums only"
        )
        rerun_effect = (
            "The reproducible v3.5.0 rerun replaced the historical stored outputs as the "
            "primary development evidence; extension and final headlines follow"
        )
        rerun_artifact = (
            "artifacts/development_corrected/primary_modality_results.tsv;"
            "provenance/development_rerun_v350/activation_report.json"
        )
    else:
        rerun_size = ("Pending rerun; historical 142/143 and 112/112 remain checksums and "
                      "are not assumed for the new run")
        rerun_effect = ("Final exact and corrected-reference headlines are blocked until "
                        "rerun and extension complete")
        rerun_artifact = "artifacts/workflow_release/PanelHLA-3.5.0.json"

    rows = [
        {
            "date": "2026-08-31",
            "change_id": "frozen_protocol",
            "change": "Freeze TwoThirdsGuardedCC as primary; require it to outperform; Holm across WGS/WES/RNA-seq",
            "direction_and_size": f"{endpoint_label}: guarded 142/153 versus plurality 143/153 WES; tied 113/118 RNA-seq",
            "verdict_effect": "Frozen primary failed to outperform: WES Holm p=1.0 against plurality; RNA-seq exact tie",
            "truth_exposure": "Before the confirmation protocol truth join, but not before analysts first saw truth: earlier truth on these caller outputs fitted champions and weights",
            "decision_record": "configs/confirmation_protocol.json",
            "evidence_artifact": "artifacts/development_corrected/primary_modality_results.tsv;artifacts/development_corrected/secondary_method_results.tsv",
        },
        {
            "date": "2026-09-08 (signed 2026-09-18)",
            "change_id": "plurality_primary",
            "change": "Make equal-weight plurality primary; Holm within assay; exclude invalid WGS",
            "direction_and_size": "Changed the primary method after per-method accuracy was inspected; exact WES +1 correct versus frozen primary, RNA-seq unchanged",
            "verdict_effect": "Primary claim changed from superiority of a fitted rule to audited performance of plurality",
            "truth_exposure": "After development truth and method accuracies had been seen",
            "decision_record": "decisions/20260908_consensus_primary_amendment.json",
            "evidence_artifact": "artifacts/development_corrected/method_performance.tsv",
        },
        {
            "date": "2026-09-18",
            "change_id": "abstention_test",
            "change": "Record and run abstention on every singleton caller output",
            "direction_and_size": "Lowered concordance; result not adopted at that time",
            "verdict_effect": "No primary change; retained as sensitivity",
            "truth_exposure": "After development results had been seen",
            "decision_record": "decisions/20260918_harmonisation_correction_result.json",
            "evidence_artifact": "artifacts/development_sensitivity_abstain/method_performance.tsv",
        },
        {
            "date": "2026-09-24",
            "change_id": "singleton_abstention_policy",
            "change": "Adopt singleton abstention as then implemented; add post hoc 2-point non-inferiority margin",
            "direction_and_size": "Historical stored outputs: RNA-seq plurality 110/118 on current truth-retained loci under abstain-all scoring",
            "verdict_effect": "Lowered the RNA-seq headline; non-inferiority remained sensitivity-only",
            "truth_exposure": "After development results had been seen",
            "decision_record": "decisions/20260924_publication_remediation.json",
            "evidence_artifact": "artifacts/development_sensitivity_abstain/method_performance.tsv",
        },
        {
            "date": "2026-09-28",
            "change_id": "truth_and_inference_amendment",
            "change": "Fail-closed truth parser; prediction freeze; CR1 cluster-t test; separate descriptive/fitted Holm families",
            "direction_and_size": "Historical stored outputs: exact denominators became 153 WES and 120 RNA-seq before later identity withholding",
            "verdict_effect": "Four comparisons significant under the declared family structure; development status remained post hoc",
            "truth_exposure": "After earlier analyses had joined truth to the same caller outputs",
            "decision_record": "decisions/20260928_truth_and_inference_amendment.json",
            "evidence_artifact": "artifacts/development_corrected/secondary_method_results.tsv",
        },
        {
            "date": "2026-10-08",
            "change_id": "caller_native_homozygosity",
            "change": "Implement caller-native homozygous completion; keep abstain-all sensitivity",
            "direction_and_size": "Historical stored outputs: RNA-seq plurality 110 to 113; HLA-HD RNA-seq 97 to 110; arcasHLA 95 to 109; HLA-HD WES 110 to 126",
            "verdict_effect": "Raised RNA-seq headline and changed strongest RNA-seq caller from OptiType to HLA-HD",
            "truth_exposure": "Rule implementation corrected after consequences were known",
            "decision_record": "decisions/20261008_singleton_native_homozygosity.json",
            "evidence_artifact": "artifacts/development_corrected/method_performance.tsv;artifacts/development_sensitivity_abstain/method_performance.tsv",
        },
        {
            "date": "2026-10-08",
            "change_id": "na07000_withheld",
            "change": "Withhold NA07000 RNA-seq after truth-free sample-identity failure",
            "direction_and_size": "Historical stored outputs: RNA-seq plurality 113/120 to 113/118; both removed loci were errors",
            "verdict_effect": "Raised RNA-seq proportion by reducing the denominator; numerator unchanged",
            "truth_exposure": "Identity decision used truth-free cross-assay calls, but development outcomes were already known",
            "decision_record": "decisions/20261008_identity_check_na07000.json",
            "evidence_artifact": "artifacts/development_characterisation/identity_withheld_effect.tsv",
        },
        {
            "date": "2026-10-09",
            "change_id": "nested_cv_refit",
            "change": "Refit nested-CV best-caller comparator under current truth and call-state rules",
            "direction_and_size": "Historical stored outputs: RNA-seq comparator 99/118 to 106/118",
            "verdict_effect": "Comparison became non-significant after Holm adjustment (p=0.188 in the recorded analysis)",
            "truth_exposure": "Post hoc refit using development truth within training folds",
            "decision_record": "decisions/20261009_nestedcv_refit.json",
            "evidence_artifact": "artifacts/development_corrected/frozen_nestedcv_legacy.tsv;artifacts/development_corrected/secondary_method_results.tsv",
        },
        {
            "date": "2026-10-09",
            "change_id": "signflip_governs",
            "change": "Make subject sign-flip, rather than CR1 cluster-t, govern significance",
            "direction_and_size": "No result count changed",
            "verdict_effect": "Same four comparisons significant under both tests at the time",
            "truth_exposure": "Adopted after development results and both test outputs were available",
            "decision_record": "decisions/20261009_signflip_governs.json",
            "evidence_artifact": "artifacts/development_corrected/secondary_method_results.tsv",
        },
        {
            "date": "2026-10-09 to 2026-10-12",
            "change_id": "second_typing_adjudication",
            "change": "Add signed second-typing adjudication, then correct the documented asterisk interpretation",
            "direction_and_size": "No registered primary count changed; historical corrected-reference vote checksums 142/143 WES and 112/112 RNA-seq",
            "verdict_effect": "Reference-corrected sensitivity must accompany exact results; it does not replace the primary endpoint",
            "truth_exposure": "Rules and correction recorded after development discordances and source values were inspected",
            "decision_record": "decisions/20261009_reference_adjudication.json;decisions/20261012_second_typing_asterisk_documented.json",
            "evidence_artifact": "artifacts/development_characterisation/reference_agreement_sensitivity.tsv",
        },
        {
            "date": "2026-10-13",
            "change_id": "v3_5_reproducible_rerun",
            "change": "Correct T1K deployment and make the full reproducible v3.5.0 rerun the primary development evidence",
            "direction_and_size": rerun_size,
            "verdict_effect": rerun_effect,
            "truth_exposure": "Locked after all historical development and adjudication results were known; extension truth remains sealed",
            "decision_record": "decisions/20261013_publication_remediation_scope.json",
            "evidence_artifact": rerun_artifact,
        },
        {
            "date": "2026-10-13 to 2026-10-25",
            "change_id": "rerun_caller_effects",
            "change": "Replace archived caller outputs with the v3.5.0 rerun as the scored calls",
            "direction_and_size": "Historical to rerun, correct loci: arcasHLA 109 to 58; HLA-HD WES 126 to 131 and RNA-seq 110 to 112; OptiType WES 140 to 142 and RNA-seq 109 to 112; POLYSOLVER 143 to 138; SpecHLA 123 to 134; T1K WES 113 to 125 and RNA-seq 91 to 101",
            "verdict_effect": "Vote unchanged at 143/153 and 113/118; the strongest WES caller changed from POLYSOLVER to OptiType; the arcasHLA fall created one of the four significant comparisons",
            "truth_exposure": "Scores from the archived outputs were known before the rerun; the rerun's scores were first seen at the registry delta",
            "decision_record": "decisions/20261013_workflow_rerun_primary.json",
            "evidence_artifact": "provenance/development_rerun_v350/historical_result_registry_pre_v350.tsv;artifacts/development_corrected/method_performance.tsv",
        },
        {
            "date": "2026-10-25",
            "change_id": "native_homozygote_collection_fix",
            "change": "Correct the collector so caller-declared homozygotes are completed; repeat collection and regeneration once",
            "direction_and_size": "RNA-seq vote 112/118 to 113/118; HLA-HD 98/118 to 112/118; arcasHLA 55/118 to 58/118; vote margin over OptiType 0 to +1 locus",
            "verdict_effect": "Restores the signed 8 October singleton policy; no rule changed; the earlier activation is kept as superseded provenance",
            "truth_exposure": "Truth-derived singleton-sensitivity rows prompted the inspection; the defect was then confirmed from caller-output fields",
            "decision_record": "decisions/20261025_rerun_native_homozygote_collection.json",
            "evidence_artifact": "provenance/development_rerun_v350_superseded_20261025/result_registry_delta.tsv;artifacts/development_corrected/method_performance.tsv",
        },
        {
            "date": "2026-10-25",
            "change_id": "arcashla_report_as_is",
            "change": "Report the arcasHLA deployment as run; make no module change",
            "direction_and_size": "No result changed; arcasHLA stays at 58/118 in the primary registry",
            "verdict_effect": "The estimate describes that deployment rather than the caller; any later change needs a signed amendment and a labelled sensitivity",
            "truth_exposure": "Diagnosed only after the truth-derived registry delta had been seen; the diagnosis used container contents, module code and caller outputs",
            "decision_record": "decisions/20261025_arcashla_report_as_is.json",
            "evidence_artifact": "artifacts/development_corrected/method_performance.tsv",
        },
        {
            "date": "2026-11-05",
            "change_id": "patient_cohorts_removed",
            "change": "Remove the FIMM and VenEx patient cohorts from the paper",
            "direction_and_size": "No development result changed; aggregate agreement and dissent results no longer reported",
            "verdict_effect": "The cohorts supported no claim; removal reverses the signed choice to block submission rather than remove them, and the S8 table records it",
            "truth_exposure": "Their aggregate results were known when they were removed; the removal does not rest on their direction",
            "decision_record": "decisions/20261105_patient_cohorts_removed.json",
            "evidence_artifact": "result_registry.tsv",
        },
        {
            "date": "2026-11-06",
            "change_id": "posthoc_round3",
            "change": "Remove the post hoc non-inferiority margin and power projection; add post hoc error counts, naive baselines, intersected duplicate rows, a pedigree relatedness check with family-clustered tests, allele-level vote and abstention trade-off; recompute S12.1-S12.3 on study-run calls; correct three HG00096 rows",
            "direction_and_size": "No primary or comparator result changed; HG00096 rows now match the S10 text; S12 per-gene totals now equal Table 2",
            "verdict_effect": "None; the additions are descriptive and select nothing",
            "truth_exposure": "Proposed by a review that had recomputed these from development truth; the expected values were stated before one run",
            "decision_record": "decisions/20261106_posthoc_round3_amendment.json",
            "evidence_artifact": "result_registry.tsv",
        },
        {
            "date": "2026-11-06",
            "change_id": "posthoc_round4",
            "change": "Add post hoc run-stability rows (archived outputs against study runs) behind one Limitations sentence; correct the Figure 1A text, mark arcasHLA in Figures 2-3 and align the Figure S6 and Table S10.2 labels",
            "direction_and_size": "No primary or comparator result changed; the vote scored 143/153 and 113/118 in both runs",
            "verdict_effect": "None; the rows are descriptive and select nothing",
            "truth_exposure": "The archived-versus-study-run scores had been seen in the ledger and the review; the expected values were stated before one run",
            "decision_record": "decisions/20261106_posthoc_round4_amendment.json",
            "evidence_artifact": "artifacts/development_characterisation/run_stability_posthoc.tsv",
        },
        {
            "date": "2026-11-06",
            "change_id": "cohort_rows_withheld",
            "change": "Withhold the FIMM and VenEx aggregate rows from the published provenance copies",
            "direction_and_size": "No result changed; the gate's archived registry has 532 of its 631 rows",
            "verdict_effect": "None; the unfiltered files stay in the private repository",
            "truth_exposure": "None new; the rows were found by their cohort labels and no value in them was used",
            "decision_record": "decisions/20261106_public_snapshot_scope.json",
            "evidence_artifact": "provenance/cohort_rows_withheld_20261106.json",
        },
        {
            "date": "2026-11-06",
            "change_id": "roihu_descriptions_round5",
            "change": "Describe the study runs' caller deployment, input read length and exon depth, read rescue counts and compute from their archived records",
            "direction_and_size": "No result changed; every T1K task in both assays used the genomic index",
            "verdict_effect": "None; the descriptions are truth-free and select nothing",
            "truth_exposure": "None; requested by a review that had seen all development results, and no reference typing was read",
            "decision_record": "decisions/20261106_roihu_descriptions_round5.json",
            "evidence_artifact": "artifacts/development_characterisation/round5_caller_deployment.tsv;artifacts/development_characterisation/round5_run_cost.tsv",
        },
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(rows)} changes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
