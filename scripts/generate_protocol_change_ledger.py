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
            "change": "Pre-register and run abstention on every singleton caller output",
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
            "direction_and_size": "RNA-seq plurality 110/118 on current truth-retained loci under abstain-all scoring",
            "verdict_effect": "Lowered the RNA-seq headline; non-inferiority remained sensitivity-only",
            "truth_exposure": "After development results had been seen",
            "decision_record": "decisions/20260924_publication_remediation.json",
            "evidence_artifact": "artifacts/development_sensitivity_abstain/method_performance.tsv",
        },
        {
            "date": "2026-09-28",
            "change_id": "truth_and_inference_amendment",
            "change": "Fail-closed truth parser; prediction freeze; CR1 cluster-t test; separate descriptive/fitted Holm families",
            "direction_and_size": "Exact denominators became 153 WES and 120 RNA-seq before later identity withholding",
            "verdict_effect": "Four comparisons significant under the declared family structure; development status remained post hoc",
            "truth_exposure": "After earlier analyses had joined truth to the same caller outputs",
            "decision_record": "decisions/20260928_truth_and_inference_amendment.json",
            "evidence_artifact": "artifacts/development_corrected/secondary_method_results.tsv",
        },
        {
            "date": "2026-10-08",
            "change_id": "caller_native_homozygosity",
            "change": "Implement caller-native homozygous completion; keep abstain-all sensitivity",
            "direction_and_size": "RNA-seq plurality 110 to 113; HLA-HD RNA-seq 97 to 110; arcasHLA 95 to 109; HLA-HD WES 110 to 126",
            "verdict_effect": "Raised RNA-seq headline and changed strongest RNA-seq caller from OptiType to HLA-HD",
            "truth_exposure": "Rule implementation corrected after consequences were known",
            "decision_record": "decisions/20261008_singleton_native_homozygosity.json",
            "evidence_artifact": "artifacts/development_corrected/method_performance.tsv;artifacts/development_sensitivity_abstain/method_performance.tsv",
        },
        {
            "date": "2026-10-08",
            "change_id": "na07000_withheld",
            "change": "Withhold NA07000 RNA-seq after truth-free sample-identity failure",
            "direction_and_size": "RNA-seq plurality 113/120 to 113/118; both removed loci were errors",
            "verdict_effect": "Raised RNA-seq proportion by reducing the denominator; numerator unchanged",
            "truth_exposure": "Identity decision used truth-free cross-assay calls, but development outcomes were already known",
            "decision_record": "decisions/20261008_identity_check_na07000.json",
            "evidence_artifact": "artifacts/development_characterisation/identity_withheld_effect.tsv",
        },
        {
            "date": "2026-10-09",
            "change_id": "nested_cv_refit",
            "change": "Refit nested-CV best-caller comparator under current truth and call-state rules",
            "direction_and_size": "RNA-seq comparator 99/118 to 106/118",
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
