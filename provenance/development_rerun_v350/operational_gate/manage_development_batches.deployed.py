#!/usr/bin/env python3
"""Submit and validate small, truth-free ChampHLA development rerun batches.

Submission is deliberately opt-in (``submit --execute``). A sample is skipped only
when its completion marker, completion checksum, result checksum inventory, caller
dispositions, Nextflow exit status and release provenance all validate.

``control`` is one stateless pass of the storage-gated controller. It re-derives
every sample's state from its artifacts, the ledgers and Slurm, submits only what
fits under the free-space and running-job gates, and stops for a human whenever a
failed sample has no recorded failure class. A failed sample is resubmitted only
after it is classified as a storage, scheduler or input-transfer failure.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "cohorts/development_rerun_manifest.tsv"
DEFAULT_RUN_ROOT = Path(
    "/scratch/project_2008084/champhla_publication_remediation/development"
)
DEFAULT_RUNNER = Path(
    "/scratch/project_2008084/champhla_publication_remediation/paper/"
    "scripts/roihu_run_development_sample.sbatch"
)
DEFAULT_RELEASE_COMMIT = "66d949da90861da6cf60cf1d4bee2f094f2518bd"
LEDGER_FIELDS = (
    "submitted_utc",
    "batch_id",
    "sample_id",
    "modality",
    "slurm_job_id",
    "release_commit",
    "prune_on_success",
)
RETRY_LEDGER_FIELDS = (
    "submitted_utc",
    "sample_id",
    "modality",
    "attempt",
    "slurm_job_id",
    "retry_of_job_id",
    "failure_class",
    "release_commit",
    "prune_on_success",
)
CLASSIFICATION_FIELDS = (
    "classified_utc",
    "sample_id",
    "modality",
    "slurm_job_id",
    "failure_class",
    "classified_by",
    "note",
)
FAILURE_CLASSES = (
    "input",
    "input_transfer",
    "integrity",
    "storage",
    "storage_deferred",
    "scheduler",
    "routing",
    "caller",
    "parser",
    "biological_non_call",
)
# Only failures that say nothing about the sample or the callers may be retried.
RETRYABLE_CLASSES = frozenset({"storage", "storage_deferred", "scheduler", "input_transfer"})
# Exit code of the runner's pre-staging free-space gate: nothing was staged, so the
# attempt is recorded as storage_deferred and does not count against --max-attempts.
STORAGE_GATE_EXIT = 10
# Exit code of the runner when the project quota was exhausted while it ran, seen by
# its storage watcher or in a task log. Tools such as HLA-HD can exit 0 on truncated
# intermediates (2026-10-15/16 incident), so such a run never counts as complete.
STORAGE_TAINT_EXIT = 11
# More gate deferrals than this in one pass means the headroom probe or the budget is
# wrong; the controller stops rather than cycling jobs that cannot start.
MAX_DEFERRALS_PER_PASS = 2
# Slurm accounting can lag the queue by a pass; these states are not yet a failure.
UNSETTLED_STATES = frozenset({
    "UNKNOWN", "PENDING", "RUNNING", "COMPLETING", "CONFIGURING", "REQUEUED",
    "RESIZING", "SUSPENDED",
})
DEFAULT_RESERVE_GIB = {"wes": 60, "rnaseq": 25}
DEFAULT_MIN_FREE_GIB = 50
DEFAULT_MAX_ATTEMPTS = 3
SCRATCH_PATH = Path("/scratch/project_2008084")
JOB_NAME = "champhla_dev"


@contextmanager
def locked_ledger(path: Path):
    """Open an append ledger under an inter-process lock on POSIX and Windows."""
    if sys.platform == "win32":
        import msvcrt

        lock_path = path.with_suffix(path.suffix + ".lock")
        with lock_path.open("a+b") as lock:
            lock.seek(0, 2)
            if lock.tell() == 0:
                lock.write(b"0")
                lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
            try:
                with path.open("a+", newline="", encoding="utf-8") as handle:
                    yield handle
            finally:
                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        with path.open("a+", newline="", encoding="utf-8") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            try:
                yield handle
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def checksum_rows(path: Path) -> list[tuple[str, Path]]:
    rows: list[tuple[str, Path]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        fields = raw.split(maxsplit=1)
        if len(fields) != 2 or len(fields[0]) != 64:
            raise ValueError(f"malformed checksum row {path}:{number}")
        rows.append((fields[0], Path(fields[1].lstrip(" *"))))
    if not rows:
        raise ValueError(f"empty checksum inventory: {path}")
    return rows


def verify_checksum_file(path: Path) -> None:
    for expected, target in checksum_rows(path):
        if not target.is_file():
            raise ValueError(f"checksummed file is missing: {target}")
        observed = sha256(target)
        if observed != expected:
            raise ValueError(f"checksum mismatch: {target}")


def release_commit_from_panel(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8"))
    candidates = (
        payload.get("commit"),
        payload.get("release_commit"),
        payload.get("workflow", {}).get("release_commit"),
        payload.get("params", {}).get("release_commit"),
    )
    commits = [value for value in candidates if isinstance(value, str) and value]
    if len(set(commits)) != 1:
        raise ValueError(f"missing or contradictory release commit in {path}")
    return commits[0]


def validate_sample(run_root: Path, row: dict[str, str], release_commit: str) -> list[str]:
    sample_root = run_root / "samples" / row["modality"] / row["sample_id"]
    errors: list[str] = []
    required = (
        "SAMPLE_COMPLETE",
        "nextflow.exit",
        "caller_dispositions.tsv",
        "completion_sha256.txt",
        "result_files_sha256.txt",
    )
    for name in required:
        if not (sample_root / name).is_file():
            errors.append(f"missing {name}")
    if errors:
        return errors
    if (sample_root / "nextflow.exit").read_text(encoding="utf-8").strip() != "0":
        errors.append("Nextflow exit is not zero")
    try:
        verify_checksum_file(sample_root / "completion_sha256.txt")
        verify_checksum_file(sample_root / "result_files_sha256.txt")
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    with (sample_root / "caller_dispositions.tsv").open(newline="", encoding="utf-8") as handle:
        dispositions = list(csv.DictReader(handle, delimiter="\t"))
    if not dispositions:
        errors.append("empty caller disposition table")
    if any(item.get("disposition") == "missing_without_trace" for item in dispositions):
        errors.append("caller missing without trace")
    panel = sample_root / "results" / "pipeline_info" / "panel_provenance.json"
    if not panel.is_file():
        errors.append("missing panel provenance")
    else:
        try:
            observed_commit = release_commit_from_panel(panel)
            if observed_commit != release_commit:
                errors.append(
                    f"release commit mismatch: {observed_commit} != {release_commit}"
                )
        except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(str(exc))
    return errors


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {"batch_id", "sample_id", "modality"}
    if not rows or not required.issubset(rows[0]):
        raise SystemExit(f"invalid development manifest: {path}")
    keys = [(row["sample_id"], row["modality"]) for row in rows]
    if len(keys) != len(set(keys)):
        raise SystemExit("duplicate sample/modality keys in development manifest")
    return rows


def ledger_keys(path: Path) -> set[tuple[str, str]]:
    if not path.exists():
        return set()
    with path.open(newline="", encoding="utf-8") as handle:
        return {(row["sample_id"], row["modality"]) for row in csv.DictReader(handle, delimiter="\t")}


def append_ledger(path: Path, record: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with locked_ledger(path) as handle:
        handle.seek(0)
        existing = list(csv.DictReader(handle, delimiter="\t"))
        key = (record["sample_id"], record["modality"])
        if any((row["sample_id"], row["modality"]) == key for row in existing):
            raise RuntimeError(f"submission already recorded for {key[0]} {key[1]}")
        handle.seek(0, 2)
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, delimiter="\t", lineterminator="\n")
        if handle.tell() == 0:
            writer.writeheader()
        writer.writerow(record)
        handle.flush()


def batch_rows(rows: list[dict[str, str]], batch_id: str) -> list[dict[str, str]]:
    selected = [row for row in rows if row["batch_id"] == batch_id]
    if not selected:
        known = ", ".join(sorted({row["batch_id"] for row in rows}))
        raise SystemExit(f"unknown batch {batch_id}; known batches: {known}")
    if len(selected) > 5:
        raise SystemExit(f"batch {batch_id} exceeds the five-sample safety cap")
    return selected


def parse_lfs_quota(text: str) -> float | None:
    """Free GiB from ``lfs quota -q`` (KiB columns), or None when no limit is set.

    A missing or zero limit returns None so that a wrong quota scope fails closed
    instead of falling back to the free space of the whole shared filesystem.
    """
    tokens = text.split()
    start = next((i for i, token in enumerate(tokens) if token.startswith("/")), None)
    if start is None:
        return None
    values = [token.rstrip("*") for token in tokens[start + 1:start + 4]]
    if len(values) != 3 or not all(value.isdigit() for value in values):
        return None
    used, soft, hard = (int(value) for value in values)
    # The soft limit is the allocation; the hard limit is only the grace ceiling.
    limit = soft or hard
    if limit <= 0:
        return None
    return (limit - used) / 1024 ** 2


def parse_lfs_project_id(text: str) -> str | None:
    """Project ID from ``lfs project -d <dir>`` output such as ``602008084 P /scratch/...``."""
    fields = text.split()
    return fields[0] if fields and fields[0].isdigit() else None


def query_free_gib(path: Path = SCRATCH_PATH) -> float | None:
    """Smaller of the project quota headroom and filesystem free space; None if unknown.

    Roihu enforces scratch allocations as Lustre project quotas (verified
    2026-10-16: the group quota of project_2008084 carries no limit).
    """
    override = os.environ.get("CHAMPHLA_FREE_GIB")
    if override is not None:
        return float(override)
    try:
        project = subprocess.run(
            ["lfs", "project", "-d", str(path)], check=True, text=True, capture_output=True,
        )
        project_id = parse_lfs_project_id(project.stdout)
        if project_id is None:
            return None
        result = subprocess.run(
            ["lfs", "quota", "-q", "-p", project_id, str(path)],
            check=True, text=True, capture_output=True,
        )
        quota_free = parse_lfs_quota(result.stdout)
        disk_free = shutil.disk_usage(path).free / 1024 ** 3
    except (OSError, subprocess.CalledProcessError):
        return None
    if quota_free is None:
        return None
    return min(quota_free, disk_free)


def active_job_ids() -> set[str]:
    """Pending or running runner jobs of this user, by Slurm job ID."""
    user = os.environ.get("USER", "")
    result = subprocess.run(
        ["squeue", "-h", "-u", user, "-n", JOB_NAME, "-o", "%i"],
        check=True, text=True, capture_output=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def job_outcome(job_id: str) -> tuple[str, str]:
    """Slurm (State, ExitCode) of a finished allocation, or ("UNKNOWN", "")."""
    result = subprocess.run(
        ["sacct", "-n", "-X", "-P", "-j", job_id, "-o", "State,ExitCode"],
        check=False, text=True, capture_output=True,
    )
    for line in result.stdout.splitlines():
        if "|" in line:
            state, exit_code = line.split("|", 1)
            return state.split()[0], exit_code.strip()
    return "UNKNOWN", ""


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def append_row(path: Path, fields: tuple[str, ...], record: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with locked_ledger(path) as handle:
        handle.seek(0, 2)
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        if handle.tell() == 0:
            writer.writeheader()
        writer.writerow(record)
        handle.flush()


def attempts_by_key(
    ledger: list[dict[str, str]], retries: list[dict[str, str]]
) -> dict[tuple[str, str], list[tuple[int, str]]]:
    """(attempt, job_id) per sample/modality; the main ledger holds attempt 1."""
    attempts: dict[tuple[str, str], list[tuple[int, str]]] = {}
    for row in ledger:
        attempts.setdefault((row["sample_id"], row["modality"]), []).append((1, row["slurm_job_id"]))
    for row in retries:
        attempts.setdefault((row["sample_id"], row["modality"]), []).append(
            (int(row["attempt"]), row["slurm_job_id"])
        )
    return {key: sorted(value) for key, value in attempts.items()}


def classification_index(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], str]:
    return {(row["sample_id"], row["modality"], row["slurm_job_id"]): row["failure_class"] for row in rows}


def auto_failure_class(job_id: str) -> tuple[str | None, str]:
    """(class, note) for outcomes that need no judgement, else (None, note).

    A note of "unsettled" means Slurm accounting has not yet recorded the end of a
    job that already left the queue; the controller waits a pass instead of stopping.
    """
    state, exit_code = job_outcome(job_id)
    if state in UNSETTLED_STATES:
        return None, "unsettled"
    if exit_code.split(":", 1)[0] == str(STORAGE_GATE_EXIT):
        return "storage_deferred", "runner storage gate (exit 10): nothing was staged"
    if exit_code.split(":", 1)[0] == str(STORAGE_TAINT_EXIT):
        return "storage", "runner storage watcher (exit 11): project quota exhausted during the run"
    if state in {"NODE_FAIL", "BOOT_FAIL"}:
        return "scheduler", f"Slurm state {state}"
    return None, f"Slurm state {state}, exit {exit_code}"


def sample_state(
    run_root: Path,
    row: dict[str, str],
    release_commit: str,
    attempts: dict[tuple[str, str], list[tuple[int, str]]],
    classes: dict[tuple[str, str, str], str],
    active: set[str],
    max_attempts: int,
) -> tuple[str, str]:
    """(state, detail) for one roster entry; never consults truth."""
    key = (row["sample_id"], row["modality"])
    if not validate_sample(run_root, row, release_commit):
        return "complete", "all completion checks passed"
    history = attempts.get(key, [])
    if not history:
        return "never_submitted", ""
    attempt, job_id = history[-1]
    if job_id in active:
        return "active", f"job {job_id}"
    failure_class = classes.get((key[0], key[1], job_id))
    if failure_class is None:
        return "failed_unclassified", f"job {job_id} attempt {attempt}"
    # A storage-gate deferral staged nothing, so it does not use up an attempt.
    counted = sum(
        1 for _, job in history if classes.get((key[0], key[1], job)) != "storage_deferred"
    )
    if failure_class in RETRYABLE_CLASSES and (
        failure_class == "storage_deferred" or counted < max_attempts
    ):
        return "failed_retryable", f"job {job_id} {failure_class}"
    return "failed_terminal", f"job {job_id} {failure_class} attempt {attempt}"


def submit_runner(runner: Path, row: dict[str, str], release_commit: str,
                  prune_on_success: bool, reserve_gib: int) -> str:
    command = [
        "sbatch",
        "--parsable",
        f"--export=ALL,PRUNE_ON_SUCCESS={int(prune_on_success)},PRUNE_ON_FAILURE=1,"
        f"CHAMPHLA_RELEASE_COMMIT={release_commit},CHAMPHLA_RESERVE_GIB={reserve_gib}",
        str(runner),
        row["sample_id"],
        row["modality"],
    ]
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    job_id = result.stdout.strip().split(";", 1)[0]
    if not job_id.isdigit():
        raise RuntimeError(f"unexpected sbatch response: {result.stdout!r}")
    return job_id


def reserve_for(args: argparse.Namespace, modality: str) -> int:
    return {"wes": args.reserve_wes_gib, "rnaseq": args.reserve_rnaseq_gib}[modality]


def tree_gib(path: Path) -> float:
    """Allocated size of a directory tree in GiB, without following symlinks."""
    total = 0
    stack = [path]
    while stack:
        try:
            entries = list(os.scandir(stack.pop()))
        except OSError:
            continue
        for entry in entries:
            try:
                info = entry.stat(follow_symlinks=False)
            except OSError:
                continue
            if entry.is_dir(follow_symlinks=False):
                stack.append(Path(entry.path))
            elif not entry.is_symlink():
                total += getattr(info, "st_blocks", 0) * 512 or info.st_size
    return total / 1024 ** 3


def sample_usage_gib(run_root: Path, row: dict[str, str]) -> float:
    """Scratch already used by a running sample: its Nextflow work and staged input."""
    sample, modality = row["sample_id"], row["modality"]
    return (tree_gib(run_root / "work" / f"{modality}_{sample}")
            + tree_gib(run_root / "inputs" / modality / sample))


def outstanding_reserve_gib(args: argparse.Namespace, row: dict[str, str]) -> float:
    """What a running sample may still add: its reserve less what it already occupies.

    Free space already reflects that usage, so subtracting the full reserve again
    would count it twice and stall submission while a large job is at its peak.
    """
    return max(0.0, reserve_for(args, row["modality"]) - sample_usage_gib(args.run_root, row))


def command_control(args: argparse.Namespace) -> int:
    """One controller pass. Exit 0 progress, 3 needs classification, 4 storage unknown, 10 done."""
    rows = read_manifest(args.manifest)
    order = {modality: rank for rank, modality in enumerate(args.modality_order.split(","))}
    rows = sorted(rows, key=lambda row: order.get(row["modality"], len(order)))
    ledger_path = args.run_root / "submission_ledger.tsv"
    retry_path = args.run_root / "retry_ledger.tsv"
    class_path = args.run_root / "failure_classifications.tsv"
    attempts = attempts_by_key(read_rows(ledger_path), read_rows(retry_path))
    classes = classification_index(read_rows(class_path))
    active = active_job_ids()

    states: list[tuple[dict[str, str], str, str]] = []
    deferrals = 0
    for row in rows:
        state, detail = sample_state(args.run_root, row, args.release_commit, attempts,
                                     classes, active, args.max_attempts)
        if state == "failed_unclassified":
            job_id = attempts[(row["sample_id"], row["modality"])][-1][1]
            failure_class, note = auto_failure_class(job_id)
            if failure_class is not None:
                append_row(class_path, CLASSIFICATION_FIELDS, {
                    "classified_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                    "sample_id": row["sample_id"], "modality": row["modality"],
                    "slurm_job_id": job_id, "failure_class": failure_class,
                    "classified_by": "auto", "note": note,
                })
                classes[(row["sample_id"], row["modality"], job_id)] = failure_class
                deferrals += failure_class == "storage_deferred"
                state, detail = sample_state(args.run_root, row, args.release_commit, attempts,
                                             classes, active, args.max_attempts)
            elif note == "unsettled":
                state, detail = "settling", f"job {job_id} awaiting Slurm accounting"
            else:
                detail = f"{detail}; {note}"
        states.append((row, state, detail))

    status_path = args.run_root / "controller_status.tsv"
    status_path.parent.mkdir(parents=True, exist_ok=True)
    with status_path.open("w", newline="", encoding="utf-8") as handle:
        handle.write("sample_id\tmodality\tstate\tdetail\n")
        for row, state, detail in states:
            handle.write(f"{row['sample_id']}\t{row['modality']}\t{state}\t{detail}\n")
    counts: dict[str, int] = {}
    for _, state, _ in states:
        counts[state] = counts.get(state, 0) + 1
    print("SUMMARY\t" + "\t".join(f"{state}={count}" for state, count in sorted(counts.items())))

    unclassified = [(row, detail) for row, state, detail in states if state == "failed_unclassified"]
    if unclassified:
        for row, detail in unclassified:
            print(f"NEEDS_CLASSIFICATION\t{row['sample_id']}\t{row['modality']}\t{detail}")
        return 3
    if deferrals > MAX_DEFERRALS_PER_PASS:
        print(f"STORAGE_DEFERRALS\t{deferrals} jobs hit the runner storage gate since the last "
              "pass; check the headroom probe and reserves before restarting")
        return 4
    pending = [row for row, state, _ in states if state in {"never_submitted", "failed_retryable"}]
    active_rows = [row for row, state, _ in states if state == "active"]
    settling = [row for row, state, _ in states if state == "settling"]
    if not pending and not active_rows and not settling:
        print("ALL_DONE")
        return 10
    free = query_free_gib()
    if free is None:
        print("STORAGE_UNKNOWN\tquota headroom could not be read; submitting nothing")
        return 4
    outstanding = sum(outstanding_reserve_gib(args, row) for row in active_rows)
    budget = free - args.min_free_gib - outstanding
    capacity = args.max_running - len(active_rows)
    print(f"GATE\tfree_gib={free:.1f}\toutstanding_reserve_gib={outstanding:.1f}\t"
          f"budget_gib={budget:.1f}\tcapacity={capacity}")
    # An exclusive modality runs alone: its scratch peak is not predictable from the
    # input size (RNA HLA-HD on the whole BAM, 2026-10-16), so nothing shares its quota.
    exclusive = args.exclusive_modality
    busy = {row["modality"] for row in active_rows + settling}
    submitted = 0
    for row in pending:
        reserve = reserve_for(args, row["modality"])
        key = (row["sample_id"], row["modality"])
        if submitted >= capacity:
            print(f"DEFER_RUNNING\t{key[0]}\t{key[1]}")
            continue
        if exclusive and busy and (exclusive in busy or key[1] == exclusive):
            print(f"DEFER_EXCLUSIVE\t{key[0]}\t{key[1]}")
            continue
        if budget < reserve:
            print(f"DEFER_STORAGE\t{key[0]}\t{key[1]}\treserve_gib={reserve}")
            continue
        budget -= reserve
        submitted += 1
        busy.add(key[1])
        if not args.execute:
            print(f"PLAN_SUBMIT\t{key[0]}\t{key[1]}")
            continue
        history = attempts.get(key, [])
        job_id = submit_runner(args.runner, row, args.release_commit, True, reserve)
        now = dt.datetime.now(dt.timezone.utc).isoformat()
        if not history:
            append_ledger(ledger_path, {
                "submitted_utc": now, "batch_id": row["batch_id"],
                "sample_id": key[0], "modality": key[1], "slurm_job_id": job_id,
                "release_commit": args.release_commit, "prune_on_success": "1",
            })
        else:
            attempt, previous = history[-1]
            append_row(retry_path, RETRY_LEDGER_FIELDS, {
                "submitted_utc": now, "sample_id": key[0], "modality": key[1],
                "attempt": str(attempt + 1), "slurm_job_id": job_id,
                "retry_of_job_id": previous,
                "failure_class": classes[(key[0], key[1], previous)],
                "release_commit": args.release_commit, "prune_on_success": "1",
            })
        print(f"SUBMITTED\t{key[0]}\t{key[1]}\t{job_id}")
    return 0


def command_classify(args: argparse.Namespace) -> int:
    """Record the author's failure class for the latest failed attempt of each sample."""
    if args.from_tsv:
        requests = read_rows(args.from_tsv)
    elif not (args.sample_id and args.modality and args.failure_class):
        raise SystemExit("give <sample_id> <modality> --failure-class, or --from-tsv")
    else:
        requests = [{"sample_id": args.sample_id, "modality": args.modality,
                     "failure_class": args.failure_class, "note": args.note}]
    manifest = {(row["sample_id"], row["modality"]): row for row in read_manifest(args.manifest)}
    attempts = attempts_by_key(read_rows(args.run_root / "submission_ledger.tsv"),
                               read_rows(args.run_root / "retry_ledger.tsv"))
    class_path = args.run_root / "failure_classifications.tsv"
    classes = classification_index(read_rows(class_path))
    active = active_job_ids()
    for request in requests:
        key = (request["sample_id"], request["modality"])
        if request["failure_class"] not in FAILURE_CLASSES:
            raise SystemExit(f"unknown failure class {request['failure_class']!r}")
        if not request.get("note", "").strip():
            raise SystemExit(f"a note is required for {key[0]} {key[1]}")
        if key not in manifest:
            raise SystemExit(f"{key[0]} {key[1]} is not in the development manifest")
        if not validate_sample(args.run_root, manifest[key], args.release_commit):
            raise SystemExit(f"{key[0]} {key[1]} is complete; nothing to classify")
        if key not in attempts:
            raise SystemExit(f"{key[0]} {key[1]} was never submitted")
        job_id = attempts[key][-1][1]
        if job_id in active:
            raise SystemExit(f"{key[0]} {key[1]} job {job_id} is still active")
        if (key[0], key[1], job_id) in classes:
            raise SystemExit(f"{key[0]} {key[1]} job {job_id} is already classified")
        append_row(class_path, CLASSIFICATION_FIELDS, {
            "classified_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
            "sample_id": key[0], "modality": key[1], "slurm_job_id": job_id,
            "failure_class": request["failure_class"], "classified_by": "author",
            "note": request["note"].strip(),
        })
        classes[(key[0], key[1], job_id)] = request["failure_class"]
        print(f"CLASSIFIED\t{key[0]}\t{key[1]}\t{job_id}\t{request['failure_class']}")
    return 0


