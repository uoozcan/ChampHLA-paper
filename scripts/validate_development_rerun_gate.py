#!/usr/bin/env python3
"""Create the signed-roster operational gate record required before collection."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


EXPECTED_EXECUTION_MANAGER_SHA256 = (
    "cd5e6ac676a1b1937e051de3f22d6162cfaf7ddb457cfccb4719b0e8d0aec7e9"
)
EXPECTED_ROSTER_SHA256 = (
    "506405a006a2cabc80f8584fa21368d868d56a6164ccd60e017d36173bcbfd85"
)
EXPECTED = {"checked": 236, "complete_valid": 236, "incomplete_or_invalid": 0}
JOB_CLASSES = ("champhla_ctl", "champhla_dev", "champhla_prefetch")
SUMMARY = re.compile(
    r"^SUMMARY\s+checked=(\d+)\s+complete_valid=(\d+)\s+incomplete_or_invalid=(\d+)\s*$",
    re.M,
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate(
    validator_report: Path, operational_status: Path,
    execution_manager: Path, roster: Path,
) -> dict:
    text = validator_report.read_text(encoding="utf-8")
    matches = SUMMARY.findall(text)
    if len(matches) != 1:
        raise ValueError("validator report must contain exactly one SUMMARY line")
    counts = dict(zip(EXPECTED, map(int, matches[0])))
    if counts != EXPECTED:
        raise ValueError(f"full-roster validator gate failed: {counts}")
    status = json.loads(operational_status.read_text(encoding="utf-8"))
    if status.get("controller_finished_normally") is not True:
        raise ValueError("controller has not finished normally")
    jobs = status.get("running_jobs")
    if not isinstance(jobs, dict):
        raise ValueError("operational status lacks running_jobs")
    observed_jobs = {name: int(jobs.get(name, -1)) for name in JOB_CLASSES}
    if observed_jobs != {name: 0 for name in JOB_CLASSES}:
        raise ValueError(f"rerun jobs remain active: {observed_jobs}")
    manager_hash, roster_hash = sha256(execution_manager), sha256(roster)
    if manager_hash != EXPECTED_EXECUTION_MANAGER_SHA256:
        raise ValueError("execution-manager hash differs from the canonical gate")
    if roster_hash != EXPECTED_ROSTER_SHA256:
        raise ValueError("rerun-roster hash differs from the canonical gate")
    return {
        "schema_version": "champhla-development-rerun-gate-1",
        "status": "PASS",
        "truth_inspected": False,
        "performance_calculated": False,
        "validator_counts": counts,
        "running_jobs": observed_jobs,
        "controller_finished_normally": True,
        "execution_manager_sha256": manager_hash,
        "roster_sha256": roster_hash,
        "validator_report_sha256": sha256(validator_report),
        "operational_status_sha256": sha256(operational_status),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validator-report", type=Path, required=True)
    parser.add_argument("--operational-status", type=Path, required=True)
    parser.add_argument("--execution-manager", type=Path, required=True)
    parser.add_argument("--roster", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = validate(
            args.validator_report, args.operational_status,
            args.execution_manager, args.roster,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(f"rerun gate refused: {exc}") from exc
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes((json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
