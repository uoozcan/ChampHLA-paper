from __future__ import annotations

import tempfile
import urllib.request
from collections import Counter
from pathlib import Path

from .consensus import build_consensus, build_guarded_cc
from .families import DEFAULT_MIN_SUPPORTING_FAMILIES, supporting_families
from .io import (canonical_pair, read_json, read_tsv, reject_truth_columns, sha256, write_json,
                 write_tsv)
from .panels import (METHOD_BASELINE, METHOD_GUARDED_CC, METHOD_PLURALITY,
                     METHOD_RAW_CC, METHOD_STRICT_MAJORITY, PANELS)
from .raw_cc import predict_raw_cc
from .schema import normalize_caller_row, normalize_method_row

DEVELOPMENT_MODALITIES = ("wes", "rnaseq")
PUBLIC_TRUTH_URL = (
    "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/technical/working/"
    "20140725_hla_genotypes/20140702_hla_diversity.txt"
)
PUBLIC_TRUTH_SHA256 = "0455d0302ac12a29ab87091cab5e3e557416f6301e89fb122eef8d49cd5644ec"
SECONDARY_METHODS = frozenset({
    "BestSingleTool_nestedCV",
    "ChampionChallenger",
    "MVFlooredCC",
    "MetaConsensus",
})

# Content-derived values are lower bounds (the earliest release containing every
# bundled allele) from provenance/external_evidence/db_release_resolution.json.
# ArcasHLA is not in that file: its value comes from a historical bundled version
# report that was not preserved. These describe caller resources, not the
# IPD-IMGT/HLA release used later for normalization.
CALLER_DATABASE_PROVENANCE = {
    "ArcasHLA": ("3.40.0", "historical bundled report; original unavailable"),
    "HLA-HD": ("3.15.0", "content-derived lower bound"),
    "OptiType": ("3.13.1", "content-derived lower bound"),
    "POLYSOLVER": ("3.11.0", "content-derived lower bound"),
    "SpecHLA": ("3.38.0 + 3.51.0", "heterogeneous bundled components"),
    "T1K": ("3.63.0", "deployment declaration and content audit"),
}
INPUT_REFERENCE_BUILD = {"wes": "GRCh38DH", "rnaseq": "GRCh37"}
# Column set of the released normalized caller table; homozygosity_basis records
# whether a pair came from two alleles or a caller-native homozygous declaration.
CALLER_INPUT_FIELDS = [
    "cohort", "subject", "superpopulation", "modality", "gene", "caller",
    "allele1_raw", "allele2_raw", "allele1", "allele2", "call_status",
    "no_call_reason", "homozygosity_basis", "allele1_suffix", "allele2_suffix",
    "caller_version", "database_version", "database_version_basis",
    "normalization_database_version", "input_reference_build", "container_digest",
    "source_path", "source_sha256", "caller_version_provenance", "container_provenance",
]


def fetch_public_truth(output_path: str, url: str = PUBLIC_TRUTH_URL,
                       expected_sha256: str = PUBLIC_TRUTH_SHA256) -> dict:
    """Download the authoritative public truth resource and verify its identity."""
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        with urllib.request.urlopen(url, timeout=60) as response, target.open("wb") as handle:
            while block := response.read(1024 * 1024):
                handle.write(block)
    observed = sha256(target)
    if observed != expected_sha256:
        target.unlink(missing_ok=True)
        raise ValueError(
            f"public truth checksum mismatch: expected {expected_sha256}, observed {observed}"
        )
    return {"url": url, "sha256": observed, "path": str(target), "verified": True}


