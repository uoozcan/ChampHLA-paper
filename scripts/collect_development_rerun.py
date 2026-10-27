#!/usr/bin/env python3
"""Collect checksum-valid v3.5.0 sample runs into truth-free paper inputs.

Every selected sample must pass the same completion/hash/release validator used by
the submission controller. The output contains one row for every frozen panel
caller and HLA-A/B/C locus; absent or failed outputs remain explicit non-calls.
T1K count, quality, schema, disposition and secondary-candidate fields are emitted
to a separate provenance table and are required whenever T1K produced output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from champhla_confirmation.development import (  # noqa: E402
    CALLER_DATABASE_PROVENANCE,
    CALLER_INPUT_FIELDS,
    INPUT_REFERENCE_BUILD,
)
from champhla_confirmation.hla_reference import HLAReference  # noqa: E402
from champhla_confirmation.io import read_tsv, sha256, write_json, write_tsv  # noqa: E402
from champhla_confirmation.panels import GENES, PANELS  # noqa: E402
from champhla_confirmation.parsers import native_homozygous_pair  # noqa: E402
from champhla_confirmation.schema import normalize_caller_row  # noqa: E402
from manage_development_batches import (  # noqa: E402
    DEFAULT_RELEASE_COMMIT,
    read_manifest,
    validate_sample,
)

DEFAULT_RUN_ROOT = Path(
    "/scratch/project_2008084/champhla_publication_remediation/development"
)
DEFAULT_MANIFEST = ROOT / "cohorts/development_rerun_manifest.tsv"
IPD = ROOT / "resources/ipd_imgt_hla/3.65.0"
CALLER_TO_DIRECTORY = {
    "HLA-HD": "hlahd",
    "OptiType": "optitype",
    "POLYSOLVER": "polysolver",
    "SpecHLA": "spechla",
    "T1K": "t1k",
    "ArcasHLA": "arcashla",
}
TOOL_TO_CALLER = {directory: caller for caller, directory in CALLER_TO_DIRECTORY.items()}
T1K_FIELDS = (
    "subject", "modality", "gene", "num_diff_alleles", "quality_1", "quality_2",
    "disposition", "input_schema", "allele_1_raw", "allele_2_raw",
    "secondary_alleles_raw", "parser_audit_path", "parser_audit_sha256",
    "raw_genotype_sha256",
)
RUN_FIELDS = (
    "subject", "modality", "batch_id", "slurm_job_id", "release_commit",
    "aggregated_calls_path", "aggregated_calls_sha256", "panel_provenance_sha256",
    "execution_trace_sha256", "caller_dispositions_sha256", "completion_sha256_sha256",
    "input_provenance_sha256", "input_sha256_manifest_sha256",
    "container_sha256_manifest_sha256", "workflow_files_sha256_manifest_sha256",
    "environment_sha256", "nextflow_command_sha256", "result_files_inventory_sha256",
    "detected_build", "sample_complete",
)
CALLER_RUN_FIELDS = (
    "subject", "modality", "batch_id", "slurm_job_id", "caller",
    "output_file_count", "trace_statuses", "disposition", "callable_genes",
    "partial_genes", "noncall_genes", "caller_dispositions_sha256",
)
CELL_COMPARISON_FIELDS = (
    "subject", "modality", "gene", "caller", "stored_call_status",
    "stored_allele1", "stored_allele2", "rerun_call_status", "rerun_allele1",
    "rerun_allele2", "same_state_and_pair", "difference_class",
)


def _reference() -> HLAReference:
    return HLAReference.from_files(
        "3.65.0", IPD / "Allelelist.txt",
        deleted_alleles=IPD / "Deleted_alleles.txt",
        p_groups=IPD / "wmda/hla_nom_p.txt",
        g_groups=IPD / "wmda/hla_nom_g.txt",
    )


def find_summary(sample_dir: Path, sample: str, directory: str) -> Path | None:
    caller_dir = sample_dir / directory
    if not caller_dir.is_dir():
        return None
    exact = caller_dir / f"{sample}_{directory}.txt"
    if exact.is_file():
        return exact
    candidates = sorted(caller_dir.glob(f"*_{directory}.txt"))
    preferred = [path for path in candidates if path.name.startswith(f"{sample}_")]
    chosen = preferred or candidates
    return chosen[0] if chosen else None


def _relative_to_run(path: Path, run_root: Path) -> str:
    return path.relative_to(run_root).as_posix()


def _dispositions(sample_root: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(sample_root / "caller_dispositions.tsv")
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        directory = row["caller"].strip().lower()
        caller = TOOL_TO_CALLER.get(directory)
        if caller is None:
            raise ValueError(
                f"unknown caller directory {row['caller']!r} in {sample_root}"
            )
        if caller in result:
            raise ValueError(f"duplicate caller disposition for {caller} in {sample_root}")
        result[caller] = row
    return result


def _t1k_audit(sample_root: Path, run_root: Path) -> tuple[dict[str, dict], list[dict]]:
    reports = list((sample_root / "results").rglob("*.parser.json"))
    if len(reports) != 1:
        raise ValueError(f"expected exactly one T1K parser audit in {sample_root}, found {len(reports)}")
    path = reports[0]
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "valid" or payload.get("counts", {}).get("invalid") != 0:
        raise ValueError(f"invalid T1K parser audit: {path}")
    by_gene: dict[str, dict] = {}
    output = []
    for row in payload.get("rows", []):
        gene = str(row.get("gene", "")).replace("HLA-", "")
        if gene not in GENES:
            continue
        if gene in by_gene:
            raise ValueError(f"duplicate T1K parser row for {gene}: {path}")
        by_gene[gene] = row
        output.append({
            "subject": sample_root.name,
            "modality": sample_root.parent.name,
            "gene": gene,
            "num_diff_alleles": row.get("num_diff_alleles", ""),
            "quality_1": row.get("quality_1", ""),
            "quality_2": row.get("quality_2", ""),
            "disposition": row.get("disposition", ""),
            "input_schema": row.get("input_schema", ""),
            "allele_1_raw": row.get("allele_1_raw", ""),
            "allele_2_raw": row.get("allele_2_raw", ""),
            "secondary_alleles_raw": row.get("secondary_alleles_raw", ""),
            "parser_audit_path": _relative_to_run(path, run_root),
            "parser_audit_sha256": sha256(path),
            "raw_genotype_sha256": payload.get("input_sha256", ""),
        })
    if set(by_gene) != set(GENES):
        raise ValueError(f"T1K audit lacks class-I rows in {path}: {sorted(by_gene)}")
    return by_gene, output


def _aggregate_rows(path: Path, sample: str, modality: str) -> dict[tuple[str, str], dict]:
    result: dict[tuple[str, str], dict] = {}
    for row in read_tsv(path):
        if row.get("sample") != sample or row.get("modality") != modality:
            raise ValueError(f"aggregate identity mismatch in {path}: {row}")
        caller = TOOL_TO_CALLER.get(row.get("tool", "").lower())
        gene = row.get("gene", "").replace("HLA-", "").upper()
        if caller not in PANELS[modality] or gene not in GENES:
            raise ValueError(f"unexpected aggregate caller/gene in {path}: {row}")
        key = (caller, gene)
        if key in result:
            raise ValueError(f"duplicate aggregate row {key} in {path}")
        callable_token = row.get("is_callable", "").strip().lower()
        if callable_token not in {"0", "1", "false", "true"}:
            raise ValueError(f"aggregate has invalid is_callable value: {row}")
        result[key] = {**row, "_is_callable": callable_token in {"1", "true"}}
    return result


def _native_from_summary(summary: Path | None, caller: str, gene: str, pair: tuple[str, str]) -> bool:
    if summary is None or caller not in {"HLA-HD", "ArcasHLA"}:
        return False
    declared = native_homozygous_pair(
        caller, summary.read_text(encoding="utf-8", errors="replace"), gene
    )
    return declared == pair


ARCASHLA_VERSION_RE = re.compile(r"arcashla:\s*([0-9]+(?:\.[0-9]+)*)", re.I)


# The v3.5.0 module's version probe printed nothing in every run, so the release is
# also read from the pinned container recorded in each sample's container_sha256.txt.
# arcashla.sif 60c42737... was inspected on Roihu on 2026-10-25: a 14 May 2020 master
# checkout (47469f58) whose scripts declare __version__ = '0.2.0'.
ARCASHLA_CONTAINER_VERSIONS = {
    "60c42737ccb8c0fa91beef256437028b64d75451ca16e4bf90bb849ba0b6c05c": (0, 2, 0),
}


def arcashla_version(result_sample: Path) -> tuple[int, ...] | None:
    """arcasHLA release from the sample's versions.yml or, failing that, its pinned
    container digest; None (abstain) when neither identifies it."""
    path = result_sample / "arcashla" / "versions.yml"
    if path.is_file():
        match = ARCASHLA_VERSION_RE.search(path.read_text(encoding="utf-8", errors="replace"))
        if match:
            return tuple(int(part) for part in match.group(1).split("."))
    containers = result_sample.parent.parent / "container_sha256.txt"
    if containers.is_file():
        for line in containers.read_text(encoding="utf-8", errors="replace").splitlines():
            fields = line.split()
            if len(fields) >= 2 and fields[-1].endswith("arcashla.sif"):
                return ARCASHLA_CONTAINER_VERSIONS.get(fields[0])
    return None


def native_completion_eligible(caller: str, result_sample: Path) -> bool:
    """decisions/20261008_singleton_native_homozygosity.json: HLA-HD writes '-' for the
    second allele of a homozygous call, and arcasHLA releases before 0.4.0 report a
    homozygous genotype as one allele. From 0.4.0, or when the version cannot be read,
    an arcasHLA single allele is not a declaration and the row abstains."""
    if caller == "HLA-HD":
        return True
    if caller == "ArcasHLA":
        version = arcashla_version(result_sample)
        return version is not None and version < (0, 4, 0)
    return False


def _cell_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return row["subject"], row["modality"], row["gene"], row["caller"]


def _cell_value(row: dict[str, str] | None) -> tuple[str, str, str]:
    if row is None:
        return "absent", "", ""
    return row.get("call_status", ""), row.get("allele1", ""), row.get("allele2", "")


def compare_stored_and_rerun_calls(
    stored: list[dict[str, str]], rerun: list[dict[str, str]]
) -> list[dict[str, object]]:
    """Truth-free, cell-by-cell comparison required by SR-005."""
    stored_by_key = {_cell_key(row): row for row in stored}
    rerun_by_key = {_cell_key(row): row for row in rerun}
    if len(stored_by_key) != len(stored) or len(rerun_by_key) != len(rerun):
        raise ValueError("duplicate caller cell in stored or rerun inputs")
    output = []
    for key in sorted(set(stored_by_key) | set(rerun_by_key)):
        before = _cell_value(stored_by_key.get(key))
        after = _cell_value(rerun_by_key.get(key))
        if key not in stored_by_key:
            difference = "new_rerun_cell"
        elif key not in rerun_by_key:
            difference = "stored_cell_missing_from_rerun"
        elif before == after:
            difference = "identical"
        elif before[0] == "callable" and after[0] != "callable":
            difference = "callable_to_noncall"
        elif before[0] != "callable" and after[0] == "callable":
            difference = "noncall_to_callable"
        elif before[0] == after[0] == "callable":
            difference = "call_changed"
        else:
            difference = "noncall_state_changed"
        output.append({
            "subject": key[0], "modality": key[1], "gene": key[2], "caller": key[3],
            "stored_call_status": before[0], "stored_allele1": before[1],
            "stored_allele2": before[2], "rerun_call_status": after[0],
            "rerun_allele1": after[1], "rerun_allele2": after[2],
            "same_state_and_pair": int(before == after), "difference_class": difference,
        })
    return output


def abstain_native_declarations(calls: list[dict[str, str]]) -> list[dict[str, str]]:
    """Build the predeclared abstain-all sensitivity input without reading truth."""
    output = []
    for source in calls:
        row = dict(source)
        if row.get("homozygosity_basis") == "caller_native_declaration":
            row["allele1"] = row["allele2"] = ""
            row["call_status"] = "partial"
            row["no_call_reason"] = "sensitivity_abstain_native_homozygous_declaration"
        output.append(row)
    return output


def collect_sample(row: dict[str, str], run_root: Path, reference: HLAReference,
                   release_commit: str) -> tuple[list[dict], list[dict], dict, list[dict]]:
    subject, modality = row["sample_id"], row["modality"]
    sample_root = run_root / "samples" / modality / subject
    errors = validate_sample(run_root, row, release_commit)
    if errors:
        raise ValueError(f"{subject} {modality} is incomplete/invalid: {'; '.join(errors)}")
    aggregate = sample_root / "results/consensus/aggregated_calls.tsv"
    if not aggregate.is_file():
        raise ValueError(f"missing aggregate: {aggregate}")
    raw = _aggregate_rows(aggregate, subject, modality)
    dispositions = _dispositions(sample_root)
    if set(dispositions) != set(PANELS[modality]):
        raise ValueError(f"caller disposition panel mismatch for {subject} {modality}")

    t1k_rows: dict[str, dict] = {}
    t1k_provenance: list[dict] = []
    if int(dispositions["T1K"]["output_file_count"]) > 0:
        t1k_rows, t1k_provenance = _t1k_audit(sample_root, run_root)

    calls = []
    result_sample = sample_root / "results" / subject
    for caller in PANELS[modality]:
        directory = CALLER_TO_DIRECTORY[caller]
        summary = find_summary(result_sample, subject, directory)
        summary_path = _relative_to_run(summary, run_root) if summary else ""
        summary_hash = sha256(summary) if summary else ""
        database_version, database_basis = CALLER_DATABASE_PROVENANCE[caller]
        for gene in GENES:
            found = raw.get((caller, gene))
            base = {
                "cohort": "1000G-development-rerun-v3.5.0",
                "subject": subject,
                "population": row.get("population", ""),
                "modality": modality,
                "gene": gene,
                "caller": caller,
                "allele1_raw": found.get("allele1", "") if found else "",
                "allele2_raw": found.get("allele2", "") if found else "",
                "database_version": database_version,
                "database_version_basis": database_basis,
                "input_reference_build": INPUT_REFERENCE_BUILD[modality],
                "source_path": summary_path,
                "source_sha256": summary_hash,
            }
            normalized = normalize_caller_row(base, reference=reference, singleton_policy="abstain")
            is_callable = bool(found and found["_is_callable"])
            # The v3.5.0 aggregate leaves a caller-declared homozygote non-callable; the
            # signed primary policy completes it from the caller's own summary, and the
            # abstain sensitivity table below turns it back into an abstention.
            declared = None
            if (not is_callable and found and summary is not None
                    and native_completion_eligible(caller, result_sample)):
                declared = native_homozygous_pair(
                    caller, summary.read_text(encoding="utf-8", errors="replace"), gene)
            if declared:
                completed = normalize_caller_row(
                    {**base, "allele2_raw": base["allele1_raw"]},
                    reference=reference, singleton_policy="abstain")
                if (completed["call_status"] != "callable"
                        or (completed["allele1"], completed["allele2"]) != tuple(declared)):
                    raise ValueError(
                        f"declared homozygote disagrees with the aggregate at "
                        f"{subject} {modality} {caller} {gene}")
                normalized = completed
                # keep the caller's literal output; only the normalized pair is completed
                normalized["allele2_raw"] = base["allele2_raw"]
                normalized["homozygosity_basis"] = "caller_native_declaration"
                is_callable = True
            if declared:
                pass
            elif is_callable:
                pair = (normalized["allele1"], normalized["allele2"])
                if normalized["call_status"] != "callable":
                    raise ValueError(
                        f"aggregate marks an unparseable pair callable at "
                        f"{subject} {modality} {caller} {gene}"
                    )
                if caller == "T1K":
                    audit = t1k_rows.get(gene)
                    if not audit:
                        raise ValueError(f"callable T1K {subject} {modality} {gene} lacks audit")
                    if audit.get("disposition") not in {
                        "complete_heterozygous", "native_homozygous"
                    }:
                        raise ValueError(
                            f"callable T1K aggregate contradicts parser disposition at "
                            f"{subject} {modality} {gene}: {audit.get('disposition')}"
                        )
                    native = audit.get("disposition") == "native_homozygous"
                    if native and pair[0] != pair[1]:
                        raise ValueError(f"T1K native homozygote is not duplicated at {subject} {gene}")
                    normalized["homozygosity_basis"] = (
                        "caller_native_declaration" if native else "two_alleles"
                    )
                elif _native_from_summary(summary, caller, gene, pair):
                    normalized["homozygosity_basis"] = "caller_native_declaration"
            else:
                if found and normalized["call_status"] == "callable":
                    raise ValueError(
                        f"aggregate marks a complete pair non-callable at "
                        f"{subject} {modality} {caller} {gene}"
                    )
                disposition = dispositions[caller]["disposition"]
                normalized["no_call_reason"] = (
                    "no_class_i_pair_after_parser" if disposition == "outputs_present"
                    # NCI-60: the pinned release cannot run POLYSOLVER from FASTQ
                    # (decisions/20261026_nci60_v350_regeneration.json).
                    else "declared_non_call_fastq_input"
                    if disposition == "declared_non_call_fastq_input"
                    else "caller_task_failed_or_explicit_non_call"
                )
                if caller == "T1K" and gene in t1k_rows:
                    t1k_disposition = t1k_rows[gene].get("disposition", "")
                    if t1k_disposition in {"complete_heterozygous", "native_homozygous"}:
                        raise ValueError(
                            f"T1K parser call is absent from aggregate at {subject} {modality} {gene}"
                        )
                    normalized["no_call_reason"] = f"t1k_{t1k_disposition}"
                    if t1k_disposition == "partial_after_quality_filter":
                        normalized["call_status"] = "partial"
            normalized["caller_version_provenance"] = "per-sample versions.yml in checksummed result tree"
            normalized["container_provenance"] = "per-sample container_sha256.txt"
            calls.append({field: normalized.get(field, "") for field in CALLER_INPUT_FIELDS})

    panel = sample_root / "results/pipeline_info/panel_provenance.json"
    trace = sample_root / "results/pipeline_info/execution_trace.txt"
    input_provenance = sample_root / "input_provenance.tsv"
    detected = read_tsv(input_provenance)[0]["detected_build"]
    run_name = json.loads(panel.read_text(encoding="utf-8"))["run_name"]
    match = re.search(r"_(\d+)$", run_name)
    if not match:
        raise ValueError(f"run name has no Slurm job id: {run_name}")
    run = {
        "subject": subject,
        "modality": modality,
        "batch_id": row["batch_id"],
        "slurm_job_id": match.group(1),
        "release_commit": release_commit,
        "aggregated_calls_path": _relative_to_run(aggregate, run_root),
        "aggregated_calls_sha256": sha256(aggregate),
        "panel_provenance_sha256": sha256(panel),
        "execution_trace_sha256": sha256(trace),
        "caller_dispositions_sha256": sha256(sample_root / "caller_dispositions.tsv"),
        "completion_sha256_sha256": sha256(sample_root / "completion_sha256.txt"),
        "input_provenance_sha256": sha256(input_provenance),
        "input_sha256_manifest_sha256": sha256(sample_root / "input_sha256.txt"),
        "container_sha256_manifest_sha256": sha256(sample_root / "container_sha256.txt"),
        "workflow_files_sha256_manifest_sha256": sha256(
            sample_root / "workflow_files_sha256.txt"
        ),
        "environment_sha256": sha256(sample_root / "environment.txt"),
        "nextflow_command_sha256": sha256(sample_root / "nextflow_command.sh"),
        "result_files_inventory_sha256": sha256(sample_root / "result_files_sha256.txt"),
        "detected_build": detected,
        "sample_complete": "1",
    }
    disposition_hash = sha256(sample_root / "caller_dispositions.tsv")
    caller_runs = []
    for caller in PANELS[modality]:
        caller_calls = [call for call in calls if call["caller"] == caller]
        caller_runs.append({
            "subject": subject,
            "modality": modality,
            "batch_id": row["batch_id"],
            "slurm_job_id": run["slurm_job_id"],
            "caller": caller,
            "output_file_count": dispositions[caller]["output_file_count"],
            "trace_statuses": dispositions[caller]["trace_statuses"],
            "disposition": dispositions[caller]["disposition"],
            "callable_genes": sum(call["call_status"] == "callable" for call in caller_calls),
            "partial_genes": sum(call["call_status"] == "partial" for call in caller_calls),
            "noncall_genes": sum(call["call_status"] != "callable" for call in caller_calls),
            "caller_dispositions_sha256": disposition_hash,
        })
    return calls, t1k_provenance, run, caller_runs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--batch-id", action="append", default=[])
    parser.add_argument("--release-commit", default=DEFAULT_RELEASE_COMMIT)
    parser.add_argument(
        "--stored-calls", type=Path,
        default=ROOT / "data/development/normalized_caller_calls.tsv",
        help="historical normalized calls used only for the truth-free SR-005 comparison",
    )
    parser.add_argument(
        "--no-stored-calls", action="store_true",
        help="skip the stored-to-rerun comparison (a roster with no stored calls, such as "
             "the frozen extension)",
    )
    args = parser.parse_args(argv)

    rows = read_manifest(args.manifest)
    if args.batch_id:
        unknown = set(args.batch_id) - {row["batch_id"] for row in rows}
        if unknown:
            raise SystemExit(f"unknown batches: {sorted(unknown)}")
        rows = [row for row in rows if row["batch_id"] in set(args.batch_id)]
    reference = _reference()
    calls: list[dict] = []
    t1k: list[dict] = []
    runs: list[dict] = []
    caller_runs: list[dict] = []
    for row in rows:
        sample_calls, sample_t1k, sample_run, sample_caller_runs = collect_sample(
            row, args.run_root, reference, args.release_commit
        )
        calls.extend(sample_calls)
        t1k.extend(sample_t1k)
        runs.append(sample_run)
        caller_runs.extend(sample_caller_runs)
    expected = sum(len(PANELS[row["modality"]]) * len(GENES) for row in rows)
    if len(calls) != expected:
        raise SystemExit(f"caller-row accounting failed: {len(calls)} != {expected}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    calls_path = args.output_dir / "normalized_caller_calls.tsv"
    t1k_path = args.output_dir / "t1k_parser_provenance.tsv"
    runs_path = args.output_dir / "sample_run_provenance.tsv"
    caller_runs_path = args.output_dir / "caller_run_state.tsv"
    comparison_path = args.output_dir / "stored_vs_rerun_cells.tsv"
    selected_manifest_path = args.output_dir / "selected_input_manifest.tsv"
    write_tsv(calls_path, calls, CALLER_INPUT_FIELDS)
    write_tsv(t1k_path, t1k, T1K_FIELDS)
    write_tsv(runs_path, runs, RUN_FIELDS)
    write_tsv(caller_runs_path, caller_runs, CALLER_RUN_FIELDS)
    stored = [] if args.no_stored_calls else read_tsv(args.stored_calls)
    comparison = [] if args.no_stored_calls else compare_stored_and_rerun_calls(stored, calls)
    write_tsv(comparison_path, comparison, CELL_COMPARISON_FIELDS)
    write_tsv(selected_manifest_path, rows, list(rows[0]))
    sensitivity_dir = args.output_dir / "sensitivity_abstain"
    sensitivity_dir.mkdir(parents=True, exist_ok=True)
    sensitivity_calls_path = sensitivity_dir / "normalized_caller_calls.tsv"
    sensitivity_calls = abstain_native_declarations(calls)
    write_tsv(sensitivity_calls_path, sensitivity_calls, CALLER_INPUT_FIELDS)
    source_hash = {"collected_calls": sha256(calls_path)}
    primary_input_manifest = {
        "schema_version": "champhla-development-rerun-inputs-1",
        "truth_free": True,
        "singleton_policy": "native_declaration",
        "source_sha256": source_hash,
        "output_sha256": {"normalized_caller_calls": sha256(calls_path)},
    }
    sensitivity_input_manifest = {
        "schema_version": "champhla-development-rerun-inputs-1",
        "truth_free": True,
        "singleton_policy": "abstain",
        "source_sha256": source_hash,
        "output_sha256": {"normalized_caller_calls": sha256(sensitivity_calls_path)},
    }
    write_json(args.output_dir / "input_manifest.json", primary_input_manifest)
    write_json(sensitivity_dir / "input_manifest.json", sensitivity_input_manifest)
    manifest = {
        "schema_version": "champhla-development-rerun-collection-2",
        "truth_free": True,
        "release_commit": args.release_commit,
        "source_manifest_sha256": sha256(args.manifest),
        "selected_input_manifest_sha256": sha256(selected_manifest_path),
        "selected_batches": sorted(set(row["batch_id"] for row in rows)),
        "sample_assays": len(rows),
        "caller_rows": len(calls),
        "callable_rows": sum(row["call_status"] == "callable" for row in calls),
        "explicit_noncall_rows": sum(row["call_status"] != "callable" for row in calls),
        "t1k_audit_rows": len(t1k),
        "caller_run_state_rows": len(caller_runs),
        "stored_vs_rerun_cell_rows": len(comparison),
        "stored_vs_rerun_changed_cells": sum(
            row["same_state_and_pair"] == 0 for row in comparison
        ),
        "stored_calls_sha256": "" if args.no_stored_calls else sha256(args.stored_calls),
        "output_sha256": {
            calls_path.name: sha256(calls_path),
            t1k_path.name: sha256(t1k_path),
            runs_path.name: sha256(runs_path),
            caller_runs_path.name: sha256(caller_runs_path),
            comparison_path.name: sha256(comparison_path),
            selected_manifest_path.name: sha256(selected_manifest_path),
            "sensitivity_abstain/normalized_caller_calls.tsv": sha256(sensitivity_calls_path),
        },
    }
    write_json(args.output_dir / "collection_manifest.json", manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
