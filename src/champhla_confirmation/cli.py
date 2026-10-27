from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .audit import audit_wgs
from .cohorts import build_overlap_crosswalk
from .characterise import characterise_development
from .consensus import build_guarded_cc
from .development import (build_development_predictions, fetch_public_truth,
                          prepare_development_inputs, prepare_development_truth)
from .evaluation import capacity, evaluate, evaluate_ambiguity_compatibility, join_truth
from .external import build_hprc_release2_candidates, select_hprc_confirmation_roster
from .freeze import freeze_bundle, validate_freeze
from .hla_reference import HLAReference
from .io import (SINGLETON_POLICIES, read_json, read_tsv, reject_truth_columns, sha256,
                 write_json, write_tsv)
from .panels import METHOD_GUARDED_CC, METHOD_RAW_CC
from .power import simulate
from .protocol import validate_benchmark_resource_protocol
from .representability import evaluate_representability
from .public_reads import (
    build_ihwg_provenance_review_packet,
    finalize_ihwg_read_roster,
    sanitize_ihwg_registry,
    scout_ihwg_public_reads,
)
from .raw_cc import freeze_raw_cc_policy, predict_raw_cc
from .readiness import audit_extension_readiness
from .schema import explode_candidate_rows, normalize_caller_row, normalize_method_row, normalize_raw_cc_row
from .wgs_pilot import collect_full_cram_wgs_pilot