def prepare_development_truth(public_truth_source: str, caller_calls_path: str,
                              output_path: str, manifest_path: str,
                              require_every_modality: bool = True,
                              cohort: str = "1000G-development") -> dict:
    """Select only the fixed development loci from the public 2014 truth table.

    ``require_every_modality=False`` is only for scoring a withheld subset (for example
    a single excluded RNA-seq input); the development endpoint always requires both.
    ``cohort`` labels the truth rows so they join the predictions of the same cohort
    (the confirmatory extension uses its own roster's label)."""
    from champhla_recovery.truth import audit_two_field_resolution, prepare_locked_truth

    calls = read_tsv(caller_calls_path)
    target_loci = {(r["subject"], r["modality"], r["gene"]) for r in calls}
    requested_subjects = {
        modality: {r["subject"] for r in calls if r["modality"] == modality}
        for modality in DEVELOPMENT_MODALITIES
    }
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        full_truth = directory / "truth.tsv"
        registry = directory / "registry.tsv"
        full_manifest = directory / "manifest.json"
        source_summary = prepare_locked_truth(
            public_truth_source, str(full_truth), str(registry), str(full_manifest)
        )
        available = {
            (r["subject"], r["modality"], r["gene"]): r for r in read_tsv(full_truth)
        }
        missing = sorted(target_loci - set(available))
        selected = []
        for locus in sorted(target_loci & set(available)):
            row = dict(available[locus])
            row["cohort"] = cohort
            selected.append(row)
        counts = {
            modality: sum(r["modality"] == modality for r in selected)
            for modality in DEVELOPMENT_MODALITIES
        }
        excluded_counts = {
            modality: sum(item[1] == modality for item in missing)
            for modality in DEVELOPMENT_MODALITIES
        }
        source_audit = audit_two_field_resolution(public_truth_source)
        exclusion_rows = []
        for subject, modality, gene in missing:
            detail = source_audit.get((subject, gene))
            exclusion_rows.append({
                "subject": subject, "modality": modality, "gene": gene,
                "reason": (detail or {}).get("reason", "subject_or_gene_absent_from_source"),
                "source_record_count": (detail or {}).get("source_record_count", 0),
            })
        exclusions_path = Path(manifest_path).with_name("development_truth_exclusions.tsv")
        write_tsv(exclusions_path, exclusion_rows,
                  ["subject", "modality", "gene", "reason", "source_record_count"])
        exclusion_reasons: dict[str, int] = {}
        for row in exclusion_rows:
            reason = str(row["reason"])
            exclusion_reasons[reason] = exclusion_reasons.get(reason, 0) + 1
        if require_every_modality and not all(counts.values()):
            raise ValueError(f"no uniquely resolvable development truth for a modality: {counts}")
        write_tsv(output_path, selected)
        manifest = {
            "schema_version": "panelhla-development-truth-1",
            "public_source_url": PUBLIC_TRUTH_URL,
            "public_source_sha256": sha256(public_truth_source),
            "expected_public_source_sha256": PUBLIC_TRUTH_SHA256,
            "caller_calls_sha256": sha256(caller_calls_path),
            "truth_output_sha256": sha256(output_path),
            "loci": counts,
            "requested_loci": {
                modality: sum(item[1] == modality for item in target_loci)
                for modality in DEVELOPMENT_MODALITIES
            },
            "requested_subjects": {key: len(value) for key, value in requested_subjects.items()},
            "requested_subject_overlap": len(requested_subjects["wes"] & requested_subjects["rnaseq"]),
            "excluded_ambiguous_or_unresolved_loci": excluded_counts,
            "truth_exclusions_path": exclusions_path.name,
            "truth_exclusions_sha256": sha256(exclusions_path),
            "truth_exclusion_reasons": dict(sorted(exclusion_reasons.items())),
            "denominator_changed_after_source_audit": bool(missing),
            "selection": "exact subject-modality-gene loci present in normalized caller inputs",
            "source_summary": source_summary,
        }
        write_json(manifest_path, manifest)
        return manifest


