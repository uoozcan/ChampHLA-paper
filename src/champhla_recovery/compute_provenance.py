from __future__ import annotations

import csv
import re
from pathlib import Path

from champhla_confirmation.io import sha256, write_json, write_tsv


SCHEMA_VERSION = "panelhla-compute-smoke-1"
RECORD_TYPE = "single_sample_workflow_smoke"
SACCT_FIELDS = [
    "job_id", "job_name", "state", "exit_code", "alloc_cpus", "requested_memory",
    "elapsed_seconds", "total_cpu", "max_rss", "max_vmem", "node", "start", "end",
]
OUTPUT_FIELDS = [
    "schema_version", "record_type", "assay_route", "actual_input_type", "sample_id",
    "workflow_role", "tool", "process_name", "native_job_id", "nextflow_status",
    "exit_code", "trace_submit", "trace_start", "trace_complete",
    "trace_duration_seconds", "trace_realtime_seconds", "trace_cpus",
    "trace_requested_memory_bytes", "trace_peak_rss_bytes", "trace_peak_vmem_bytes",
    "slurm_state", "slurm_exit_code", "slurm_alloc_cpus",
    "slurm_requested_memory_bytes", "slurm_elapsed_seconds", "slurm_total_cpu_seconds",
    "slurm_max_rss_bytes", "slurm_max_vmem_bytes", "slurm_node", "slurm_start",
    "slurm_end", "execution_mode", "execution_artifact", "container_sha256",
    "caller_version", "caller_version_status", "workflow_commit", "workflow_dirty",
    "dsl_revision", "session_uuid", "run_name", "workflow_main_sha256",
    "workflow_config_sha256", "command_sha256", "launch_wrapper_sha256",
    "raw_trace_sha256", "raw_sacct_sha256", "wrapper_stdout_sha256",
    "nextflow_log_sha256", "source_manifest_sha256",
]

ROUTES = {
    "dna": {
        "assay_route": "dna_short_read_caller_route",
        "actual_input_type": "WGS-derived mate-aware HLA BAM",
        "sample_id": "HG00096",
        "stdout": "panelhla_vote_1427633.out",
        "nextflow_log": ".nextflow.log",
    },
    "rna": {
        "assay_route": "rna_seq_caller_route",
        "actual_input_type": "paired-end RNA-seq FASTQ",
        "sample_id": "HG00096",
        "stdout": "panelhla_rnaseq_1410978.out",
        "nextflow_log": ".nextflow.log.7",
    },
}

PROCESS_META = {
    "BAM_TO_FASTQ": ("preprocessing", "samtools BAM-to-FASTQ"),
    "OPTITYPE": ("caller", "OptiType"),
    "HLAHD_BAM": ("caller", "HLA-HD"),
    "HLAHD_FASTQ": ("caller", "HLA-HD"),
    "T1K_FASTQ": ("caller", "T1K"),
    "KOURAMI": ("caller", "Kourami"),
    "POLYSOLVER": ("caller", "POLYSOLVER"),
    "SPECHLA_BAM": ("caller", "SpecHLA"),
    "ARCASHLA_FASTQ": ("caller", "arcasHLA"),
    "SEQ2HLA": ("caller", "seq2HLA"),
    "AGGREGATE_RESULTS": ("integration", "ChampHLA aggregation"),
    "MAJORITY_VOTING": ("integration", "ChampHLA consensus"),
}

VERSION_FILES = {
    "HLA-HD": "hlahd_versions.yml",
    "OptiType": "optitype_versions.yml",
    "T1K": "t1k_versions.yml",
    "Kourami": "kourami_versions.yml",
    "POLYSOLVER": "polysolver_versions.yml",
    "SpecHLA": "spechla_versions.yml",
    "arcasHLA": "arcashla_versions.yml",
    "seq2HLA": "seq2hla_versions.yml",
}


def parse_duration(value: str) -> float:
    """Parse Nextflow/Slurm duration tokens into seconds."""
    value = value.strip()
    if not value:
        return 0.0
    if re.fullmatch(r"\d+(?::\d+){1,2}(?:\.\d+)?", value):
        parts = [float(part) for part in value.split(":")]
        if len(parts) == 2:
            return parts[0] * 60 + parts[1]
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    units = {"d": 86400.0, "h": 3600.0, "m": 60.0, "s": 1.0, "ms": 0.001}
    total = 0.0
    for number, unit in re.findall(r"(\d+(?:\.\d+)?)\s*(ms|[dhms])", value):
        total += float(number) * units[unit]
    if total == 0.0 and value not in {"0", "0s", "0ms"}:
        raise ValueError(f"unsupported duration: {value!r}")
    return total