def command_free_gib(args: argparse.Namespace) -> int:
    free = query_free_gib()
    if free is None:
        print("STORAGE_UNKNOWN", file=sys.stderr)
        return 4
    print(int(free))
    return 0


def command_submit(args: argparse.Namespace) -> int:
    selected = batch_rows(read_manifest(args.manifest), args.batch_id)
    already = ledger_keys(args.ledger)
    actions: list[dict[str, str]] = []
    for row in selected:
        errors = validate_sample(args.run_root, row, args.release_commit)
        key = (row["sample_id"], row["modality"])
        if not errors:
            print(f"SKIP_COMPLETE\t{row['batch_id']}\t{row['sample_id']}\t{row['modality']}")
        elif key in already:
            raise SystemExit(
                f"refusing duplicate submission for {key[0]} {key[1]}; "
                "inspect its recorded Slurm job and artifacts first"
            )
        else:
            actions.append(row)
            print(
                f"PLAN_SUBMIT\t{row['batch_id']}\t{row['sample_id']}\t{row['modality']}\t"
                + "; ".join(errors)
            )
    deferred = actions[args.max_submit:]
    actions = actions[:args.max_submit]
    for row in deferred:
        print(
            f"DEFER_CAP\t{row['batch_id']}\t{row['sample_id']}\t{row['modality']}\t"
            f"--max-submit={args.max_submit}"
        )
    if getattr(args, "min_free_gib", None) is not None:
        free = query_free_gib()
        if free is None:
            print("STORAGE_UNKNOWN\tquota headroom could not be read; submitting nothing")
            return 4
        budget = free - args.min_free_gib
        fitting: list[dict[str, str]] = []
        for row in actions:
            reserve = reserve_for(args, row["modality"])
            if budget < reserve:
                print(
                    f"DEFER_STORAGE\t{row['batch_id']}\t{row['sample_id']}\t{row['modality']}\t"
                    f"free_gib={free:.1f}\treserve_gib={reserve}"
                )
                continue
            budget -= reserve
            fitting.append(row)
        actions = fitting
    if not args.execute:
        print(f"DRY_RUN\tplanned={len(actions)}")
        return 0
    for row in actions:
        command = [
            "sbatch",
            "--parsable",
            f"--export=ALL,PRUNE_ON_SUCCESS={int(args.prune_on_success)},"
            f"CHAMPHLA_RELEASE_COMMIT={args.release_commit}",
            str(args.runner),
            row["sample_id"],
            row["modality"],
        ]
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        job_id = result.stdout.strip().split(";", 1)[0]
        if not job_id.isdigit():
            raise RuntimeError(f"unexpected sbatch response: {result.stdout!r}")
        append_ledger(
            args.ledger,
            {
                "submitted_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
                "batch_id": row["batch_id"],
                "sample_id": row["sample_id"],
                "modality": row["modality"],
                "slurm_job_id": job_id,
                "release_commit": args.release_commit,
                "prune_on_success": str(int(args.prune_on_success)),
            },
        )
        print(f"SUBMITTED\t{row['batch_id']}\t{row['sample_id']}\t{row['modality']}\t{job_id}")
    return 0