def prepare_development_candidate_truth(public_truth_source: str, caller_calls_path: str,
                                        output_path: str, manifest_path: str) -> dict:
    """Select set-valued source truth for every requested development locus.

    This is intentionally independent of predictions.  Source-absent and invalid
    records remain explicit denominator states rather than disappearing during a
    truth join.
    """
    from champhla_recovery.truth import prepare_ambiguity_aware_truth

    calls = read_tsv(caller_calls_path)
    target_loci = {(r["subject"], r["modality"], r["gene"]) for r in calls}
    with tempfile.TemporaryDirectory() as directory:
        directory = Path(directory)
        full_truth = directory / "candidate_truth.tsv"
        full_manifest = directory / "candidate_truth_manifest.json"
        prepare_ambiguity_aware_truth(
            public_truth_source, str(full_truth), str(full_manifest)
        )
        available = {
            (r["subject"], r["modality"], r["gene"]): r
            for r in read_tsv(full_truth)
        }
        selected = []
        for locus in sorted(target_loci):
            row = available.get(locus)
            if row is None:
                subject, modality, gene = locus
                row = {
                    "cohort": "1000G-development-candidate-truth",
                    "subject": subject,
                    "population": "",
                    "modality": modality,
                    "gene": gene,
                    "truth_status": "absent",
                    "truth_candidate_pairs_json": "[]",
                    "candidate_pair_count": 0,
                    "parse_errors": "subject_or_gene_absent_from_source",
                    "truth_source": "2014 1000 Genomes laboratory HLA typing",
                    "source_sha256": sha256(public_truth_source),
                }
            else:
                row = dict(row)
                row["cohort"] = "1000G-development-candidate-truth"
            selected.append(row)
        write_tsv(output_path, selected)
        status_counts: dict[str, dict[str, int]] = {}
        for modality in DEVELOPMENT_MODALITIES:
            counts: dict[str, int] = {}
            for row in selected:
                if row["modality"] == modality:
                    status = row["truth_status"]
                    counts[status] = counts.get(status, 0) + 1
            status_counts[modality] = dict(sorted(counts.items()))
        manifest = {
            "schema_version": "panelhla-development-candidate-truth-2",
            "truth_representation": "set_of_valid_unordered_two_field_genotypes",
            "caller_outputs_used": False,
            "requested_loci": len(target_loci),
            "status_counts": status_counts,
            "source_sha256": sha256(public_truth_source),
            "caller_calls_sha256": sha256(caller_calls_path),
            "output_sha256": sha256(output_path),
        }
        write_json(manifest_path, manifest)
        return manifest


def _identity_controls(assay_manifest: str | None, identity_exclusions: str | None):
    admitted = ({(r["sample_id"], r["modality"]) for r in read_tsv(assay_manifest)}
                if assay_manifest else None)
    excluded = {}
    if identity_exclusions:
        for item in read_json(identity_exclusions)["exclusions"]:
            excluded[(item["subject"], item["modality"])] = item
    return admitted, excluded


def _partition_by_identity(rows: list[dict], admitted, excluded, what: str):
    """Fail closed: an input must be in the official assay manifest or be a recorded
    exclusion (decisions/20261008_identity_check_na07000.json)."""
    kept, withheld = [], []
    for row in rows:
        key = (row["subject"], row["modality"])
        if key in excluded:
            withheld.append(row)
        elif admitted is not None and key not in admitted:
            raise ValueError(f"{what} {key} is not in the official assay manifest "
                             "and is not a recorded identity exclusion")
        else:
            kept.append(row)
    return kept, withheld


