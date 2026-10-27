"""Operational full-roster gate tests."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_development_rerun_gate",
    ROOT / "scripts/validate_development_rerun_gate.py",
)
assert SPEC and SPEC.loader
GATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GATE)


def _inputs(tmp_path: Path) -> tuple[Path, Path]:
    validator = tmp_path / "validator.txt"
    validator.write_text(
        "SUMMARY\tchecked=236\tcomplete_valid=236\tincomplete_or_invalid=0\n",
        encoding="utf-8",
    )
    status = tmp_path / "status.json"
    status.write_text(json.dumps({
        "controller_finished_normally": True,
        "running_jobs": {
            "champhla_ctl": 0, "champhla_dev": 0, "champhla_prefetch": 0,
        },
    }), encoding="utf-8")
    return validator, status


def test_full_quiescent_gate_passes(tmp_path: Path):
    validator, status = _inputs(tmp_path)
    result = GATE.validate(
        validator, status, ROOT / "provenance/development_rerun_v350/operational_gate/manage_development_batches.deployed.py",
        ROOT / "cohorts/development_rerun_manifest.tsv",
    )
    assert result["status"] == "PASS"
    assert result["truth_inspected"] is False


@pytest.mark.parametrize("field,value", [
    ("complete_valid", 235), ("incomplete_or_invalid", 1), ("checked", 235),
])
def test_incomplete_validator_counts_are_refused(tmp_path: Path, field: str, value: int):
    validator, status = _inputs(tmp_path)
    counts = {"checked": 236, "complete_valid": 236, "incomplete_or_invalid": 0}
    counts[field] = value
    validator.write_text(
        "SUMMARY\t" + "\t".join(f"{key}={counts[key]}" for key in counts) + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="full-roster validator gate failed"):
        GATE.validate(
            validator, status, ROOT / "provenance/development_rerun_v350/operational_gate/manage_development_batches.deployed.py",
            ROOT / "cohorts/development_rerun_manifest.tsv",
        )


def test_running_job_or_unfinished_controller_is_refused(tmp_path: Path):
    validator, status = _inputs(tmp_path)
    status.write_text(json.dumps({
        "controller_finished_normally": False,
        "running_jobs": {
            "champhla_ctl": 1, "champhla_dev": 0, "champhla_prefetch": 0,
        },
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="controller has not finished normally"):
        GATE.validate(
            validator, status, ROOT / "provenance/development_rerun_v350/operational_gate/manage_development_batches.deployed.py",
            ROOT / "cohorts/development_rerun_manifest.tsv",
        )