def command_validate(args: argparse.Namespace) -> int:
    rows = read_manifest(args.manifest)
    if args.batch_id:
        rows = batch_rows(rows, args.batch_id)
    failed = 0
    print("batch_id\tsample_id\tmodality\tartifact_state\tdetail")
    for row in rows:
        errors = validate_sample(args.run_root, row, args.release_commit)
        state = "complete_valid" if not errors else "incomplete_or_invalid"
        failed += bool(errors)
        print(
            f"{row['batch_id']}\t{row['sample_id']}\t{row['modality']}\t{state}\t"
            f"{'; '.join(errors) if errors else 'all completion checks passed'}"
        )
    print(f"SUMMARY\tchecked={len(rows)}\tcomplete_valid={len(rows)-failed}\tincomplete_or_invalid={failed}")
    return 1 if failed else 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    result.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    result.add_argument("--release-commit", default=DEFAULT_RELEASE_COMMIT)
    subparsers = result.add_subparsers(dest="command", required=True)

    submit = subparsers.add_parser("submit")
    submit.add_argument("batch_id")
    submit.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    submit.add_argument("--ledger", type=Path, default=DEFAULT_RUN_ROOT / "submission_ledger.tsv")
    submit.add_argument(
        "--max-submit", type=int, choices=range(1, 6), default=5,
        help="submit at most this many eligible rows; remaining rows are explicitly deferred",
    )
    submit.add_argument("--execute", action="store_true")
    submit.add_argument("--prune-on-success", action="store_true")
    add_storage_arguments(submit)
    submit.set_defaults(func=command_submit)

    validate = subparsers.add_parser("validate")
    validate.add_argument("batch_id", nargs="?")
    validate.set_defaults(func=command_validate)

    control = subparsers.add_parser(
        "control", help="one stateless, storage-gated controller pass over the whole roster"
    )
    control.add_argument("--runner", type=Path, default=DEFAULT_RUNNER)
    control.add_argument("--max-running", type=int, choices=range(1, 6), default=2)
    control.add_argument("--max-attempts", type=int, choices=range(1, 6), default=DEFAULT_MAX_ATTEMPTS)
    control.add_argument("--modality-order", default="rnaseq,wes")
    control.add_argument("--exclusive-modality", choices=("wes", "rnaseq"),
                         help="run this modality only while no other job is active, and alone")
    control.add_argument("--execute", action="store_true")
    add_storage_arguments(control)
    control.set_defaults(func=command_control)

    classify = subparsers.add_parser(
        "classify", help="record the failure class of a sample's latest failed attempt"
    )
    classify.add_argument("sample_id", nargs="?")
    classify.add_argument("modality", nargs="?", choices=("wes", "rnaseq"))
    classify.add_argument("--failure-class", choices=FAILURE_CLASSES)
    classify.add_argument("--note", default="")
    classify.add_argument("--from-tsv", type=Path,
                          help="TSV with sample_id, modality, failure_class and note columns")
    classify.set_defaults(func=command_classify)

    free_gib = subparsers.add_parser("free-gib", help="print project scratch headroom in GiB")
    free_gib.set_defaults(func=command_free_gib)
    return result


def add_storage_arguments(command: argparse.ArgumentParser) -> None:
    command.add_argument("--min-free-gib", type=int, default=DEFAULT_MIN_FREE_GIB,
                         help="headroom that must remain after every planned sample's reserve")
    command.add_argument("--reserve-wes-gib", type=int, default=DEFAULT_RESERVE_GIB["wes"])
    command.add_argument("--reserve-rnaseq-gib", type=int, default=DEFAULT_RESERVE_GIB["rnaseq"])


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