def prepare_development_inputs(caller_source: str, method_source: str, output_dir: str,
                               singleton_policy: str = "abstain",
                               assay_manifest: str | None = None,
                               identity_exclusions: str | None = None) -> dict:
    """Create portable truth-free inputs from the recovered development sources."""
    caller_rows = read_tsv(caller_source)
    method_rows = read_tsv(method_source)
    caller_source_sha256 = sha256(caller_source)
    method_source_sha256 = sha256(method_source)
    calls = []
    for row in caller_rows:
        modality = row.get("modality", "").strip().lower()
        caller = row.get("tool", row.get("caller", "")).strip()
        if modality not in DEVELOPMENT_MODALITIES or caller not in PANELS[modality]:
            continue
        normalized = normalize_caller_row(row, "1000G-development",
                                          singleton_policy=singleton_policy)
        database_version, basis = CALLER_DATABASE_PROVENANCE[caller]
        normalized["database_version"] = database_version
        normalized["database_version_basis"] = basis
        normalized["input_reference_build"] = INPUT_REFERENCE_BUILD[modality]
        normalized["caller_version_provenance"] = (
            "historical executable version unavailable" if not normalized["caller_version"]
            else "recorded in recovered source"
        )
        normalized["container_provenance"] = (
            "historical digest unavailable" if not normalized["container_digest"]
            else "recorded in recovered source"
        )
        normalized["source_path"] = "recovered-development-caller-output"
        normalized["source_sha256"] = caller_source_sha256
        calls.append(normalized)

    secondary = []
    for row in method_rows:
        modality = row.get("modality", "").strip().lower()
        method = row.get("method", "").strip()
        if modality not in DEVELOPMENT_MODALITIES or method not in SECONDARY_METHODS:
            continue
        normalized = normalize_method_row(row, "1000G-development")
        for field in (
            "decision_reason", "champion_tool", "champion_pair", "challenger_pair",
            "supporting_tools", "supporting_callers", "supporting_families",
            "support_fraction", "support_margin", "override_triggered", "outer_fold",
        ):
            if field in row:
                normalized[field] = row[field]
        secondary.append(normalized)

    admitted, excluded = _identity_controls(assay_manifest, identity_exclusions)
    calls, excluded_calls = _partition_by_identity(calls, admitted, excluded, "caller input")
    secondary, excluded_secondary = _partition_by_identity(
        secondary, admitted, excluded, "secondary input")
    reject_truth_columns(calls, "prepared development caller calls")
    reject_truth_columns(secondary, "prepared development secondary calls")
    call_keys = [(r["subject"], r["modality"], r["gene"], r["caller"]) for r in calls]
    method_keys = [(r["subject"], r["modality"], r["gene"], r["method"]) for r in secondary]
    if len(call_keys) != len(set(call_keys)):
        raise ValueError("duplicate development caller rows after normalization")
    if len(method_keys) != len(set(method_keys)):
        raise ValueError("duplicate development method rows after normalization")

    calls.sort(key=lambda r: (r["subject"], r["modality"], r["gene"], r["caller"]))
    secondary.sort(key=lambda r: (r["subject"], r["modality"], r["gene"], r["method"]))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    calls_path = out / "normalized_caller_calls.tsv"
    secondary_path = out / "normalized_secondary_calls.tsv"
    write_tsv(calls_path, calls, CALLER_INPUT_FIELDS)
    write_tsv(secondary_path, secondary)
    identity = {"assay_manifest_enforced": admitted is not None,
                "excluded_subject_assays": sorted(f"{s}:{m}" for s, m in excluded)}
    if assay_manifest:
        identity["assay_manifest_sha256"] = sha256(assay_manifest)
    if identity_exclusions:
        identity["identity_exclusions_sha256"] = sha256(identity_exclusions)
    if excluded_calls:
        excluded_calls.sort(key=lambda r: (r["subject"], r["modality"], r["gene"], r["caller"]))
        write_tsv(out / "excluded_caller_calls.tsv", excluded_calls, CALLER_INPUT_FIELDS)
        identity["excluded_caller_rows"] = len(excluded_calls)
    if excluded_secondary:
        excluded_secondary.sort(key=lambda r: (r["subject"], r["modality"], r["gene"], r["method"]))
        write_tsv(out / "excluded_secondary_calls.tsv", excluded_secondary)
        identity["excluded_secondary_rows"] = len(excluded_secondary)
    manifest = {
        "schema_version": "panelhla-development-inputs-1",
        "truth_free": True,
        "singleton_policy": singleton_policy,
        "source_identifiers": {
            "caller_rows": "recovered harmonized_population_enriched.tsv",
            "method_rows": "recovered baseline_oof_calls.tsv",
        },
        "source_sha256": {
            "caller_rows": caller_source_sha256,
            "method_rows": method_source_sha256,
        },
        "output_sha256": {
            "normalized_caller_calls": sha256(calls_path),
            "normalized_secondary_calls": sha256(secondary_path),
        },
        "rows": {"caller": len(calls), "secondary": len(secondary)},
        "partial_rows": sum(r["call_status"] == "partial" for r in calls),
        "native_homozygous_rows": sum(
            r["homozygosity_basis"] == "caller_native_declaration" for r in calls
        ),
        "modalities": list(DEVELOPMENT_MODALITIES),
        "identity_controls": identity,
    }
    write_json(out / "input_manifest.json", manifest)
    return manifest