def parse_memory(value: str) -> int:
    """Parse decimal Nextflow and binary Slurm memory strings into bytes."""
    value = value.strip()
    if not value:
        return 0
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([KMGT]?)(?:i?[Bb])?", value, re.I)
    if not match:
        raise ValueError(f"unsupported memory value: {value!r}")
    number, prefix = float(match.group(1)), match.group(2).upper()
    base = 1024 if not re.search(r"\s", value) else 1000
    power = {"": 0, "K": 1, "M": 2, "G": 3, "T": 4}[prefix]
    return round(number * (base ** power))


def _process_token(name: str) -> str:
    token = name.split("(", 1)[0].split(":")[-1].strip()
    if token not in PROCESS_META:
        raise ValueError(f"unknown workflow process: {name!r}")
    return token


def _read_trace(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _read_sacct(path: Path) -> dict[str, dict[str, str]]:
    parents: dict[str, dict[str, str]] = {}
    steps: dict[str, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for values in csv.reader(handle, delimiter="|"):
            if values and values[-1] == "":
                values.pop()
            if len(values) != len(SACCT_FIELDS):
                raise ValueError(f"invalid sacct row in {path}: {values!r}")
            row = dict(zip(SACCT_FIELDS, values))
            if row["job_id"].endswith(".batch"):
                steps[row["job_id"][:-len(".batch")]] = row
            elif "." not in row["job_id"]:
                if row["job_id"] in parents:
                    raise ValueError(f"duplicate Slurm job {row['job_id']} in {path}")
                parents[row["job_id"]] = row
    for job_id, row in parents.items():
        batch = steps.get(job_id, {})
        row["max_rss"] = batch.get("max_rss", "")
        row["max_vmem"] = batch.get("max_vmem", "")
    return parents


def _extract_log_metadata(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    patterns = {
        "session_uuid": r"Session UUID:\s*([^\s]+)",
        "run_name": r"Run name:\s*([^\s]+)",
        "dsl_revision": r"DSL2 - revision:\s*([^\s]+)",
    }
    result = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if not match:
            raise ValueError(f"missing {key} in {path}")
        result[key] = match.group(1)
    return result


def _hash_from_manifest(path: Path, suffix: str) -> str:
    matches = []
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, source = line.split("  ", 1)
        if source.endswith(suffix):
            matches.append(digest)
    if len(matches) != 1:
        raise ValueError(f"expected one manifest entry ending {suffix!r}; found {len(matches)}")
    return matches[0]


def _container_hashes(path: Path) -> dict[str, str]:
    result = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        digest, source = line.split(None, 1)
        result[Path(source).name] = digest
    return result


def _execution_artifact(command_run: Path) -> tuple[str, str]:
    text = command_run.read_text(encoding="utf-8", errors="replace")
    matches = sorted(set(re.findall(r"/[^\s'\"]+/([A-Za-z0-9._-]+\.sif)", text)))
    if len(matches) > 1:
        raise ValueError(f"multiple containers in {command_run}: {matches}")
    if matches:
        return "apptainer_sif", matches[0]
    if "SPECHLA" in command_run.name or "1427637" in command_run.name:
        return "native_local_install", "/projappl/project_2008084/SpecHLAx"
    return "host_process", ""


def _version(route_root: Path, tool: str) -> tuple[str, str]:
    filename = VERSION_FILES.get(tool)
    if not filename:
        return "", "not_applicable"
    path = route_root / "versions" / filename
    if not path.is_file():
        return "", "missing_version_artifact"
    text = path.read_text(encoding="utf-8", errors="replace")
    values = []
    for line in text.splitlines():
        match = re.match(r"\s*(?:hlahd|optitype|t1k|kourami|polysolver|spechla|arcashla|seq2hla):\s*(.*)$",
                         line, re.I)
        if match:
            values.append(match.group(1).strip().strip('"'))
    value = values[0] if values else ""
    if not value:
        return "", "empty_version_output"
    if value.lower().startswith("usage:"):
        return value, "unresolved_usage_output"
    return value, "reported_by_smoke_task"


def build_compute_smoke_registry(raw_root: str | Path, output_tsv: str | Path,
                                 output_manifest: str | Path) -> list[dict[str, object]]:
    raw = Path(raw_root).resolve()
    source_manifest = raw / "SHA256SUMS"
    if not source_manifest.is_file():
        raise ValueError("missing source SHA256SUMS")
    prefix = "/scratch/project_2008084/panelhla_provenance_20260928/"
    for line in source_manifest.read_text(encoding="utf-8").splitlines():
        expected, remote = line.split("  ", 1)
        relative = remote[len(prefix):] if remote.startswith(prefix) else remote
        local = raw / relative
        if not local.is_file() or sha256(local) != expected:
            raise ValueError(f"source artifact checksum mismatch: {relative}")

    container_hashes = _container_hashes(raw / "containers" / "container_sha256.txt")
    rows: list[dict[str, object]] = []
    seen_jobs: set[str] = set()
    workflow_revisions: set[tuple[str, str]] = set()
    for label, route in ROUTES.items():
        route_root = raw / label
        trace_path = route_root / "pipeline_info" / "execution_trace.txt"
        sacct_path = route_root / "slurm_sacct.psv"
        stdout_path = route_root / route["stdout"]
        log_path = route_root / route["nextflow_log"]
        sacct = _read_sacct(sacct_path)
        log_meta = _extract_log_metadata(log_path)
        commit = (route_root / "workflow" / "git_commit.txt").read_text().strip()
        dirty = bool((route_root / "workflow" / "git_status.txt").read_text().strip())
        workflow_revisions.add((commit, log_meta["dsl_revision"]))
        for trace in _read_trace(trace_path):
            job_id = trace["native_id"]
            if job_id in seen_jobs:
                raise ValueError(f"duplicate native job ID: {job_id}")
            seen_jobs.add(job_id)
            if job_id not in sacct:
                raise ValueError(f"missing Slurm accounting for job {job_id}")
            process = _process_token(trace["name"])
            role, tool = PROCESS_META[process]
            command = route_root / "task_commands" / f"{job_id}.command.sh"
            launch = route_root / "task_commands" / f"{job_id}.command.run"
            mode, artifact = _execution_artifact(launch)
            container_hash = container_hashes.get(artifact, "")
            if mode == "apptainer_sif" and not container_hash:
                raise ValueError(f"container digest unavailable for {artifact}")
            version, version_status = _version(route_root, tool)
            slurm = sacct[job_id]
            rows.append({
                "schema_version": SCHEMA_VERSION, "record_type": RECORD_TYPE,
                "assay_route": route["assay_route"],
                "actual_input_type": route["actual_input_type"],
                "sample_id": route["sample_id"], "workflow_role": role, "tool": tool,
                "process_name": process, "native_job_id": job_id,
                "nextflow_status": trace["status"], "exit_code": trace["exit"],
                "trace_submit": trace["submit"], "trace_start": trace["start"],
                "trace_complete": trace["complete"],
                "trace_duration_seconds": parse_duration(trace["duration"]),
                "trace_realtime_seconds": parse_duration(trace["realtime"]),
                "trace_cpus": trace["cpus"],
                "trace_requested_memory_bytes": parse_memory(trace["memory"]),
                "trace_peak_rss_bytes": parse_memory(trace["peak_rss"]),
                "trace_peak_vmem_bytes": parse_memory(trace["peak_vmem"]),
                "slurm_state": slurm["state"], "slurm_exit_code": slurm["exit_code"],
                "slurm_alloc_cpus": slurm["alloc_cpus"],
                "slurm_requested_memory_bytes": parse_memory(slurm["requested_memory"]),
                "slurm_elapsed_seconds": int(slurm["elapsed_seconds"]),
                "slurm_total_cpu_seconds": parse_duration(slurm["total_cpu"]),
                "slurm_max_rss_bytes": parse_memory(slurm["max_rss"]),
                "slurm_max_vmem_bytes": parse_memory(slurm["max_vmem"]),
                "slurm_node": slurm["node"], "slurm_start": slurm["start"],
                "slurm_end": slurm["end"], "execution_mode": mode,
                "execution_artifact": artifact, "container_sha256": container_hash,
                "caller_version": version, "caller_version_status": version_status,
                "workflow_commit": commit, "workflow_dirty": str(dirty).lower(),
                **log_meta,
                "workflow_main_sha256": sha256(route_root / "workflow" / "main.nf"),
                "workflow_config_sha256": sha256(route_root / "workflow" / "nextflow.config"),
                "command_sha256": sha256(command), "launch_wrapper_sha256": sha256(launch),
                "raw_trace_sha256": sha256(trace_path), "raw_sacct_sha256": sha256(sacct_path),
                "wrapper_stdout_sha256": sha256(stdout_path),
                "nextflow_log_sha256": sha256(log_path),
                "source_manifest_sha256": sha256(source_manifest),
            })

    rows.sort(key=lambda row: (str(row["assay_route"]), int(str(row["native_job_id"]))))
    write_tsv(output_tsv, rows, OUTPUT_FIELDS)
    manifest = {
        "schema_version": "panelhla-compute-smoke-manifest-1",
        "record_type": RECORD_TYPE,
        "source_manifest_sha256": sha256(source_manifest),
        "output_tsv": Path(output_tsv).name,
        "output_tsv_sha256": sha256(output_tsv),
        "row_count": len(rows),
        "caller_task_count": sum(row["workflow_role"] == "caller" for row in rows),
        "workflow_revisions": [
            {"workflow_commit": commit, "dsl_revision": revision}
            for commit, revision in sorted(workflow_revisions)
        ],
        "interpretation_boundary": (
            "Current HG00096 single-sample workflow smoke measurements; not historical "
            "development-cohort resource use, monetary cost, or cohort-scale estimates."
        ),
    }
    write_json(output_manifest, manifest)
    return rows
