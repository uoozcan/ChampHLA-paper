"""Cohort rows withheld from the published provenance (decisions/20261106_public_snapshot_scope.json, S1-S2)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REGISTRY = (b"result_id\tcohort\taccuracy\n"
            b"DEV_A\t1000G-development\t0.9\n"
            b"FIMM_X\tFIMM_AML_MDS\t0.5\n"
            b"DEV_B\t1000G-development\t0.8\n"
            b"VENEX_Y\tVENEX_WES\t0.4\n")
DELTA = (b"result_id\tstatus\told_accuracy\n"
         b"DEV_A\tchanged\t0.9\n"
         b"DEV_C\tadded\t\n"
         b"FIMM_X\tremoved\t0.5\n"
         b"VENEX_Y\tremoved\t0.4\n")


def synthetic(tmp_path: Path, module) -> Path:
    for directory in module.DIRECTORIES:
        (tmp_path / directory).mkdir(parents=True)
        (tmp_path / directory / module.REGISTRY).write_bytes(REGISTRY)
        (tmp_path / directory / module.DELTA).write_bytes(DELTA)
    return tmp_path


def test_withhold_drops_only_cohort_rows_and_keeps_the_originals(tmp_path):
    module = load("withhold_cohort_rows")
    root = synthetic(tmp_path, module)
    manifest = module.withhold(root)
    directory = module.DIRECTORIES[0]
    assert (root / directory / module.REGISTRY).read_bytes() == (
        b"result_id\tcohort\taccuracy\nDEV_A\t1000G-development\t0.9\n"
        b"DEV_B\t1000G-development\t0.8\n")
    assert (root / directory / module.DELTA).read_bytes() == (
        b"result_id\tstatus\told_accuracy\nDEV_A\tchanged\t0.9\nDEV_C\tadded\t\n")
    original = root / module.DESTINATION / directory / module.REGISTRY
    assert original.read_bytes() == REGISTRY
    entry = next(e for e in manifest["files"] if e["path"] == f"{directory}/{module.REGISTRY}")
    assert (entry["rows_before"], entry["rows_after"]) == (4, 2)
    assert entry["sha256_before"] == hashlib.sha256(REGISTRY).hexdigest()
    assert len(manifest["files"]) == 4


def test_withhold_runs_once_and_refuses_crlf(tmp_path):
    module = load("withhold_cohort_rows")
    root = synthetic(tmp_path, module)
    module.withhold(root)
    with pytest.raises(SystemExit, match="runs once"):
        module.withhold(root)
    with pytest.raises(SystemExit, match="LF"):
        module.split(b"a\tb\r\n1\t2\r\n")


def test_published_provenance_holds_no_cohort_rows_and_matches_its_manifest():
    module = load("withhold_cohort_rows")
    manifest = json.loads((ROOT / module.MANIFEST).read_text(encoding="utf-8"))
    labels = re.compile("|".join(re.escape(c) for c in module.WITHHELD_COHORTS))
    for entry in manifest["files"]:
        data = (ROOT / entry["path"]).read_bytes()
        if entry["path"] not in module.REGENERATED:
            assert hashlib.sha256(data).hexdigest() == entry["sha256_after"]
            assert data.count(b"\n") - 1 == entry["rows_after"]
        assert not labels.search(data.decode("utf-8")), entry["path"]
        withheld = ROOT / entry["withheld_copy"]
        if withheld.is_file():  # absent from the public snapshot by design
            assert hashlib.sha256(withheld.read_bytes()).hexdigest() == entry["sha256_before"]


def test_snapshot_holds_back_the_withheld_copies_and_internal_records():
    script = (ROOT / "scripts" / "publish_snapshot.sh").read_text(encoding="utf-8")
    hold_back = script[script.index("HOLD_BACK=("):script.index("\n)\n")]
    for path in ("provenance/cohort_rows_withheld_20261106", "AUTHOR_FIELDS_TO_COMPLETE.md",
                 "reports/author_decisions_20261106.md", "reports/coauthor_update_20261106.md",
                 "reports/ChampHLA_Scientific_Reports_Cover_Letter.md", "manuscripts/historical",
                 "manuscripts/source_original"):
        assert path in hold_back, path
    assert not re.search(r"^\s*'?decisions/?'?\s*$", hold_back, re.MULTILINE)