NESTED_CV_METHOD = "BestSingleTool_nestedCV"


def _outer_folds(secondary_path: str) -> dict[tuple[str, str], str]:
    """Subject-level outer folds recovered with the frozen best-single-caller predictions."""
    folds: dict[tuple[str, str], str] = {}
    for row in read_tsv(secondary_path):
        if row["method"] != NESTED_CV_METHOD:
            continue
        key = (row["subject"], row["modality"])
        if folds.setdefault(key, row["outer_fold"]) != row["outer_fold"]:
            raise ValueError(f"subject {key} has more than one outer fold")
    return folds


def refit_best_single_caller(calls_path: str, truth_path: str, secondary_path: str,
                             output_path: str, manifest_path: str) -> dict:
    """Refit best-single-caller selection on the recovered outer folds
    (decisions/20261009_nestedcv_refit.json).

    For each assay and fold, the panel caller with the most exact correct calls on the
    other folds' truth-retained loci is applied to every locus of the held-out fold.
    A held-out subject's truth never informs its own prediction. Ties go to the
    alphabetically first caller."""
    calls = read_tsv(calls_path)
    reject_truth_columns(calls, "nested-CV refit caller input")
    by_key = {(r["subject"], r["modality"], r["gene"], r["caller"]): r for r in calls}
    truth = {(r["subject"], r["modality"], r["gene"]):
             canonical_pair(r["truth_allele1"], r["truth_allele2"], r["gene"])
             for r in read_tsv(truth_path)}
    folds = _outer_folds(secondary_path)
    loci = sorted({(r["cohort"], r["subject"], r["superpopulation"], r["modality"], r["gene"])
                   for r in calls})
    unassigned = sorted({(s, m) for _, s, _, m, _ in loci if (s, m) not in folds})
    if unassigned:
        raise ValueError(f"subjects without an outer fold: {unassigned[:5]}")

    def correct(subject: str, modality: str, gene: str, caller: str) -> int:
        row = by_key.get((subject, modality, gene, caller))
        if not row or row["call_status"] != "callable":
            return 0
        return int(canonical_pair(row["allele1"], row["allele2"], gene)
                   == truth[(subject, modality, gene)])

    picks: dict[str, dict[str, dict]] = {}
    output = []
    for modality in DEVELOPMENT_MODALITIES:
        modality_truth = [key for key in truth if key[1] == modality]
        picks[modality] = {}
        for fold in sorted({folds[(s, m)] for _, s, _, m, _ in loci if m == modality}, key=int):
            training = [key for key in modality_truth if folds[(key[0], modality)] != fold]
            scores = {caller: sum(correct(*key, caller) for key in training)
                      for caller in PANELS[modality]}
            best = max(scores.values())
            pick = sorted(caller for caller, score in scores.items() if score == best)[0]
            picks[modality][fold] = {"caller": pick, "training_loci": len(training),
                                     "training_correct": scores}
            for cohort, subject, population, mod, gene in loci:
                if mod != modality or folds[(subject, modality)] != fold:
                    continue
                row = by_key.get((subject, modality, gene, pick))
                callable_ = bool(row) and row["call_status"] == "callable"
                output.append({
                    "cohort": cohort, "subject": subject, "superpopulation": population,
                    "modality": modality, "gene": gene, "method": NESTED_CV_METHOD,
                    "allele1": row["allele1"] if callable_ else "",
                    "allele2": row["allele2"] if callable_ else "",
                    "call_status": row["call_status"] if row else "missing",
                    "decision_reason": f"nestedcv_refit_pick:{pick}",
                    "analysis_scope": "exploratory_fitted",
                    "champion_tool": pick, "outer_fold": fold,
                })
    output.sort(key=lambda r: (r["subject"], r["modality"], r["gene"]))
    write_tsv(output_path, output)
    manifest = {
        "schema_version": "champhla-fitted-predictions-1",
        "decision": "decisions/20261009_nestedcv_refit.json",
        "method": NESTED_CV_METHOD,
        "truth_values_used_for_prediction": "training_folds_only",
        "tie_break": "alphabetical caller name",
        "picks": picks,
        "input_sha256": {"calls": sha256(calls_path), "truth": sha256(truth_path),
                         "secondary_folds": sha256(secondary_path)},
        "predictions_sha256": sha256(output_path),
        "rows": len(output),
    }
    write_json(manifest_path, manifest)
    return manifest


