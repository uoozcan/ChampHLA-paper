"""Rebuild the complete ChampHLA development paper from its release boundary."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import analyse_mutually_available  # noqa: E402
import compare_hg00096_rerun  # noqa: E402
import generate_figures  # noqa: E402
import generate_compute_provenance  # noqa: E402
import generate_manuscript_tables  # noqa: E402
import generate_result_registry  # noqa: E402
import generate_protocol_change_ledger  # noqa: E402
import integration_headroom_and_power  # noqa: E402
import compare_result_registry  # noqa: E402
from champhla_confirmation.characterise import (  # noqa: E402
    characterise_development,
    single_allele_zygosity,
    tie_break_sensitivity,
)
from champhla_confirmation.development import (  # noqa: E402
    PUBLIC_TRUTH_SHA256,
    build_development_predictions,
    combine_predictions,
    identity_check,
    prepare_development_candidate_truth,
    withheld_input_effect,
    prepare_development_truth,
    refit_best_single_caller,
    refit_secondary_fitted_methods,
    score_frozen_nestedcv,
)
from champhla_confirmation.evaluation import (  # noqa: E402
    evaluate,
    evaluate_ambiguity_compatibility,
    evaluate_g_group_compatibility,
    evaluate_p_group_compatibility,
    evaluate_truth_selection,
    write_per_locus_results,
    join_truth,
)
from champhla_confirmation.freeze import freeze_bundle  # noqa: E402
from champhla_confirmation.hla_reference import HLAReference  # noqa: E402
from champhla_confirmation.io import sha256, write_json  # noqa: E402
from champhla_confirmation.representability import evaluate_representability  # noqa: E402
from champhla_recovery.manuscript import audit_claims  # noqa: E402
from champhla_recovery.release import freeze_release, validate_release  # noqa: E402
from champhla_recovery.submission import render_docx, validate_docx_parity  # noqa: E402

RELEASE_BOOTSTRAP = 100_000
RELEASE_POWER_ITERATIONS = 2_000
FIMM_AUTHOR_GATE = ROOT / "configs" / "fimm_submission_gate.json"
def require_file(path: Path, description: str) -> None:
    if not path.is_file():
        raise SystemExit(f"missing {description}: {path}")


def run_checks() -> None:
    subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "-m", "ruff", "check", "src", "scripts", "tests"],
                   cwd=ROOT, check=True)


def render_review_docx() -> None:
    notes = [
        "REVIEW DRAFT - NOT FOR SUBMISSION. Generated reproducibly from Markdown.",
        "Author declarations and submission details await confirmation; see AUTHOR_FIELDS_TO_COMPLETE.md.",
        "Scientific results are retrospective development evidence; no external validation is claimed.",
    ]
    documents = (
        ("manuscript.md", "ChampHLA_manuscript_REVIEW_DRAFT.docx",
         "ChampHLA benchmark and plurality baseline"),
        ("supplementary.md", "ChampHLA_supplementary_REVIEW_DRAFT.docx",
         "ChampHLA supplementary material"),
    )
    for source_name, output_name, title in documents:
        source = ROOT / "manuscripts" / "benchmark" / source_name
        output = ROOT / "manuscripts" / "benchmark" / output_name
        render_docx(str(source), str(output), figures_dir=str(ROOT / "figures"),
                    strip_result_tags=True, header_note=notes, title=title)
        parity = validate_docx_parity(str(source), str(output),
                                      figures_dir=str(ROOT / "figures"),
                                      strip_result_tags=True)
        if parity["failures"]:
            raise RuntimeError(
                f"{source_name} DOCX parity failed: " + "; ".join(parity["failures"])
            )


def fitted_stage(calls: Path, truth: Path, secondary: Path, policy: Path,
                 truth_free: Path, truth_free_freeze: Path,
                 workdir: Path) -> tuple[Path, Path]:
    """decisions/20261009_nestedcv_refit.json: the truth-free predictions keep their
    pre-truth freeze; the refit is frozen as its own stage; the evaluated file pins both."""
    nested = workdir / "development_nestedcv_predictions.tsv"
    refit_best_single_caller(str(calls), str(truth), str(secondary), str(nested),
                             str(workdir / "development_nestedcv_manifest.json"))
    secondary_fitted = workdir / "development_secondary_fitted_predictions.tsv"
    refit_secondary_fitted_methods(
        str(calls), str(truth), str(secondary), str(policy), str(secondary_fitted),
        str(workdir / "development_secondary_fitted_manifest.json"),
    )
    fitted = workdir / "development_fitted_predictions.tsv"
    combine_predictions([str(nested), str(secondary_fitted)], str(fitted))
    fitted_freeze = workdir / "development_fitted_freeze.json"
    freeze_bundle(ROOT, {"predictions": fitted}, fitted_freeze)
    combined = workdir / "development_predictions_combined.tsv"
    combine_predictions([str(truth_free), str(fitted)], str(combined))
    combined_freeze = workdir / "development_predictions_combined_freeze.json"
    freeze_bundle(ROOT, {
        "predictions": combined,
        "truth_free_predictions": truth_free, "truth_free_freeze": truth_free_freeze,
        "fitted_predictions": fitted, "fitted_freeze": fitted_freeze,
    }, combined_freeze)
    return combined, combined_freeze


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-truth", required=True,
                        help="downloaded 20140702_hla_diversity.txt with the pinned checksum")
    parser.add_argument("--bootstrap", type=int, default=RELEASE_BOOTSTRAP)
    parser.add_argument("--power-iterations", type=int, default=RELEASE_POWER_ITERATIONS)
    parser.add_argument("--release", action="store_true",
                        help="enforce full precision, tests, lint, audits, DOCX parity and freeze")
    parser.add_argument("--submission", action="store_true",
                        help="also fail on author/archive placeholders")
    parser.add_argument("--skip-tests", action="store_true",
                        help="developer-only; forbidden with --release")
    parser.add_argument("--restored-caller-source",
                        help="recovered harmonized_population_enriched.tsv; reruns the S12 "
                             "restored analyses (required with --release)")
    args = parser.parse_args()
    input_manifest = ROOT / "data" / "development" / "input_manifest.json"
    # S12 is an analysis of the historical stored outputs. On the v3.5.0 rerun inputs
    # its committed artifacts are kept as labelled historical provenance and are never
    # recomputed from rerun calls (author decision of 2026-10-25).
    rerun_inputs = input_manifest.is_file() and json.loads(
        input_manifest.read_text(encoding="utf-8")
    ).get("schema_version") == "champhla-development-rerun-inputs-1"
    if args.release and not args.restored_caller_source and not rerun_inputs:
        raise SystemExit("--release regenerates every artifact and needs "
                         "--restored-caller-source for the S12 restored analyses")

    if sys.version_info < (3, 11):
        raise SystemExit(f"Python 3.11+ is required; found {sys.version.split()[0]}")
    if args.release and sys.version_info[:3] != (3, 11, 15):
        raise SystemExit(
            "release mode requires Python 3.11.15 exactly; "
            f"found {sys.version.split()[0]}"
        )
    if args.release and args.skip_tests:
        raise SystemExit("--release forbids --skip-tests")
    if args.release and args.bootstrap != RELEASE_BOOTSTRAP:
        raise SystemExit(f"--release requires --bootstrap {RELEASE_BOOTSTRAP}")
    if args.release and args.power_iterations < RELEASE_POWER_ITERATIONS:
        raise SystemExit(
            f"--release requires --power-iterations >= {RELEASE_POWER_ITERATIONS}"
        )

    public_truth = Path(args.public_truth).resolve()
    require_file(public_truth, "public truth source")
    observed_truth_hash = sha256(public_truth)
    if observed_truth_hash != PUBLIC_TRUTH_SHA256:
        raise SystemExit(
            f"public truth checksum mismatch: expected {PUBLIC_TRUTH_SHA256}, "
            f"observed {observed_truth_hash}"
        )

    data = ROOT / "data" / "development"
    runtime = ROOT / "runtime_data"
    corrected = ROOT / "artifacts" / "development_corrected"
    character = ROOT / "artifacts" / "development_characterisation"
    limits = ROOT / "artifacts" / "development_limits"
    character.mkdir(parents=True, exist_ok=True)
    calls = data / "normalized_caller_calls.tsv"
    secondary = data / "normalized_secondary_calls.tsv"
    policy = data / "frozen_raw_cc_policy.json"
    for path, description in ((calls, "normalized caller input"),
                              (secondary, "normalized secondary input"),
                              (policy, "frozen exploratory policy")):
        require_file(path, description)
    runtime.mkdir(parents=True, exist_ok=True)
    truth = runtime / "development_truth.tsv"
    truth_manifest = runtime / "development_truth_manifest.json"
    candidate_truth = runtime / "development_candidate_truth.tsv"
    candidate_truth_manifest = runtime / "development_candidate_truth_manifest.json"
    predictions = runtime / "development_predictions.tsv"
    prediction_manifest = runtime / "development_predictions_manifest.json"
    prediction_freeze = runtime / "development_prediction_freeze.json"
    joined = runtime / "joined_development.tsv"
    join_manifest = runtime / "development_join_manifest.json"

    print("== truth-free sample-identity check ==")
    identity_check([str(calls), str(data / "excluded_caller_calls.tsv")],
                   str(ROOT / "cohorts" / "official_1000g_assay_manifest.tsv"),
                   str(character / "identity_check.tsv"))
    print("== HG00096 stored calls vs a workflow re-run (truth-free) ==")
    compare_hg00096_rerun.main()
    print("== regenerate truth-free predictions over the requested roster ==")
    build_development_predictions(str(calls), str(secondary), None, str(policy),
                                  str(predictions), str(prediction_manifest))
    freeze_bundle(ROOT, {"predictions": predictions}, prediction_freeze)
    print("== build exact and set-valued truth after the prediction freeze ==")
    prepare_development_truth(str(public_truth), str(calls), str(truth), str(truth_manifest))
    prepare_development_candidate_truth(
        str(public_truth), str(calls), str(candidate_truth), str(candidate_truth_manifest)
    )
    print("== fitted stage: nested-CV refit on training-fold truth, frozen separately ==")
    score_frozen_nestedcv(str(secondary), str(truth),
                          str(corrected / "frozen_nestedcv_legacy.tsv"))
    predictions, prediction_freeze = fitted_stage(
        calls, truth, secondary, policy, predictions, prediction_freeze, runtime)
    joined.unlink(missing_ok=True)
    join_manifest.unlink(missing_ok=True)
    print("== deterministic truth join and evaluation ==")
    join_truth(str(predictions), str(truth), str(prediction_freeze), str(joined),
               str(join_manifest), allow_prediction_superset=True)
    evaluate(str(joined), str(corrected), args.bootstrap, 20260831, True, "discovery")
    write_per_locus_results(str(joined), str(corrected / "per_locus_results.tsv"))
    print("== fixed-denominator and mutually-available caller comparisons ==")
    analyse_mutually_available.main()
    print("== bounded current-deployment native-list representability ==")
    evaluate_representability(
        str(truth), str(ROOT / "resources" / "caller_native" / "MANIFEST.json"),
        str(character / "caller_truth_representability.tsv"),
        str(character / "caller_truth_representability.json"),
    )
    generate_protocol_change_ledger.main()
    print("== identity sensitivity: withheld inputs scored, never used to exclude ==")
    withheld_input_effect(str(data / "excluded_caller_calls.tsv"), str(public_truth),
                          str(runtime / "withheld_inputs"),
                          str(character / "identity_withheld_effect.tsv"))
    print("== singleton sensitivity: every single-allele call abstains ==")
    # decisions/20261008_singleton_native_homozygosity.json: the primary inputs honour
    # caller-native homozygous declarations; this pass reports the abstain-all scoring
    # beside it, through the same prediction, freeze, join and evaluation code.
    sensitivity_calls = data / "sensitivity_abstain" / "normalized_caller_calls.tsv"
    require_file(sensitivity_calls, "abstain-all sensitivity caller input")
    sensitivity = runtime / "sensitivity_abstain"
    sensitivity.mkdir(parents=True, exist_ok=True)
    sens_predictions = sensitivity / "development_predictions.tsv"
    sens_freeze = sensitivity / "development_prediction_freeze.json"
    sens_joined = sensitivity / "joined_development.tsv"
    sens_join_manifest = sensitivity / "development_join_manifest.json"
    build_development_predictions(str(sensitivity_calls), str(secondary), None, str(policy),
                                  str(sens_predictions),
                                  str(sensitivity / "development_predictions_manifest.json"))
    freeze_bundle(ROOT, {"predictions": sens_predictions}, sens_freeze)
    sens_predictions, sens_freeze = fitted_stage(
        sensitivity_calls, truth, secondary, policy, sens_predictions, sens_freeze, sensitivity)
    sens_joined.unlink(missing_ok=True)
    sens_join_manifest.unlink(missing_ok=True)
    join_truth(str(sens_predictions), str(truth), str(sens_freeze), str(sens_joined),
               str(sens_join_manifest), allow_prediction_superset=True)
    evaluate(str(sens_joined), str(ROOT / "artifacts" / "development_sensitivity_abstain"),
             args.bootstrap, 20260831, True, "discovery")
    evaluate_ambiguity_compatibility(
        str(predictions), str(candidate_truth), str(prediction_freeze),
        str(character / "ambiguity_compatibility.tsv"), args.bootstrap, 20260925,
    )
    evaluate_truth_selection(
        str(predictions), str(candidate_truth), str(prediction_freeze),
        str(character / "truth_selection_compatibility.tsv"),
        str(character / "truth_selection_profile.tsv"), args.bootstrap, 20260925,
    )
    ipd = ROOT / "resources" / "ipd_imgt_hla" / "3.65.0"
    reference = HLAReference.from_files(
        "3.65.0", ipd / "Allelelist.txt",
        deleted_alleles=ipd / "Deleted_alleles.txt",
        p_groups=ipd / "wmda" / "hla_nom_p.txt",
        g_groups=ipd / "wmda" / "hla_nom_g.txt",
    )
    evaluate_g_group_compatibility(
        str(predictions), str(candidate_truth), str(prediction_freeze),
        str(character / "g_group_compatibility.tsv"), reference,
        args.bootstrap, 20260925,
    )
    evaluate_p_group_compatibility(
        str(predictions), str(candidate_truth), str(prediction_freeze),
        str(character / "p_group_compatibility.tsv"), reference,
        args.bootstrap, 20260925,
    )
    characterise_development(
        str(joined), str(truth_manifest), str(character), str(candidate_truth), reference
    )
    tie_break_sensitivity(str(joined), str(character / "tie_break_sensitivity.tsv"))
    single_allele_zygosity(str(calls), str(truth),
                           str(character / "single_allele_zygosity.tsv"))
    integration_headroom_and_power.main(
        ["integration_headroom_and_power.py", str(joined), str(limits),
         str(args.power_iterations)]
    )
    second_typing = runtime / "public_truth" / "20181129_HLA_types_full_1000_Genomes_Project_panel.txt"
    if second_typing.is_file():
        # decisions/20261009_reference_adjudication.json: the script checks the pinned
        # SHA-256 and never reads extension subjects.
        print("== second-typing adjudication ==")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "adjudicate_reference_discordance.py"),
                        str(joined), str(second_typing)], check=True)
    elif args.release:
        raise SystemExit(f"--release needs the second typing for the adjudication: {second_typing}")
    else:
        print("== second-typing adjudication not rerun: file absent ==")
    if rerun_inputs:
        print("== restored analyses (S12): historical stored-output provenance, not rerun ==")
    elif args.restored_caller_source:
        # S12 reads the joined table written above, so it must run before the
        # registry; without it the committed S12 artifacts are used unchanged.
        print("== restored analyses (S12) ==")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "restored_analyses.py"),
                        "--caller-source", args.restored_caller_source], check=True)
    else:
        print("== restored analyses (S12) not rerun: no --restored-caller-source ==")
    print("== compute provenance and result registry ==")
    generate_compute_provenance.main()
    generate_result_registry.main()
    input_manifest = ROOT / "data/development/input_manifest.json"
    input_schema = ""
    if input_manifest.is_file():
        input_schema = json.loads(input_manifest.read_text(encoding="utf-8")).get(
            "schema_version", ""
        )
    if input_schema == "champhla-development-rerun-inputs-1":
        provenance = ROOT / "provenance/development_rerun_v350"
        old_registry = provenance / "historical_result_registry_pre_v350.tsv"
        require_file(old_registry, "pre-v3.5.0 result registry archived at activation")
        delta_rows, delta_summary = compare_result_registry.compare(
            old_registry, ROOT / "result_registry.tsv"
        )
        compare_result_registry.write_reports(delta_rows, delta_summary, provenance)
        # Each signed approval binds one exact registry; later amendments add new
        # records rather than editing an earlier one.
        approvals = sorted((ROOT / "decisions").glob("20261025_rerun_registry_delta_approved*.json"))
        approval = next((
            record for record in approvals
            if compare_result_registry.approval_matches(
                delta_summary, ROOT / "result_registry.tsv", record)
        ), None)
        if delta_summary["author_approval_required"] and approval is None:
            raise SystemExit(
                "rerun analysis completed, but manuscript finalization stopped for author "
                "approval; see provenance/development_rerun_v350/result_registry_delta.md"
            )
        if delta_summary["author_approval_required"]:
            print(f"== registry delta approved by the author: {approval.relative_to(ROOT)} ==")
    print("== figures and manuscript tables ==")
    generate_figures.main(["generate_figures.py", str(ROOT / "figures")])
    generate_manuscript_tables.main()
    render_review_docx()

    if not args.skip_tests:
        print("== tests and lint ==")
        run_checks()

    print("== manuscript claim audits ==")
    audit_results = []
    for name in ("manuscript.md", "supplementary.md"):
        audit_results.append(audit_claims(
            str(ROOT / "manuscripts" / "benchmark" / name),
            str(ROOT / "result_registry.tsv"),
            str(ROOT / "manuscripts" / "claim_audit.tsv"),
            str(ROOT / "artifacts" / f"benchmark_{name.removesuffix('.md')}_audit.json"),
            str(ROOT),
            author_gate=str(FIMM_AUTHOR_GATE),
        ))
    scientific_failures = sorted({failure for result in audit_results
                                  for failure in result["blocking_failures"]})
    author_blockers = sorted({marker for result in audit_results
                              for marker in result["pending_author_input"]})
    author_gate_statuses = sorted({result["author_gate_status"] for result in audit_results
                                   if result["author_gate_status"]})
    if scientific_failures:
        raise SystemExit("scientific claim audit failed: " + "; ".join(scientific_failures))
    if args.submission and author_blockers:
        raise SystemExit("submission blocked by author input: " + ", ".join(author_blockers))

    gate = {
        "schema_version": "panelhla-publication-readiness-1",
        "scientific_failures": scientific_failures,
        "author_archive_input_required": bool(author_blockers),
        "author_archive_markers": author_blockers,
        "author_gate": FIMM_AUTHOR_GATE.relative_to(ROOT).as_posix(),
        "author_gate_statuses": author_gate_statuses,
        "unresolved_author_gate_items": [
            item.removeprefix("FIMM: ") for item in author_blockers
            if item.startswith("FIMM: ")
        ],
        "public_truth_sha256": observed_truth_hash,
        "bootstrap_iterations": args.bootstrap,
        "power_iterations": args.power_iterations,
        "status": "author_input_required" if author_blockers else "technically_ready",
    }
    write_json(ROOT / "artifacts" / "publication_readiness_gate.json", gate)

    if args.release:
        print("== release freeze (last write) ==")
        manifest = ROOT / "artifacts" / "release_freeze.json"
        freeze_release(str(ROOT), str(manifest))
        validation = validate_release(str(ROOT), str(manifest))
        if not validation["valid"]:
            raise SystemExit(f"release freeze validation failed: {validation}")

    print(f"publication gate: {gate['status']}; scientific failures=0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
