"""Confirmatory extension driver (configs/benchmark_resource_protocol_v2.json, as amended by
decisions/20261009_extension_voting_panels_only.json).

The extension runs the development gate's own chain on the frozen, subject-disjoint
roster, so the confirmatory result comes from the code that produced the development
result:

  prepare  frozen runs accept only checksum-validated collector directories containing
           normalized calls, T1K parser provenance and per-run provenance. Every roster
           subject-assay must have exactly one row per panel caller and gene. The older
           aggregated_calls.tsv adapter is retained only for non-frozen historical dry
           runs; it is not an admissible confirmatory input boundary.
  predict  truth-free predictions, a sample-identity check, and a freeze of predictions
           plus code.
  unblind  only if the readiness audit permits the truth join (signed pre-registration
           recording the release DOI): the truth is joined once and evaluated with the
           protocol's inference settings.

    python scripts/run_extension.py prepare --collection-dir <collector-output> [...]
    python scripts/run_extension.py predict
    python scripts/run_extension.py unblind --preregistration decisions/<record>.json

--roster and --work-dir exist only so the dry run can replay the chain on the
development subjects (reports/extension_dry_run_*). A dry run never writes into
data/extension, runtime_data/extension or artifacts/extension, and it can only bypass
the readiness gate when it does not use the frozen roster.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.development import (  # noqa: E402
    build_development_predictions,
    identity_check,
    prepare_development_candidate_truth,
    prepare_development_truth,
)
from champhla_confirmation.evaluation import (  # noqa: E402
    evaluate,
    evaluate_ambiguity_compatibility,
    join_truth,
)
from champhla_confirmation.freeze import freeze_bundle, validate_freeze  # noqa: E402
from champhla_confirmation.hla_reference import HLAReference  # noqa: E402
from champhla_confirmation.io import (  # noqa: E402
    normalize_modality,
    read_json,
    read_tsv,
    sha256,
    write_json,
    write_tsv,
)
from champhla_confirmation.panels import GENES, PANELS  # noqa: E402
from champhla_confirmation.readiness import audit_extension_readiness  # noqa: E402
from champhla_confirmation.schema import normalize_caller_row  # noqa: E402

PROTOCOL = ROOT / "configs" / "benchmark_resource_protocol_v2.json"
FROZEN_ROSTER = ROOT / "cohorts" / "frozen_initial_rosters.tsv"
IPD = ROOT / "resources" / "ipd_imgt_hla" / "3.65.0"
RAW_CC_POLICY = ROOT / "data" / "development" / "frozen_raw_cc_policy.json"
PUBLIC_TRUTH = ROOT / "runtime_data" / "public_truth" / "20140702_hla_diversity.txt"
COHORT = "1000G-2014-unseen"
SINGLETON_POLICY = "native_declaration"
TOOL_TO_CALLER = {"hlahd": "HLA-HD", "optitype": "OptiType", "polysolver": "POLYSOLVER",
                  "spechla": "SpecHLA", "t1k": "T1K", "arcashla": "ArcasHLA"}
CALLER_FIELDS = ["cohort", "subject", "superpopulation", "modality", "gene", "caller",
                 "allele1_raw", "allele2_raw", "allele1", "allele2", "call_status",
                 "no_call_reason", "homozygosity_basis", "allele1_suffix", "allele2_suffix",
                 "normalization_database_version", "source_path", "source_sha256"]
PINNED_RELEASE_COMMIT = "66d949da90861da6cf60cf1d4bee2f094f2518bd"
COLLECTION_SCHEMA = "champhla-development-rerun-collection-2"
COLLECTION_OUTPUTS = (
    "normalized_caller_calls.tsv",
    "t1k_parser_provenance.tsv",
    "sample_run_provenance.tsv",
    "selected_input_manifest.tsv",
)


def _paths(work: Path | None) -> dict[str, Path]:
    if work is None:
        data, runtime, out = (ROOT / "data" / "extension", ROOT / "runtime_data" / "extension",
                              ROOT / "artifacts" / "extension")
    else:
        data, runtime, out = work / "data", work / "runtime", work / "artifacts"
    return {"data": data, "runtime": runtime, "out": out,
            "calls": data / "normalized_caller_calls.tsv",
            "prepare_manifest": data / "prepare_manifest.json",
            "secondary": data / "no_secondary_methods.tsv",
            "predictions": runtime / "predictions.tsv",
            "prediction_manifest": runtime / "predictions_manifest.json",
            "freeze": runtime / "prediction_freeze.json",
            "truth": runtime / "truth.tsv", "truth_manifest": runtime / "truth_manifest.json",
            "candidate_truth": runtime / "candidate_truth.tsv",
            "candidate_manifest": runtime / "candidate_truth_manifest.json",
            "joined": runtime / "joined.tsv", "join_manifest": runtime / "join_manifest.json"}


def _protocol_inference() -> dict:
    return read_json(PROTOCOL)["inference"]


def _roster(path: Path) -> dict[tuple[str, str], str]:
    roster: dict[tuple[str, str], str] = {}
    for row in read_tsv(path):
        modality = normalize_modality(row["modality"])
        if modality not in {"wes", "rnaseq"}:
            continue
        subject = row.get("subject", "").strip()
        if not subject:
            raise ValueError(f"blank subject in roster: {path}")
        key = (subject, modality)
        if key in roster:
            raise ValueError(f"duplicate subject-assay in roster: {key}")
        roster[key] = row.get("population", "")
    if not roster:
        raise ValueError(f"roster has no WES or RNA-seq rows: {path}")
    return roster


def prepare_collected(collection_dirs: list[Path], roster_path: Path,
                      paths: dict[str, Path]) -> dict:
    """Prepare frozen predictions from checksum-bound, truth-free collector outputs."""
    roster = _roster(roster_path)
    expected = {
        (subject, modality, gene, caller)
        for subject, modality in roster
        for gene in GENES
        for caller in PANELS[modality]
    }
    calls_by_key: dict[tuple[str, str, str, str], dict[str, str]] = {}
    run_keys: set[tuple[str, str]] = set()
    t1k_keys: set[tuple[str, str, str]] = set()
    inputs: list[dict[str, object]] = []

    for directory in collection_dirs:
        manifest_path = directory / "collection_manifest.json"
        if not manifest_path.is_file():
            raise ValueError(f"missing collection manifest: {manifest_path}")
        manifest = read_json(manifest_path)
        if manifest.get("schema_version") != COLLECTION_SCHEMA:
            raise ValueError(f"unsupported collection schema: {manifest_path}")
        if manifest.get("truth_free") is not True:
            raise ValueError(f"collection is not marked truth-free: {manifest_path}")
        if manifest.get("release_commit") != PINNED_RELEASE_COMMIT:
            raise ValueError(f"collection release commit mismatch: {manifest_path}")
        recorded = manifest.get("output_sha256")
        if not isinstance(recorded, dict):
            raise ValueError(f"collection has no output hashes: {manifest_path}")
        output_hashes: dict[str, str] = {}
        for name in COLLECTION_OUTPUTS:
            source = directory / name
            if not source.is_file():
                raise ValueError(f"missing collected output: {source}")
            observed = sha256(source)
            if recorded.get(name) != observed:
                raise ValueError(f"collection output hash mismatch: {source}")
            output_hashes[name] = observed

        collected_calls = read_tsv(directory / COLLECTION_OUTPUTS[0])
        t1k_rows = read_tsv(directory / COLLECTION_OUTPUTS[1])
        run_rows = read_tsv(directory / COLLECTION_OUTPUTS[2])
        selected_rows = read_tsv(directory / COLLECTION_OUTPUTS[3])
        if manifest.get("selected_input_manifest_sha256") != output_hashes[COLLECTION_OUTPUTS[3]]:
            raise ValueError(f"selected input manifest hash mismatch: {manifest_path}")
        if manifest.get("caller_rows") != len(collected_calls):
            raise ValueError(f"collection caller-row count mismatch: {manifest_path}")
        if manifest.get("t1k_audit_rows") != len(t1k_rows):
            raise ValueError(f"collection T1K-row count mismatch: {manifest_path}")
        local_runs: set[tuple[str, str]] = set()
        for row in run_rows:
            key = (row.get("subject", "").strip(), normalize_modality(row["modality"]))
            if key not in roster:
                raise ValueError(f"collected run {key} is not in the extension roster")
            if key in run_keys or key in local_runs:
                raise ValueError(f"duplicate collected run provenance for {key}")
            if row.get("release_commit") != PINNED_RELEASE_COMMIT:
                raise ValueError(f"run release commit mismatch for {key}")
            if row.get("sample_complete") != "1":
                raise ValueError(f"collected run is not complete for {key}")
            local_runs.add(key)
        if manifest.get("sample_assays") != len(local_runs):
            raise ValueError(f"collection sample-assay count mismatch: {manifest_path}")
        selected_keys = {
            (row.get("sample_id", "").strip(), normalize_modality(row["modality"]))
            for row in selected_rows
        }
        if selected_keys != local_runs or len(selected_rows) != len(selected_keys):
            raise ValueError(f"selected input manifest does not match run provenance: {manifest_path}")
        run_keys.update(local_runs)

        for row in t1k_rows:
            key = (
                row.get("subject", "").strip(),
                normalize_modality(row["modality"]),
                row.get("gene", "").replace("HLA-", "").upper(),
            )
            if key[:2] not in local_runs or key[2] not in GENES:
                raise ValueError(f"invalid or cross-bundle T1K provenance key {key}")
            if key in t1k_keys:
                raise ValueError(f"duplicate T1K provenance key {key}")
            if not row.get("parser_audit_sha256") or not row.get("raw_genotype_sha256"):
                raise ValueError(f"unhashed T1K provenance at {key}")
            t1k_keys.add(key)

        local_call_keys: set[tuple[str, str, str, str]] = set()
        for row in collected_calls:
            subject = row.get("subject", "").strip()
            modality = normalize_modality(row["modality"])
            gene = row.get("gene", "").replace("HLA-", "").upper()
            caller = row.get("caller", "").strip()
            key = (subject, modality, gene, caller)
            if (subject, modality) not in local_runs:
                raise ValueError(f"collected call {key} lacks matching run provenance in its bundle")
            if gene not in GENES or caller not in PANELS[modality]:
                raise ValueError(f"collected call is outside the frozen panel: {key}")
            if key in calls_by_key:
                raise ValueError(f"duplicate collected caller output for {key}")
            if not row.get("call_status"):
                raise ValueError(f"collected call has no call state: {key}")
            copied = {field: row.get(field, "") for field in CALLER_FIELDS}
            copied["cohort"] = COHORT
            copied["subject"] = subject
            copied["superpopulation"] = roster[(subject, modality)]
            copied["modality"] = modality
            copied["gene"] = gene
            copied["caller"] = caller
            calls_by_key[key] = copied
            local_call_keys.add(key)

        local_expected = {
            (subject, modality, gene, caller)
            for subject, modality in local_runs
            for gene in GENES
            for caller in PANELS[modality]
        }
        if local_call_keys != local_expected:
            raise ValueError(
                f"collection bundle caller grid mismatch: "
                f"missing={sorted(local_expected-local_call_keys)[:10]} "
                f"extra={sorted(local_call_keys-local_expected)[:10]}"
            )

        inputs.append({
            "directory": directory.as_posix(),
            "manifest_sha256": sha256(manifest_path),
            "output_sha256": output_hashes,
        })

    missing = sorted(expected - set(calls_by_key))
    extra = sorted(set(calls_by_key) - expected)
    if missing or extra:
        raise ValueError(
            f"collected caller grid mismatch: missing={missing[:10]} extra={extra[:10]}"
        )
    expected_runs = set(roster)
    if run_keys != expected_runs:
        raise ValueError(
            f"collected run grid mismatch: missing={sorted(expected_runs-run_keys)[:10]} "
            f"extra={sorted(run_keys-expected_runs)[:10]}"
        )

    calls = [calls_by_key[key] for key in sorted(calls_by_key)]
    paths["data"].mkdir(parents=True, exist_ok=True)
    write_tsv(paths["calls"], calls, CALLER_FIELDS)
    write_tsv(paths["secondary"], [], ["cohort", "subject", "modality", "gene", "method"])
    manifest = {
        "schema_version": "champhla-extension-prepare-2",
        "cohort": COHORT,
        "input_boundary": "checksummed_truth_free_collector_outputs",
        "release_commit": PINNED_RELEASE_COMMIT,
        "normalization_release": "3.65.0",
        "roster_sha256": sha256(roster_path),
        "roster_subject_assays": len(roster),
        "collection_inputs": inputs,
        "caller_rows": len(calls),
        "explicit_noncall_rows": sum(row["call_status"] != "callable" for row in calls),
        "t1k_audit_rows": len(t1k_keys),
        "calls_sha256": sha256(paths["calls"]),
    }
    write_json(paths["prepare_manifest"], manifest)
    return manifest


def prepare(aggregated: list[Path], roster_path: Path, paths: dict[str, Path]) -> dict:
    roster = _roster(roster_path)
    reference = HLAReference.from_files("3.65.0", IPD / "Allelelist.txt",
                                        deleted_alleles=IPD / "Deleted_alleles.txt",
                                        p_groups=IPD / "wmda" / "hla_nom_p.txt",
                                        g_groups=IPD / "wmda" / "hla_nom_g.txt")
    raw: dict[tuple[str, str, str, str], dict] = {}
    ignored_tools: dict[str, int] = {}
    for source in aggregated:
        digest = sha256(source)
        for row in read_tsv(source):
            modality = normalize_modality(row["modality"])
            key = (row["sample"].strip(), modality)
            if key not in roster:
                raise ValueError(f"input {key} is not in the extension roster")
            caller = TOOL_TO_CALLER.get(row["tool"].strip().lower())
            if caller not in PANELS[modality]:
                ignored_tools[row["tool"]] = ignored_tools.get(row["tool"], 0) + 1
                continue
            locus = (*key, row["gene"].strip().replace("HLA-", "").upper(), caller)
            if locus in raw:
                raise ValueError(f"duplicate caller output for {locus}")
            raw[locus] = {"allele1_raw": row.get("allele1", ""), "allele2_raw": row.get("allele2", ""),
                          "source_path": source.as_posix(), "source_sha256": digest}
    calls, absent = [], []
    for (subject, modality), population in sorted(roster.items()):
        for gene in GENES:
            for caller in PANELS[modality]:
                found = raw.get((subject, modality, gene, caller))
                if not found:
                    absent.append(f"{subject}:{modality}:{gene}:{caller}")
                row = normalize_caller_row({
                    "cohort": COHORT, "subject": subject, "population": population,
                    "modality": modality, "gene": gene, "caller": caller,
                    "allele1_raw": (found or {}).get("allele1_raw", ""),
                    "allele2_raw": (found or {}).get("allele2_raw", ""),
                    "source_path": (found or {}).get("source_path", ""),
                    "source_sha256": (found or {}).get("source_sha256", ""),
                }, COHORT, reference=reference, singleton_policy=SINGLETON_POLICY)
                if not found:
                    row["no_call_reason"] = "no_caller_output"
                calls.append(row)
    paths["data"].mkdir(parents=True, exist_ok=True)
    write_tsv(paths["calls"], calls, CALLER_FIELDS)
    write_tsv(paths["secondary"], [], ["cohort", "subject", "modality", "gene", "method"])
    manifest = {
        "schema_version": "champhla-extension-prepare-1", "cohort": COHORT,
        "singleton_policy": SINGLETON_POLICY, "normalization_release": "3.65.0",
        "roster_sha256": sha256(roster_path), "roster_subject_assays": len(roster),
        "aggregated_inputs": {p.as_posix(): sha256(p) for p in aggregated},
        "caller_rows": len(calls), "absent_caller_loci": len(absent),
        "absent_examples": absent[:20], "ignored_non_panel_tools": ignored_tools,
        "calls_sha256": sha256(paths["calls"]),
    }
    write_json(paths["prepare_manifest"], manifest)
    return manifest


def predict(paths: dict[str, Path]) -> dict:
    paths["runtime"].mkdir(parents=True, exist_ok=True)
    manifest = build_development_predictions(
        str(paths["calls"]), str(paths["secondary"]), None, str(RAW_CC_POLICY),
        str(paths["predictions"]), str(paths["prediction_manifest"]))
    identity_check([str(paths["calls"])], str(ROOT / "cohorts" / "official_1000g_assay_manifest.tsv"),
                   str(paths["runtime"] / "identity_check.tsv"))
    freeze_bundle(ROOT, {"predictions": paths["predictions"], "calls": paths["calls"],
                         "prepare_manifest": paths["prepare_manifest"]}, paths["freeze"])
    return manifest


def unblind(paths: dict[str, Path], preregistration: str | None, dry_run: bool) -> dict:
    if not dry_run:
        readiness = audit_extension_readiness(
            str(ROOT), str(ROOT / "artifacts" / "benchmark_resource_protocol_audit.json"),
            str(ROOT / "configs" / "caller_resources_v2.json"),
            str(paths["runtime"] / "readiness_at_unblinding.json"),
            preregistration_path=preregistration)
        if not readiness["truth_join_permitted"]:
            raise SystemExit(f"truth join not permitted: {readiness['failures'] + readiness['truth_join_blockers']}")
    validation = validate_freeze(str(paths["freeze"]))
    if not validation["valid"]:
        raise SystemExit(f"prediction freeze invalid: {validation['failures']}")
    if paths["joined"].exists() and not dry_run:
        raise SystemExit("the extension truth has already been joined once; refusing to join again")
    inference = _protocol_inference()
    prepare_development_truth(str(PUBLIC_TRUTH), str(paths["calls"]), str(paths["truth"]),
                              str(paths["truth_manifest"]), cohort=COHORT)
    prepare_development_candidate_truth(str(PUBLIC_TRUTH), str(paths["calls"]),
                                        str(paths["candidate_truth"]),
                                        str(paths["candidate_manifest"]))
    join_truth(str(paths["predictions"]), str(paths["truth"]), str(paths["freeze"]),
               str(paths["joined"]), str(paths["join_manifest"]), allow_prediction_superset=True)
    result = evaluate(str(paths["joined"]), str(paths["out"]), inference["bootstrap_iterations"],
                      inference["bootstrap_seed"], True, "discovery",
                      signflip_seed=inference["signflip_seed"])
    evaluate_ambiguity_compatibility(
        str(paths["predictions"]), str(paths["candidate_truth"]), str(paths["freeze"]),
        str(paths["out"] / "ambiguity_compatibility.tsv"), inference["bootstrap_iterations"],
        inference["bootstrap_seed"])
    write_json(paths["out"] / "unblinding_manifest.json", {
        "schema_version": "champhla-extension-unblinding-1", "dry_run": dry_run,
        "preregistration": preregistration or "", "freeze_sha256": sha256(paths["freeze"]),
        "join_manifest_sha256": sha256(paths["join_manifest"]),
        "inference": inference,
    })
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stage", choices=("prepare", "predict", "unblind"))
    parser.add_argument("--aggregated", action="append", default=[], type=Path,
                        help="historical dry-run adapter only; forbidden for the frozen roster")
    parser.add_argument("--collection-dir", action="append", default=[], type=Path,
                        help="checksummed output directory from collect_development_rerun.py")
    parser.add_argument("--preregistration")
    parser.add_argument("--roster", type=Path, default=FROZEN_ROSTER)
    parser.add_argument("--work-dir", type=Path)
    args = parser.parse_args(argv)
    dry_run = args.roster.resolve() != FROZEN_ROSTER.resolve()
    if dry_run and args.work_dir is None:
        raise SystemExit("a dry run (non-frozen roster) requires --work-dir")
    if not dry_run and args.work_dir is not None:
        raise SystemExit("the frozen-roster run writes only to the extension locations")
    paths = _paths(args.work_dir)
    if args.stage == "prepare":
        if args.collection_dir and args.aggregated:
            raise SystemExit("prepare accepts either collector directories or historical aggregates, not both")
        if not dry_run:
            if not args.collection_dir:
                raise SystemExit(
                    "frozen-roster prepare requires at least one --collection-dir; "
                    "aggregate-only input is forbidden"
                )
            print(prepare_collected(args.collection_dir, args.roster, paths))
        elif args.collection_dir:
            print(prepare_collected(args.collection_dir, args.roster, paths))
        elif args.aggregated:
            print(prepare(args.aggregated, args.roster, paths))
        else:
            raise SystemExit("prepare needs --collection-dir or, for a dry run, --aggregated")
    elif args.stage == "predict":
        print(predict(paths))
    else:
        unblind(paths, args.preregistration, dry_run)
        print(f"evaluated -> {paths['out']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
