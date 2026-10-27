import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/manage_development_batches.py"
SPEC = importlib.util.spec_from_file_location("manage_development_batches", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _valid_sample(tmp_path: Path, commit: str = MODULE.DEFAULT_RELEASE_COMMIT):
    row = {"batch_id": "wes-001", "sample_id": "HG00096", "modality": "wes"}
    root = tmp_path / "samples/wes/HG00096"
    panel_dir = root / "results/pipeline_info"
    panel_dir.mkdir(parents=True)
    (root / "nextflow.exit").write_text("0\n", encoding="utf-8")
    (root / "caller_dispositions.tsv").write_text(
        "caller\toutput_file_count\ttrace_statuses\tdisposition\n"
        "t1k\t1\tCOMPLETED:exit=0\toutputs_present\n",
        encoding="utf-8",
    )
    (panel_dir / "panel_provenance.json").write_text(
        json.dumps({"pipeline": "PanelHLA", "version": "3.5.0", "commit": commit}),
        encoding="utf-8",
    )
    result = root / "results/call.tsv"
    result.write_text("call\n", encoding="utf-8")
    (root / "result_files_sha256.txt").write_text(
        f"{_digest(result)}  {result}\n{_digest(panel_dir / 'panel_provenance.json')}  "
        f"{panel_dir / 'panel_provenance.json'}\n",
        encoding="utf-8",
    )
    (root / "completion_sha256.txt").write_text(
        f"{_digest(root / 'caller_dispositions.tsv')}  {root / 'caller_dispositions.tsv'}\n"
        f"{_digest(root / 'result_files_sha256.txt')}  {root / 'result_files_sha256.txt'}\n",
        encoding="utf-8",
    )
    (root / "SAMPLE_COMPLETE").touch()
    return row


def test_completed_sample_requires_checksums_and_exact_release(tmp_path):
    row = _valid_sample(tmp_path)
    assert MODULE.validate_sample(tmp_path, row, MODULE.DEFAULT_RELEASE_COMMIT) == []

    result = tmp_path / "samples/wes/HG00096/results/call.tsv"
    result.write_text("changed\n", encoding="utf-8")
    errors = MODULE.validate_sample(tmp_path, row, MODULE.DEFAULT_RELEASE_COMMIT)
    assert any("checksum mismatch" in error for error in errors)


def test_wrong_release_and_unaccounted_caller_are_rejected(tmp_path):
    row = _valid_sample(tmp_path, commit="0" * 40)
    status = tmp_path / "samples/wes/HG00096/caller_dispositions.tsv"
    status.write_text(
        "caller\toutput_file_count\ttrace_statuses\tdisposition\n"
        "t1k\t0\tnot_observed\tmissing_without_trace\n",
        encoding="utf-8",
    )
    errors = MODULE.validate_sample(tmp_path, row, MODULE.DEFAULT_RELEASE_COMMIT)
    assert any("release commit mismatch" in error for error in errors)
    assert "caller missing without trace" in errors


def test_ledger_is_append_only_per_sample_modality(tmp_path):
    ledger = tmp_path / "submission_ledger.tsv"
    record = {
        "submitted_utc": "2026-10-13T00:00:00+00:00",
        "batch_id": "wes-001",
        "sample_id": "HG00097",
        "modality": "wes",
        "slurm_job_id": "123",
        "release_commit": MODULE.DEFAULT_RELEASE_COMMIT,
        "prune_on_success": "1",
    }
    MODULE.append_ledger(ledger, record)
    with ledger.open(newline="", encoding="utf-8") as handle:
        assert list(csv.DictReader(handle, delimiter="\t")) == [record]
    try:
        MODULE.append_ledger(ledger, record)
    except RuntimeError as exc:
        assert "already recorded" in str(exc)
    else:
        raise AssertionError("duplicate ledger key was accepted")


def test_manifest_batches_are_small_and_exact():
    rows = MODULE.read_manifest(ROOT / "cohorts/development_rerun_manifest.tsv")
    selected = MODULE.batch_rows(rows, "wes-001")
    assert len(selected) == 5
    assert {row["batch_id"] for row in selected} == {"wes-001"}


def test_max_submit_defers_instead_of_overfilling_storage(tmp_path, capsys):
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text(
        "batch_id\tsample_id\tmodality\n"
        "rnaseq-001\tHG00097\trnaseq\n"
        "rnaseq-001\tHG00099\trnaseq\n"
        "rnaseq-001\tHG00100\trnaseq\n",
        encoding="utf-8",
    )
    args = SimpleNamespace(
        manifest=manifest,
        batch_id="rnaseq-001",
        run_root=tmp_path / "runs",
        release_commit=MODULE.DEFAULT_RELEASE_COMMIT,
        ledger=tmp_path / "ledger.tsv",
        max_submit=2,
        execute=False,
        prune_on_success=True,
        runner=tmp_path / "runner.sbatch",
    )
    assert MODULE.command_submit(args) == 0
    output = capsys.readouterr().out
    assert output.count("PLAN_SUBMIT") == 3
    assert output.count("DEFER_CAP") == 1
    assert "DRY_RUN\tplanned=2" in output