def refit_secondary_fitted_methods(calls_path: str, truth_path: str, secondary_path: str,
                                   raw_cc_policy: str, output_path: str,
                                   manifest_path: str) -> dict:
    """Refit MV-floor and MetaConsensus from v3.5.0 per-locus caller rows.

    The implementation lives in :mod:`champhla_confirmation.fitted` so its
    prediction surface can be tested without opening the development truth.  This
    path supplies truth only to fold-local training and never serializes it with the
    held-out predictions.
    """
    from .fitted import refit_fitted_methods

    calls = read_tsv(calls_path)
    reject_truth_columns(calls, "secondary fitted-method caller input")
    truth = {
        (row.get("cohort", ""), row["subject"], row["modality"], row["gene"]):
        canonical_pair(row["truth_allele1"], row["truth_allele2"], row["gene"])
        for row in read_tsv(truth_path)
    }
    predictions, manifest = refit_fitted_methods(
        calls, truth, _outer_folds(secondary_path), raw_cc_policy
    )
    write_tsv(output_path, predictions)
    manifest.update({
        "input_sha256": {
            "calls": sha256(calls_path),
            "truth": sha256(truth_path),
            "secondary_folds": sha256(secondary_path),
            "raw_cc_policy": sha256(raw_cc_policy),
        },
        "predictions_sha256": sha256(output_path),
        "rows": len(predictions),
    })
    write_json(manifest_path, manifest)
    return manifest


