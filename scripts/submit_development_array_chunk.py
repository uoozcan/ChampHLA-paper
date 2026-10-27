#!/usr/bin/env python3
"""Submit one capped development array and chain the next manifest chunk.

Each array covers a stable range of the frozen manifest, runs at most five
samples concurrently, and skips already validated completions. The next chunk
is submitted only after every task in the current array reaches a terminal
state, keeping the CSC submit-job count below the account limit.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import importlib.util
from pathlib import Path
import subprocess
import sys


ROOT = Path("/scratch/project_2008084/champhla_publication_remediation")
MANIFEST = ROOT / "paper/cohorts/development_rerun_manifest.tsv"
MANAGER = ROOT / "paper/scripts/manage_development_batches.py"
ARRAY_RUNNER = ROOT / "paper/scripts/roihu_run_development_array.sbatch"
THIS_SCRIPT = ROOT / "paper/scripts/submit_development_array_chunk.py"
RUN_ROOT = ROOT / "development"
LEDGER = RUN_ROOT / "submission_ledger.tsv"
CHAIN_LEDGER = RUN_ROOT / "array_chain.tsv"
LOG_DIR = RUN_ROOT / "logs"
RELEASE_COMMIT = "66d949da90861da6cf60cf1d4bee2f094f2518bd"


def load_manager():
    spec = importlib.util.spec_from_file_location("development_manager", MANAGER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def sbatch(*args: str) -> str:
    result = subprocess.run(
        ["sbatch", "--parsable", *args], check=True, text=True, capture_output=True
    )
    job_id = result.stdout.strip().split(";", 1)[0]
    if not job_id.isdigit():
        raise RuntimeError(f"unexpected sbatch response: {result.stdout!r}")
    return job_id


def append_chain_record(record: str) -> None:
    import fcntl

    CHAIN_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with CHAIN_LEDGER.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0, 2)
        if handle.tell() == 0:
            handle.write(
                "submitted_utc\tarray_job_id\ttask_start\ttask_end\t"
                "concurrency\tnext_controller_job_id\n"
            )
        handle.write(record + "\n")
        handle.flush()


def rollback_ledger(manager, array_job: str) -> None:
    """Remove only records written for an unreleased array submission."""
    with manager.locked_ledger(LEDGER) as handle:
        handle.seek(0)
        rows = list(csv.DictReader(handle, delimiter="\t"))
        kept = [
            row
            for row in rows
            if not row.get("slurm_job_id", "").startswith(f"{array_job}_")
        ]
        handle.seek(0)
        handle.truncate()
        writer = csv.DictWriter(
            handle,
            fieldnames=manager.LEDGER_FIELDS,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(kept)
        handle.flush()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--chunk-size", type=int, default=100)
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()
    if args.start < 0 or args.chunk_size < 1 or not 1 <= args.concurrency <= 5:
        raise SystemExit("invalid start, chunk size, or concurrency")

    manager = load_manager()
    rows = manager.read_manifest(MANIFEST)
    if args.start >= len(rows):
        print(f"CHAIN_COMPLETE\tmanifest_rows={len(rows)}")
        return 0
    end = min(args.start + args.chunk_size, len(rows)) - 1
    selected = list(enumerate(rows[args.start : end + 1], start=args.start))
    existing = manager.ledger_keys(LEDGER)
    planned: list[tuple[int, dict[str, str]]] = []
    for index, row in selected:
        errors = manager.validate_sample(RUN_ROOT, row, RELEASE_COMMIT)
        key = (row["sample_id"], row["modality"])
        if not errors:
            continue
        if key in existing:
            raise SystemExit(
                f"refusing duplicate submission for incomplete recorded run {key}"
            )
        planned.append((index, row))

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    array_job = sbatch(
        "--hold",
        f"--array={args.start}-{end}%{args.concurrency}",
        "--export=ALL,PRUNE_ON_SUCCESS=1,"
        f"CHAMPHLA_RELEASE_COMMIT={RELEASE_COMMIT}",
        str(ARRAY_RUNNER),
    )
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    next_job = ""
    try:
        for index, row in planned:
            manager.append_ledger(
                LEDGER,
                {
                    "submitted_utc": now,
                    "batch_id": row["batch_id"],
                    "sample_id": row["sample_id"],
                    "modality": row["modality"],
                    "slurm_job_id": f"{array_job}_{index}",
                    "release_commit": RELEASE_COMMIT,
                    "prune_on_success": "1",
                },
            )

        next_start = end + 1
        if next_start < len(rows):
            next_job = sbatch(
                f"--dependency=afterany:{array_job}",
                "--job-name=champhla_dev_continue",
                "--account=project_2008084",
                "--partition=small",
                "--time=00:10:00",
                "--cpus-per-task=1",
                "--mem=1G",
                f"--output={LOG_DIR}/champhla_continue_%j.out",
                f"--error={LOG_DIR}/champhla_continue_%j.err",
                str(THIS_SCRIPT),
                "--start",
                str(next_start),
                "--chunk-size",
                str(args.chunk_size),
                "--concurrency",
                str(args.concurrency),
            )
        append_chain_record(
            f"{now}\t{array_job}\t{args.start}\t{end}\t"
            f"{args.concurrency}\t{next_job}"
        )
        subprocess.run(["scontrol", "release", array_job], check=True)
    except Exception:
        if next_job:
            subprocess.run(["scancel", next_job], check=False)
        subprocess.run(["scancel", array_job], check=False)
        rollback_ledger(manager, array_job)
        raise

    print(
        f"SUBMITTED_CHUNK\tarray_job={array_job}\ttasks={args.start}-{end}\t"
        f"compute_required={len(planned)}\tconcurrency={args.concurrency}\t"
        f"next_controller={next_job or 'none'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