def audit_wgs_inputs_main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed audit of WGS calls against caller-native sources")
    parser.add_argument("--harmonized", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--manual-review")
    args = parser.parse_args()
    summary = audit_wgs(args.harmonized, args.output_dir, args.manual_review)
    print(f"WGS audit passed={summary['passed']} records={summary['locus_caller_records']}")
    return 0 if summary["passed"] else 2


def validate_benchmark_resource_protocol_main() -> int:
    parser = argparse.ArgumentParser(description="Validate the locked WES/RNA extension protocol")
    parser.add_argument("--protocol", required=True)
    parser.add_argument("--roster", required=True)
    parser.add_argument("--exposure-ledger", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = validate_benchmark_resource_protocol(
        args.protocol, args.roster, args.exposure_ledger, args.output)
    print(f"protocol valid={result['valid']} selected={result['selected_subjects_by_modality']}")
    return 0 if result["valid"] else 2


def evaluate_representability_main() -> int:
    parser = argparse.ArgumentParser(description="Audit truth-allele representability by caller database")
    parser.add_argument("--truth", required=True)
    parser.add_argument("--caller-resources", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    evaluate_representability(args.truth, args.caller_resources, args.output, args.summary)
    return 0


def audit_extension_readiness_main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed extension caller/resource readiness gate")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--protocol-audit", required=True)
    parser.add_argument("--caller-resources", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--preregistration",
                        help="signed confirmatory pre-registration; required to permit the truth join")
    args = parser.parse_args()
    result = audit_extension_readiness(
        args.project_root, args.protocol_audit, args.caller_resources, args.output,
        preregistration_path=args.preregistration)
    print(f"extension ready={result['ready']} caller_failures={len(result['caller_failures'])} "
          f"truth_join_permitted={result['truth_join_permitted']}")
    return 0 if result["ready"] else 2


def prepare_development_inputs_main() -> int:
    parser = argparse.ArgumentParser(description="Create truth-free corrected development inputs")
    parser.add_argument("--caller-source", required=True)
    parser.add_argument("--method-source", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--singleton-policy", choices=SINGLETON_POLICIES, default="abstain",
                        help="see decisions/20261008_singleton_native_homozygosity.json")
    parser.add_argument("--assay-manifest",
                        help="official assay manifest; inputs absent from it fail unless excluded")
    parser.add_argument("--identity-exclusions",
                        help="configs/identity_exclusions.json "
                             "(decisions/20261008_identity_check_na07000.json)")
    args = parser.parse_args()
    result = prepare_development_inputs(args.caller_source, args.method_source, args.output_dir,
                                        singleton_policy=args.singleton_policy,
                                        assay_manifest=args.assay_manifest,
                                        identity_exclusions=args.identity_exclusions)
    print(f"development inputs callers={result['rows']['caller']} "
          f"secondary={result['rows']['secondary']} partial={result['partial_rows']}")
    return 0


def fetch_public_truth_main() -> int:
    parser = argparse.ArgumentParser(description="Fetch checksum-pinned public 1000G HLA truth")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = fetch_public_truth(args.output)
    print(f"public truth verified sha256={result['sha256']}")
    return 0


def prepare_development_truth_main() -> int:
    parser = argparse.ArgumentParser(description="Select fixed development loci from public HLA truth")
    parser.add_argument("--public-truth", required=True)
    parser.add_argument("--calls", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    result = prepare_development_truth(args.public_truth, args.calls, args.output, args.manifest)
    print(f"development truth loci={result['loci']}")
    return 0


def build_development_predictions_main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate corrected development predictions")
    parser.add_argument("--calls", required=True)
    parser.add_argument("--secondary", required=True)
    parser.add_argument("--truth", required=True)
    parser.add_argument("--raw-cc-policy", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    result = build_development_predictions(
        args.calls, args.secondary, args.truth, args.raw_cc_policy, args.output, args.manifest)
    print(f"development predictions loci={result['loci']} methods={len(result['method_rows'])}")
    return 0


def characterise_development_main() -> int:
    parser = argparse.ArgumentParser(description="Generate development-cohort robustness summaries")
    parser.add_argument("--joined", required=True)
    parser.add_argument("--truth-manifest", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    result = characterise_development(args.joined, args.truth_manifest, args.output_dir)
    print(f"development characterisation shared_subjects={result['wes_rnaseq_shared_subjects']}")
    return 0


def run_truth_blind_predictions_main() -> int:
    parser = argparse.ArgumentParser(description="Run frozen two-thirds baseline and guarded CC without truth")
    parser.add_argument("--calls", required=True)
    raw_group = parser.add_mutually_exclusive_group(required=True)
    raw_group.add_argument("--raw-cc")
    raw_group.add_argument("--raw-cc-policy")
    parser.add_argument("--secondary")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--cohort-default", default="")
    parser.add_argument("--candidate-support-format", action="store_true")
    parser.add_argument("--ipd-release", default="")
    parser.add_argument("--ipd-allele-list")
    parser.add_argument("--ipd-deleted-alleles")
    parser.add_argument("--ipd-p-groups")
    parser.add_argument("--ipd-g-groups")
    args = parser.parse_args()
    source_calls = read_tsv(args.calls)
    source_cc = read_tsv(args.raw_cc) if args.raw_cc else []
    reject_truth_columns(source_calls, "runtime caller calls")
    reject_truth_columns(source_cc, "runtime raw CC calls")
    reference = None
    if args.ipd_allele_list:
        if not args.ipd_release:
            raise ValueError("--ipd-release is required with --ipd-allele-list")
        reference = HLAReference.from_files(
            args.ipd_release, args.ipd_allele_list,
            deleted_alleles=args.ipd_deleted_alleles,
            p_groups=args.ipd_p_groups, g_groups=args.ipd_g_groups,
        )
    calls = (explode_candidate_rows(source_calls, args.cohort_default, reference)
             if args.candidate_support_format
             else [normalize_caller_row(row, args.cohort_default, reference)
                   for row in source_calls])
    if args.raw_cc_policy:
        raw_cc = predict_raw_cc(calls, args.raw_cc_policy)
    else:
        raw_cc = [normalize_raw_cc_row(row, args.cohort_default) for row in source_cc
                  if row.get("method", METHOD_RAW_CC) == METHOD_RAW_CC]
    predictions = build_guarded_cc(calls, raw_cc)
    predictions.extend(raw_cc)
    for row in calls:
        predictions.append({
            "cohort": row["cohort"], "subject": row["subject"],
            "superpopulation": row.get("superpopulation", ""), "modality": row["modality"],
            "gene": row["gene"], "method": f"Caller:{row['caller']}",
            "allele1": row["allele1"], "allele2": row["allele2"],
            "call_status": row["call_status"], "decision_reason": "individual_intended_use_caller",
        })
    if args.secondary:
        secondary_source = read_tsv(args.secondary)
        reject_truth_columns(secondary_source, "runtime secondary method calls")
        predictions.extend(normalize_method_row(row, args.cohort_default) for row in secondary_source
                           if row.get("method") and row.get("method") != METHOD_RAW_CC)
    predictions.sort(key=lambda row: (row.get("cohort", ""), row["subject"], row["modality"],
                                      row["gene"], row["method"]))
    leading = ["cohort", "subject", "superpopulation", "modality", "gene", "method",
               "allele1", "allele2", "call_status", "decision_reason"]
    all_fields = {field for row in predictions for field in row}
    write_tsv(args.predictions, predictions, leading + sorted(all_fields - set(leading)))
    guarded_rows = [row for row in predictions if row["method"] == METHOD_GUARDED_CC]
    reasons = Counter(row.get("decision_reason", "") for row in predictions
                      if row["method"] == METHOD_GUARDED_CC)
    write_json(args.manifest, {
        "schema_version": "truth-blind-predictions-1", "truth_blind": True,
        "always_emit_guarded_cc": all(row["call_status"] == "callable" for row in guarded_rows),
        "guarded_no_evidence_loci": sum(row["call_status"] != "callable" for row in guarded_rows),
        "homozygosity_guard_primary": False,
        "prediction_rows": len(predictions),
        "guarded_decision_counts": dict(sorted(reasons.items())),
        "input_sha256": {"calls": sha256(args.calls),
                         "raw_cc_or_policy": sha256(args.raw_cc or args.raw_cc_policy)},
        "normalization": {
            "mode": "release_backed" if reference else "legacy_syntax_only",
            "ipd_imgt_hla_release": reference.release if reference else "",
            "source_sha256": reference.source_sha256 if reference else {},
        },
        "predictions_sha256": sha256(args.predictions),
    })
    return 0


def freeze_confirmation_bundle_main() -> int:
    parser = argparse.ArgumentParser(description="Freeze code, policies, predictions, and truth-blind gates")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--input", action="append", default=[], metavar="NAME=PATH")
    args = parser.parse_args()
    inputs = {}
    for item in args.input:
        if "=" not in item:
            raise ValueError(f"--input must be NAME=PATH: {item}")
        name, path = item.split("=", 1)
        if not name or name in inputs:
            raise ValueError(f"invalid or duplicate freeze input name: {name!r}")
        inputs[name] = path
    required = {"predictions", "protocol", "capacity", "wgs_audit"}
    if not required.issubset(inputs):
        raise ValueError(f"external freeze missing required inputs: {sorted(required - set(inputs))}")
    guarded = [row for row in read_tsv(inputs["predictions"])
               if row.get("method") == METHOD_GUARDED_CC]
    if not guarded or any(row.get("call_status") != "callable" for row in guarded):
        raise ValueError("external freeze requires a callable Guarded CC top call at every locus")
    if not read_json(inputs["capacity"]).get("passed"):
        raise ValueError("external freeze requires a passed truth-blind capacity gate")
    if not read_json(inputs["wgs_audit"]).get("passed"):
        raise ValueError("external freeze requires a passed WGS audit")
    freeze_bundle(args.project_root, inputs, args.output)
    return 0


def validate_prediction_freeze_main() -> int:
    parser = argparse.ArgumentParser(description="Validate an immutable confirmation freeze")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = validate_freeze(args.manifest)
    write_json(args.output, result)
    print(f"freeze valid={result['valid']} failures={len(result['failures'])}")
    return 0 if result["valid"] else 2


def join_external_truth_main() -> int:
    parser = argparse.ArgumentParser(description="Join independently frozen truth to immutable predictions once")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--truth", required=True)
    parser.add_argument("--freeze-manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--join-manifest", required=True)
    args = parser.parse_args()
    if Path(args.join_manifest).exists() or Path(args.output).exists():
        raise ValueError("truth join output already exists; join-once policy forbids overwrite")
    join_truth(args.predictions, args.truth, args.freeze_manifest, args.output, args.join_manifest)
    return 0


def evaluate_confirmation_main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate the locked three-modality confirmation")
    parser.add_argument("--joined", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--bootstrap", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--allow-partial", action="store_true")
    parser.add_argument("--mode", choices=("discovery", "external"), default="discovery")
    parser.add_argument("--wgs-audit-summary")
    args = parser.parse_args()
    result = evaluate(args.joined, args.output_dir, args.bootstrap, args.seed, args.allow_partial,
                      args.mode, args.wgs_audit_summary)
    print(f"confirmation status={result['status']} headline_retained={result['headline_retained']}")
    return 0


def evaluate_ambiguity_compatibility_main() -> int:
    parser = argparse.ArgumentParser(description="Score frozen calls against set-valued HLA truth")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--candidate-truth", required=True)
    parser.add_argument("--freeze-manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--bootstrap", type=int, default=100000)
    parser.add_argument("--seed", type=int, default=20260925)
    args = parser.parse_args()
    evaluate_ambiguity_compatibility(
        args.predictions, args.candidate_truth, args.freeze_manifest,
        args.output, args.bootstrap, args.seed)
    return 0


def check_confirmation_capacity_main() -> int:
    parser = argparse.ArgumentParser(description="Truth-blind mathematical capacity gate")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = capacity(args.predictions, args.output)
    print(f"capacity passed={result['passed']} discordant_subjects={result['discordant_subjects']}")
    return 0 if result["passed"] else 2


def build_overlap_crosswalk_main() -> int:
    parser = argparse.ArgumentParser(description="Exclude external aliases and relatives overlapping development")
    parser.add_argument("--development", required=True)
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    build_overlap_crosswalk(args.development, args.candidates, args.output, args.summary)
    return 0


def simulate_confirmation_power_main() -> int:
    parser = argparse.ArgumentParser(description="Discovery-based subject-cluster power projection")
    parser.add_argument("--paired", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--wgs", type=int, default=120)
    parser.add_argument("--wes", type=int, default=89)
    parser.add_argument("--rnaseq", type=int, default=150)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260831)
    parser.add_argument("--wgs-audit-summary")
    args = parser.parse_args()
    simulate(args.paired, args.output, {"wgs": args.wgs, "wes": args.wes, "rnaseq": args.rnaseq},
             args.iterations, args.seed, args.wgs_audit_summary)
    return 0


def build_hprc_release2_candidates_main() -> int:
    parser = argparse.ArgumentParser(description="Build a truth-free, non-overlapping HPRC R2 roster")
    parser.add_argument("--assemblies", required=True)
    parser.add_argument("--illumina", required=True)
    parser.add_argument("--sample-metadata", required=True)
    parser.add_argument("--development", required=True)
    parser.add_argument("--historical-exclusions", required=True)
    parser.add_argument("--source-commit", default="")
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    result = build_hprc_release2_candidates(
        args.assemblies, args.illumina, args.sample_metadata, args.development,
        args.historical_exclusions, args.output, args.summary, args.source_commit,
    )
    print(f"HPRC eligible non-overlap={result['eligible_nonoverlap']} "
          f"target120={result['target_120_available']}")
    return 0 if result["target_120_available"] else 2


def select_hprc_confirmation_roster_main() -> int:
    parser = argparse.ArgumentParser(description="Freeze a truth-free stratified HPRC WGS roster")
    parser.add_argument("--candidates", required=True)
    parser.add_argument("--target", type=int, default=120)
    parser.add_argument("--seed", default="ChampHLA-CC-confirmation-20260831")
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    result = select_hprc_confirmation_roster(
        args.candidates, args.target, args.seed, args.output, args.summary,
    )
    print(f"HPRC selected={result['selected']} target={result['target']}")
    return 0


def build_frozen_raw_cc_policy_main() -> int:
    parser = argparse.ArgumentParser(description="Freeze raw CC weights from development labels only")
    parser.add_argument("--development-harmonized", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = read_tsv(args.development_harmonized)
    result = freeze_raw_cc_policy(rows, args.development_harmonized, args.output)
    print(f"raw CC policy weights={len(result['diagnostics'])} output={args.output}")
    return 0


def sanitize_ihwg_registry_main() -> int:
    parser = argparse.ArgumentParser(description="Remove genotype fields from an IHWG name registry")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args()
    result = sanitize_ihwg_registry(args.source, args.output, args.manifest)
    print(f"sanitized IHWG subjects={result['subjects']} truth_blind={result['truth_blind']}")
    return 0


def scout_ihwg_public_reads_main() -> int:
    parser = argparse.ArgumentParser(description="Truth-free ENA discovery for public IHWG WES/RNA reads")
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--sleep-seconds", type=float, default=0.1)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    result = scout_ihwg_public_reads(
        args.registry, args.output, args.summary, args.cache_dir,
        args.sleep_seconds, args.limit, args.offline,
    )
    print(f"ENA candidate subjects={result['candidate_subjects_by_modality']} "
          f"failures={len(result['query_failures'])}")
    return 0 if not result["query_failures"] else 2


def build_ihwg_provenance_review_packet_main() -> int:
    parser = argparse.ArgumentParser(description="Build a fail-closed IHWG run provenance review sheet")
    parser.add_argument("--matches", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    result = build_ihwg_provenance_review_packet(args.matches, args.output, args.summary)
    print(f"IHWG runs requiring provenance review={result['candidate_runs']}")
    return 0


def finalize_ihwg_read_roster_main() -> int:
    parser = argparse.ArgumentParser(description="Freeze provenance-verified IHWG WES/RNA run rosters")
    parser.add_argument("--review", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--min-wes", type=int, default=89)
    parser.add_argument("--min-rnaseq", type=int, default=130)
    args = parser.parse_args()
    result = finalize_ihwg_read_roster(
        args.review, args.output, args.summary, args.min_wes, args.min_rnaseq,
    )
    print(f"IHWG selected={result['selected_subjects_by_modality']} "
          f"minimum_met={result['minimum_met']}")
    return 0 if all(result["minimum_met"].values()) else 2


def collect_full_cram_wgs_pilot_main() -> int:
    parser = argparse.ArgumentParser(description="Collect strict truth-free full-CRAM WGS pilot calls")
    parser.add_argument("--caller-root", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--sample", action="append", default=[])
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()
    result = collect_full_cram_wgs_pilot(
        args.caller_root, args.manifest, args.sample, args.output, args.summary,
    )
    print(f"WGS pilot samples={result['samples']} records={result['observed_locus_caller_records']}")
    return 0