def combine_predictions(paths: list[str], output_path: str) -> None:
    """Concatenate prediction stages (truth-free first) into the evaluated file."""
    stages = [read_tsv(path) for path in paths]
    rows = [row for stage in stages for row in stage]
    keys = [(row["subject"], row["modality"], row["gene"], row["method"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate method/locus rows across prediction stages")
    leading = list(stages[0][0]) if stages and stages[0] else []
    fields = leading + sorted({f for row in rows for f in row}.difference(leading))
    rows.sort(key=lambda r: (r["subject"], r["modality"], r["gene"], r["method"]))
    write_tsv(output_path, rows, fields)


def score_frozen_nestedcv(secondary_path: str, truth_path: str, output_path: str) -> list[dict]:
    """Historical score of the replaced frozen selector on the current exact loci;
    reported once for transparency, never part of an inference family."""
    truth = {(r["subject"], r["modality"], r["gene"]):
             canonical_pair(r["truth_allele1"], r["truth_allele2"], r["gene"])
             for r in read_tsv(truth_path)}
    totals: dict[str, list[int]] = {}
    for row in read_tsv(secondary_path):
        key = (row["subject"], row["modality"], row["gene"])
        if row["method"] != NESTED_CV_METHOD or key not in truth:
            continue
        hit = (row["call_status"] == "callable" and row["allele1"] and row["allele2"]
               and canonical_pair(row["allele1"], row["allele2"], row["gene"]) == truth[key])
        tally = totals.setdefault(row["modality"], [0, 0])
        tally[0] += 1
        tally[1] += int(bool(hit))
    output = [{"modality": m, "loci": str(n), "correct": str(c)}
              for m, (n, c) in sorted(totals.items())]
    write_tsv(output_path, output, ["modality", "loci", "correct"])
    return output


def withheld_input_effect(excluded_calls: str, public_truth: str, work_dir: str,
                          output_path: str) -> list[dict]:
    """Reported sensitivity only, never an exclusion criterion: how the withheld inputs'
    plurality calls score at the exact endpoint (decisions/20261008_identity_check_na07000.json)."""
    fields = ["modality", "withheld_retained_loci", "withheld_consensus_correct"]
    # The v3.5.0 rerun applies the identity control in its signed roster, so its
    # withheld table is present but empty; there is then nothing to score.
    if not Path(excluded_calls).is_file() or not read_tsv(excluded_calls):
        write_tsv(output_path, [], fields)
        return []
    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    truth_path = work / "withheld_truth.tsv"
    prepare_development_truth(public_truth, excluded_calls, str(truth_path),
                              str(work / "withheld_truth_manifest.json"),
                              require_every_modality=False)
    consensus = {(r["subject"], r["modality"], r["gene"]): r
                 for r in build_consensus(read_tsv(excluded_calls))
                 if r["method"] == METHOD_PLURALITY}
    totals: dict[str, list[int]] = {}
    for row in read_tsv(truth_path):
        key = (row["subject"], row["modality"], row["gene"])
        truth = canonical_pair(row["truth_allele1"], row["truth_allele2"], row["gene"])
        call = consensus.get(key)
        correct = bool(call and call["allele1"] and call["allele2"]) and canonical_pair(
            call["allele1"], call["allele2"], row["gene"]) == truth
        tally = totals.setdefault(row["modality"], [0, 0])
        tally[0] += 1
        tally[1] += int(correct)
    output = [{"modality": modality, "withheld_retained_loci": str(loci),
               "withheld_consensus_correct": str(correct)}
              for modality, (loci, correct) in sorted(totals.items())]
    write_tsv(output_path, output, fields)
    return output


def identity_check(call_paths: list[str], assay_manifest: str, output_path: str) -> list[dict]:
    """Truth-free sample-identity evidence for every subject, including excluded inputs:
    official-manifest membership per assay and alleles shared between the WES and
    RNA-seq plurality genotypes at every gene called in both."""
    rows = [row for path in call_paths if Path(path).is_file() for row in read_tsv(path)]
    reject_truth_columns(rows, "identity-check caller input")
    admitted = {(r["sample_id"], r["modality"]) for r in read_tsv(assay_manifest)}
    consensus = {
        (r["subject"], r["modality"], r["gene"]): (r["allele1"], r["allele2"])
        for r in build_consensus(rows)
        if r["method"] == METHOD_PLURALITY and r["allele1"] and r["allele2"]
    }
    assays: dict[str, set[str]] = {}
    for row in rows:
        assays.setdefault(row["subject"], set()).add(row["modality"])
    output = []
    for subject in sorted(assays):
        genes = [g for g in ("A", "B", "C")
                 if (subject, "wes", g) in consensus and (subject, "rnaseq", g) in consensus]
        shared = sum(sum((Counter(consensus[(subject, "wes", g)])
                          & Counter(consensus[(subject, "rnaseq", g)])).values()) for g in genes)
        output.append({
            "subject": subject, "assays": ",".join(sorted(assays[subject])),
            **{f"{m}_in_assay_manifest": ("" if m not in assays[subject]
                                           else str(int((subject, m) in admitted)))
               for m in DEVELOPMENT_MODALITIES},
            "genes_compared": str(len(genes)),
            "alleles_shared": str(shared) if genes else "",
            "alleles_compared": str(2 * len(genes)) if genes else "",
        })
    write_tsv(output_path, output)
    return output


def _input_singleton_policy(calls_path: str) -> str:
    """The policy recorded beside a normalized caller table (older tables: abstain)."""
    manifest = Path(calls_path).with_name("input_manifest.json")
    if not manifest.exists():
        return "abstain"
    return str(read_json(manifest).get("singleton_policy", "abstain"))


def _locus_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row.get("cohort", ""), row["subject"], row["modality"], row["gene"])


def _family_gated_rows(raw_cc: list[dict], calls: list[dict[str, str]]) -> list[dict]:
    caller_rows = {(_locus_key(row), row["caller"]): row for row in calls}
    output = []
    for row in raw_cc:
        gated = dict(row)
        gated["method"] = "FamilyGatedCC"
        if row.get("decision_reason") == "challenger_override":
            families = supporting_families(row.get("supporting_callers", ""))
            if len(families) < DEFAULT_MIN_SUPPORTING_FAMILIES:
                champion = caller_rows.get((_locus_key(row), row.get("champion_caller", "")))
                if champion and champion.get("call_status") == "callable":
                    gated["allele1"], gated["allele2"] = champion["allele1"], champion["allele2"]
                    gated["call_status"] = "callable"
                else:
                    gated["allele1"] = gated["allele2"] = ""
                    gated["call_status"] = "missing"
                gated["decision_reason"] = "family_gate_rejected_override"
        output.append(gated)
    return output


def build_development_predictions(calls_path: str, secondary_path: str, truth_path: str | None,
                                  raw_cc_policy: str, output_path: str,
                                  manifest_path: str) -> dict:
    """Regenerate predictions before truth access on the full requested roster.

    ``truth_path`` is retained only for command-line compatibility and its
    contents are never read.  This closes the historical truth-dependent locus
    selection leak and permits ambiguity-aware secondary scoring.
    """
    calls = read_tsv(calls_path)
    secondary = read_tsv(secondary_path)
    requested_loci = {_locus_key(row) for row in calls}
    reject_truth_columns(calls, "development caller predictions")
    reject_truth_columns(secondary, "development secondary predictions")
    call_loci = {_locus_key(row) for row in calls}
    if call_loci != requested_loci:  # defensive invariant; deliberately truth-free
        raise ValueError("development caller locus accounting failed")

    raw_cc = predict_raw_cc(calls, raw_cc_policy)
    predictions = build_guarded_cc(calls, raw_cc)
    predictions.extend(raw_cc)
    predictions.extend(_family_gated_rows(raw_cc, calls))
    for row in calls:
        predictions.append({
            "cohort": row["cohort"], "subject": row["subject"],
            "superpopulation": row.get("superpopulation", ""),
            "modality": row["modality"], "gene": row["gene"],
            "method": f"Caller:{row['caller']}", "allele1": row["allele1"],
            "allele2": row["allele2"], "call_status": row["call_status"],
            "decision_reason": row.get("no_call_reason", "") or "individual_caller",
        })
    # All three historical fitted comparators are rebuilt after truth in their own
    # fold-local frozen stage. Historical secondary rows supply folds only and are
    # never eligible for release predictions.
    retained_frozen: set[str] = set()

    primary = {METHOD_PLURALITY}
    descriptive = {METHOD_BASELINE, METHOD_STRICT_MAJORITY}
    fitted = {METHOD_RAW_CC, METHOD_GUARDED_CC, "FamilyGatedCC",
              "BestSingleTool_nestedCV", "MVFlooredCC", "MetaConsensus"}
    for row in predictions:
        method = row["method"]
        row["analysis_scope"] = (
            "primary" if method in primary else
            "descriptive_comparator" if method in descriptive or method.startswith("Caller:") else
            "exploratory_fitted" if method in fitted else "secondary"
        )
    predictions.sort(key=lambda row: (*_locus_key(row), row["method"]))
    keys = [(*_locus_key(row), row["method"]) for row in predictions]
    if len(keys) != len(set(keys)):
        raise ValueError("duplicate method/locus prediction rows")
    leading_fields = [
        "cohort", "subject", "superpopulation", "modality", "gene",
        "method", "allele1", "allele2", "call_status", "decision_reason",
        "analysis_scope",
    ]
    all_fields = {field for row in predictions for field in row}
    output_fields = leading_fields + sorted(all_fields.difference(leading_fields))
    write_tsv(output_path, predictions, output_fields)
    method_counts: dict[str, int] = {}
    for row in predictions:
        method_counts[row["method"]] = method_counts.get(row["method"], 0) + 1
    manifest = {
        "schema_version": "panelhla-development-predictions-2",
        "truth_values_used_for_prediction": False,
        "truth_used_only_to_select_audited_loci": False,
        "prediction_universe": "all requested loci in normalized caller inputs",
        "singleton_policy": _input_singleton_policy(calls_path),
        "legacy_frozen_fitted_methods": sorted(
            method for method in retained_frozen if method_counts.get(method, 0)
        ),
        "legacy_frozen_fitted_release_eligible": False,
        "loci": len(requested_loci),
        "method_rows": dict(sorted(method_counts.items())),
        "input_sha256": {
            "calls": sha256(calls_path), "secondary": sha256(secondary_path),
            "raw_cc_policy": sha256(raw_cc_policy),
        },
        "predictions_sha256": sha256(output_path),
    }
    write_json(manifest_path, manifest)
    return manifest
