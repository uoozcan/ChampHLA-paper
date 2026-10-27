import csv
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/manage_development_batches.py"
SPEC = importlib.util.spec_from_file_location("manage_development_batches_controller", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
RUNNER = ROOT / "scripts/roihu_run_development_sample.sbatch"
CONTROLLER = ROOT / "scripts/roihu_development_controller.sbatch"


class FakeCluster:
    """Stand-in for Slurm, the quota probe and the artifact validator."""

    def __init__(self, monkeypatch, free_gib=500.0, complete=(), active=(), outcomes=None):
        self.free_gib = free_gib
        self.complete = set(complete)
        self.active = set(active)
        self.outcomes = outcomes or {}
        self.submitted = []
        monkeypatch.setattr(MODULE, "query_free_gib", lambda *a, **k: self.free_gib)
        monkeypatch.setattr(MODULE, "active_job_ids", lambda *_: set(self.active))
        monkeypatch.setattr(MODULE, "job_outcome", lambda job: self.outcomes.get(job, ("FAILED", "1:0")))
        monkeypatch.setattr(
            MODULE, "validate_sample",
            lambda run_root, row, commit: [] if (row["sample_id"], row["modality"]) in self.complete
            else ["missing SAMPLE_COMPLETE"],
        )
        monkeypatch.setattr(MODULE, "submit_runner", self._submit)

    def _submit(self, runner, row, commit, prune, reserve, args=None):
        job_id = str(9000 + len(self.submitted))
        self.submitted.append((row["sample_id"], row["modality"], reserve))
        self.active.add(job_id)
        return job_id


def _manifest(tmp_path, rows):
    path = tmp_path / "manifest.tsv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        handle.write("batch_id\tsample_id\tmodality\n")
        for batch, sample, modality in rows:
            handle.write(f"{batch}\t{sample}\t{modality}\n")
    return path


def _args(tmp_path, manifest, **overrides):
    values = dict(
        manifest=manifest, run_root=tmp_path / "runs", release_commit=MODULE.DEFAULT_RELEASE_COMMIT,
        runner=tmp_path / "runner.sbatch", max_running=2, max_attempts=3,
        modality_order="rnaseq,wes", execute=True, min_free_gib=50,
        reserve_wes_gib=60, reserve_rnaseq_gib=25, exclusive_modality=None,
        job_name=MODULE.JOB_NAME, amendment=None,
    )
    values.update(overrides)
    return SimpleNamespace(**values)


def _ledger(tmp_path, rows):
    path = tmp_path / "runs/submission_ledger.tsv"
    for sample, modality, job in rows:
        MODULE.append_ledger(path, {
            "submitted_utc": "2026-10-14T00:00:00+00:00", "batch_id": "b",
            "sample_id": sample, "modality": modality, "slurm_job_id": job,
            "release_commit": MODULE.DEFAULT_RELEASE_COMMIT, "prune_on_success": "1",
        })


def _rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


@pytest.mark.parametrize("text, expected", [
    ("/scratch 157286400 0 262144000 - 100 0 0 -\n", 100.0),
    ("/scratch 157286400* 0 262144000 - 100 0 0 -\n", 100.0),
    ("/scratch\n 157286400 262144000 0 - 100 0 0 -\n", 100.0),
    # Roihu project quota of project_2008084 on 2026-10-16: the soft limit governs.
    ("        /scratch 146744024  262144000 263192576       -  191551   500000  501000       -\n",
     (262144000 - 146744024) / 1024 ** 2),
    # Roihu group quota of the same project carries no limit: fail closed.
    ("        /scratch 131782100        0       0       -  157309        0       0       -\n", None),
    ("no quota information\n", None),
])
def test_lfs_quota_parse_fails_closed_without_a_limit(text, expected):
    assert MODULE.parse_lfs_quota(text) == expected


def test_lfs_project_id_parse():
    assert MODULE.parse_lfs_project_id("602008084 P /scratch/project_2008084\n") == "602008084"
    assert MODULE.parse_lfs_project_id("lfs: cannot get project\n") is None


def test_low_headroom_defers_every_submission(tmp_path, monkeypatch, capsys):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq"), ("w", "HG2", "wes")])
    cluster = FakeCluster(monkeypatch, free_gib=60.0)
    assert MODULE.command_control(_args(tmp_path, manifest)) == 0
    output = capsys.readouterr().out
    assert cluster.submitted == []
    assert output.count("DEFER_STORAGE") == 2


def test_unknown_headroom_submits_nothing(tmp_path, monkeypatch, capsys):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq")])
    cluster = FakeCluster(monkeypatch, free_gib=None)
    assert MODULE.command_control(_args(tmp_path, manifest)) == 4
    assert cluster.submitted == []
    assert "STORAGE_UNKNOWN" in capsys.readouterr().out


def test_budget_counts_active_reserves_and_running_cap(tmp_path, monkeypatch, capsys):
    manifest = _manifest(tmp_path, [
        ("r", "HG1", "rnaseq"), ("r", "HG2", "rnaseq"), ("r", "HG3", "rnaseq"), ("w", "HG4", "wes"),
    ])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    cluster = FakeCluster(monkeypatch, free_gib=140.0, active={"100"})
    assert MODULE.command_control(_args(tmp_path, manifest)) == 0
    output = capsys.readouterr().out
    # 140 free - 50 headroom - 25 for the active RNA job leaves room for two RNA reserves,
    # but the running cap of two allows only one more job.
    assert cluster.submitted == [("HG2", "rnaseq", 25)]
    assert "DEFER_RUNNING\tHG3\trnaseq" in output


def test_running_job_usage_is_not_counted_twice(tmp_path, monkeypatch, capsys):
    # Measured 2026-10-16: an RNA job at its HLA-HD peak already occupies ~40 GiB of its
    # 70 GiB reserve, and free space already reflects that. Only the remaining 30 GiB may
    # be held back, so a 20 GiB WES job still fits.
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq"), ("w", "HG2", "wes")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    cluster = FakeCluster(monkeypatch, free_gib=73.0, active={"100"})
    monkeypatch.setattr(MODULE, "sample_usage_gib", lambda run_root, row: 40.0)
    args = _args(tmp_path, manifest, min_free_gib=15, reserve_wes_gib=20, reserve_rnaseq_gib=70)
    assert MODULE.command_control(args) == 0
    assert cluster.submitted == [("HG2", "wes", 20)]
    assert "outstanding_reserve_gib=30.0" in capsys.readouterr().out


def test_usage_above_the_reserve_holds_back_nothing_more(tmp_path, monkeypatch):
    monkeypatch.setattr(MODULE, "sample_usage_gib", lambda run_root, row: 90.0)
    args = SimpleNamespace(run_root=tmp_path, reserve_wes_gib=20, reserve_rnaseq_gib=70)
    assert MODULE.outstanding_reserve_gib(args, {"sample_id": "HG1", "modality": "rnaseq"}) == 0.0


def test_sample_usage_reads_work_and_input_trees(tmp_path):
    work = tmp_path / "work/rnaseq_HG1/ab/cd"
    work.mkdir(parents=True)
    (work / "big.sam").write_bytes(b"x" * 4096)
    inputs = tmp_path / "inputs/rnaseq/HG1"
    inputs.mkdir(parents=True)
    (inputs / "HG1.bam").write_bytes(b"x" * 4096)
    (tmp_path / "work/wes_HG1").mkdir(parents=True)
    (tmp_path / "work/wes_HG1/other.bam").write_bytes(b"x" * 1024 * 1024)
    usage = MODULE.sample_usage_gib(tmp_path, {"sample_id": "HG1", "modality": "rnaseq"})
    assert 8192 / 1024 ** 3 <= usage < 1024 * 1024 / 1024 ** 3


def test_unclassified_failure_stops_the_controller(tmp_path, monkeypatch, capsys):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq"), ("r", "HG2", "rnaseq")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    cluster = FakeCluster(monkeypatch, outcomes={"100": ("FAILED", "1:0")})
    assert MODULE.command_control(_args(tmp_path, manifest)) == 3
    assert cluster.submitted == []
    assert "NEEDS_CLASSIFICATION\tHG1\trnaseq" in capsys.readouterr().out


def test_storage_gate_exit_is_auto_classified_and_retried_once(tmp_path, monkeypatch):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    cluster = FakeCluster(monkeypatch, outcomes={"100": ("FAILED", f"{MODULE.STORAGE_GATE_EXIT}:0")})
    assert MODULE.command_control(_args(tmp_path, manifest)) == 0
    assert cluster.submitted == [("HG1", "rnaseq", 25)]
    classes = _rows(tmp_path / "runs/failure_classifications.tsv")
    assert [(row["failure_class"], row["classified_by"]) for row in classes] == [
        ("storage_deferred", "auto")
    ]
    retry = _rows(tmp_path / "runs/retry_ledger.tsv")
    assert [(row["attempt"], row["retry_of_job_id"], row["failure_class"]) for row in retry] == [
        ("2", "100", "storage_deferred")
    ]


def test_storage_taint_exit_is_auto_classified_as_an_attempt_using_storage_failure(tmp_path, monkeypatch):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    taint = ("FAILED", f"{MODULE.STORAGE_TAINT_EXIT}:0")
    cluster = FakeCluster(monkeypatch, outcomes={"100": taint})
    assert MODULE.command_control(_args(tmp_path, manifest, max_attempts=2)) == 0
    assert cluster.submitted == [("HG1", "rnaseq", 25)]
    classes = _rows(tmp_path / "runs/failure_classifications.tsv")
    assert [(row["failure_class"], row["classified_by"]) for row in classes] == [("storage", "auto")]
    # unlike a gate deferral, a tainted run used up an attempt
    cluster.active.discard("9000")
    cluster.outcomes["9000"] = taint
    assert MODULE.command_control(_args(tmp_path, manifest, max_attempts=2)) == 10
    assert len(cluster.submitted) == 1


def test_exclusive_modality_waits_for_an_idle_cluster_and_then_runs_alone(tmp_path, monkeypatch, capsys):
    manifest = _manifest(tmp_path, [
        ("w", "HG1", "wes"), ("w", "HG2", "wes"), ("r", "HG3", "rnaseq"), ("r", "HG4", "rnaseq"),
    ])
    _ledger(tmp_path, [("HG1", "wes", "100")])
    cluster = FakeCluster(monkeypatch, free_gib=500.0, active={"100"})
    args = _args(tmp_path, manifest, max_running=3, modality_order="wes,rnaseq",
                 exclusive_modality="rnaseq", reserve_rnaseq_gib=110, reserve_wes_gib=15)
    assert MODULE.command_control(args) == 0
    # WES may join WES, but RNA never starts beside a running WES job
    assert cluster.submitted == [("HG2", "wes", 15)]
    assert "DEFER_EXCLUSIVE	HG3	rnaseq" in capsys.readouterr().out
    cluster.active.clear()
    cluster.complete |= {("HG1", "wes"), ("HG2", "wes")}
    assert MODULE.command_control(args) == 0
    # on an idle cluster exactly one RNA job starts, and nothing beside it
    assert cluster.submitted[1:] == [("HG3", "rnaseq", 110)]
    assert "DEFER_EXCLUSIVE	HG4	rnaseq" in capsys.readouterr().out


def test_exclusive_modality_blocks_other_work_while_it_runs(tmp_path, monkeypatch, capsys):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq"), ("w", "HG2", "wes")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    cluster = FakeCluster(monkeypatch, free_gib=500.0, active={"100"})
    args = _args(tmp_path, manifest, max_running=3, exclusive_modality="rnaseq")
    assert MODULE.command_control(args) == 0
    assert cluster.submitted == []
    assert "DEFER_EXCLUSIVE	HG2	wes" in capsys.readouterr().out


def test_storage_gate_deferrals_do_not_use_up_attempts(tmp_path, monkeypatch):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    gate = ("FAILED", f"{MODULE.STORAGE_GATE_EXIT}:0")
    cluster = FakeCluster(monkeypatch, outcomes={"100": gate})
    args = _args(tmp_path, manifest, max_attempts=1)
    for expected_job in ("9000", "9001"):
        assert MODULE.command_control(args) == 0
        cluster.active.discard(expected_job)
        cluster.outcomes[expected_job] = gate
    assert [sample for sample, _, _ in cluster.submitted] == ["HG1", "HG1"]


def test_repeated_storage_gate_deferrals_stop_the_controller(tmp_path, monkeypatch, capsys):
    rows = [("r", f"HG{i}", "rnaseq") for i in range(1, 5)]
    manifest = _manifest(tmp_path, rows)
    _ledger(tmp_path, [(f"HG{i}", "rnaseq", str(100 + i)) for i in range(1, 5)])
    gate = ("FAILED", f"{MODULE.STORAGE_GATE_EXIT}:0")
    cluster = FakeCluster(monkeypatch, outcomes={str(100 + i): gate for i in range(1, 5)})
    assert MODULE.command_control(_args(tmp_path, manifest)) == 4
    assert cluster.submitted == []
    assert "STORAGE_DEFERRALS" in capsys.readouterr().out


def test_job_missing_from_accounting_waits_instead_of_stopping(tmp_path, monkeypatch, capsys):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq"), ("r", "HG2", "rnaseq")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    cluster = FakeCluster(monkeypatch, outcomes={"100": ("UNKNOWN", "")})
    assert MODULE.command_control(_args(tmp_path, manifest)) == 0
    assert cluster.submitted == [("HG2", "rnaseq", 25)]
    status = _rows(tmp_path / "runs/controller_status.tsv")
    assert {row["sample_id"]: row["state"] for row in status}["HG1"] == "settling"
    assert not (tmp_path / "runs/failure_classifications.tsv").exists()


def test_terminal_classes_are_never_resubmitted(tmp_path, monkeypatch, capsys):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq"), ("w", "HG2", "wes")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    cluster = FakeCluster(monkeypatch, complete={("HG2", "wes")})
    args = SimpleNamespace(manifest=manifest, run_root=tmp_path / "runs",
                           release_commit=MODULE.DEFAULT_RELEASE_COMMIT, from_tsv=None,
                           sample_id="HG1", modality="rnaseq", failure_class="caller",
                           note="HLA-HD segfault reproduced on two nodes")
    assert MODULE.command_classify(args) == 0
    assert MODULE.command_control(_args(tmp_path, manifest)) == 10
    assert cluster.submitted == []
    assert "ALL_DONE" in capsys.readouterr().out


def test_retry_attempts_are_capped(tmp_path, monkeypatch):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    cluster = FakeCluster(monkeypatch, outcomes={"100": ("NODE_FAIL", "0:0")})
    args = _args(tmp_path, manifest, max_attempts=1)
    assert MODULE.command_control(args) == 10
    assert cluster.submitted == []


def test_classify_requires_known_class_note_and_finished_job(tmp_path, monkeypatch):
    manifest = _manifest(tmp_path, [("r", "HG1", "rnaseq")])
    _ledger(tmp_path, [("HG1", "rnaseq", "100")])
    FakeCluster(monkeypatch, active={"100"})
    base = dict(manifest=manifest, run_root=tmp_path / "runs",
                release_commit=MODULE.DEFAULT_RELEASE_COMMIT, from_tsv=None,
                sample_id="HG1", modality="rnaseq")
    with pytest.raises(SystemExit, match="unknown failure class"):
        MODULE.command_classify(SimpleNamespace(**base, failure_class="bad", note="x"))
    with pytest.raises(SystemExit, match="note is required"):
        MODULE.command_classify(SimpleNamespace(**base, failure_class="storage", note=" "))
    with pytest.raises(SystemExit, match="still active"):
        MODULE.command_classify(SimpleNamespace(**base, failure_class="storage", note="quota"))


def test_manual_submit_applies_the_storage_gate(tmp_path, monkeypatch, capsys):
    manifest = _manifest(tmp_path, [("w", "HG1", "wes"), ("w", "HG2", "wes")])
    FakeCluster(monkeypatch, free_gib=120.0)
    args = SimpleNamespace(
        manifest=manifest, batch_id="w", run_root=tmp_path / "runs",
        release_commit=MODULE.DEFAULT_RELEASE_COMMIT, ledger=tmp_path / "ledger.tsv",
        max_submit=5, execute=False, prune_on_success=True, runner=tmp_path / "runner.sbatch",
        min_free_gib=50, reserve_wes_gib=60, reserve_rnaseq_gib=25,
    )
    assert MODULE.command_submit(args) == 0
    output = capsys.readouterr().out
    assert "DRY_RUN\tplanned=1" in output
    assert "DEFER_STORAGE\tw\tHG2\twes" in output


def test_runner_gates_storage_before_staging_and_prunes_failures():
    text = RUNNER.read_text(encoding="utf-8")
    gate = text.index("Storage gate: fail closed before staging")
    assert gate < text.index('download_one "${input_url}"')
    assert "exit 10" in text[gate:text.index('download_one "${input_url}"')]
    assert "trap prune_after_failure EXIT" in text
    assert text.index("trap prune_after_failure EXIT") < text.index('download_one "${input_url}"')
    failure = text[text.index("prune_after_failure() {"):text.index("trap prune_after_failure EXIT")]
    # forensics are copied before anything is deleted, and nothing is pruned after success
    assert failure.index("task_files.tar.gz") < failure.index('rm -rf -- "${WORK_DIR:?}"')
    # a failed forensic archive keeps the work directory instead of losing the diagnostics
    assert "FORENSICS_FAILED" in failure
    assert 'if [[ ${keep_work} -eq 0 ]]; then rm -rf -- "${WORK_DIR:?}"; fi' in failure
    assert "--force-local" in failure
    assert "SAMPLE_COMPLETE" in failure
    assert '"${input_path}.partial"' in failure
    assert "results_failed_attempt" in failure


def test_runner_never_resumes_a_partial_from_an_earlier_job_and_checks_unhashed_bams():
    text = RUNNER.read_text(encoding="utf-8")
    download = text[text.index("download_one() {"):text.index('download_one "${input_url}"')]
    assert download.index('rm -f -- "${target}.partial"') < download.index("curl --fail")
    assert 'gzip -t -- "${target}"' in download
    assert download.index("md5sum --check") < download.index("gzip -t")


def test_runner_quarantines_stale_results_before_a_retry():
    text = RUNNER.read_text(encoding="utf-8")
    quarantine = text.index("A retry must not inherit caller outputs")
    assert quarantine < text.index('"${command[@]}" > "${SAMPLE_ROOT}/nextflow.stdout.log"')
    assert "stale_attempts" in text


def test_controller_job_is_stateless_and_stops_instead_of_retrying():
    text = CONTROLLER.read_text(encoding="utf-8")
    assert text.index('source "${PIPELINE}/bin/roihu_env.sh"') < text.index("set -u")
    assert "control --execute" in text
    for code in ("3)", "4)", "10)"):
        assert code in text
    assert "CONTROLLER_STOPPED" in text
    body = text.split("set -eo pipefail", 1)[1]
    # the only submission is the successor, which cannot start before this job ends
    assert body.count("sbatch ") == 1
    assert '--dependency="afterany:${SLURM_JOB_ID}"' in body
    # a second controller refuses to run beside the first
    assert "another controller is already running" in body
    assert body.index("another controller is already running") < body.index("while true; do")


def test_runner_watches_storage_and_never_completes_a_tainted_run():
    text = RUNNER.read_text(encoding="utf-8")
    gate = text.index("Storage gate: fail closed before staging")
    start = text.index("storage_watcher &")
    # the watcher starts after the gate passed and before anything is downloaded
    assert gate < start < text.index('download_one "${input_url}"')
    watcher = text[text.index("storage_watcher() {"):text.index("stop_watcher() {")]
    assert "set +e" in watcher
    assert "free-gib" in watcher and "TAINT_GIB" in watcher and "WATCH_LOG" in watcher
    # the verdict is first kept off the project quota that may be full
    assert 'mktemp "${TMPDIR:-/tmp}' in text
    taint = text.index("Storage taint: a run during which the quota filled")
    assert text.index('"${command[@]}" > "${SAMPLE_ROOT}/nextflow.stdout.log"') < taint
    assert taint < text.index('touch "${SAMPLE_ROOT}/SAMPLE_COMPLETE"')
    assert "exit 11" in text[taint:text.index('touch "${SAMPLE_ROOT}/SAMPLE_COMPLETE"')]
    assert "Disk quota exceeded|No space left on device" in text
    failure = text[text.index("prune_after_failure() {"):text.index("trap prune_after_failure EXIT")]
    # any failure during exhaustion is reported as the storage taint exit, never the gate's
    assert failure.index("stop_watcher") < failure.index("storage_tainted")
    assert "status=11" in failure
    assert "${status} -ne 10" in failure


def test_rna_prefetch_verifies_before_staging_and_never_touches_runner_files():
    text = (ROOT / "scripts/roihu_prefetch_rna_inputs.sbatch").read_text(encoding="utf-8")
    fetch = text[text.index("fetch() {"):text.index("while true; do")]
    # its own temporary name, never the runner's .partial
    assert ".prefetch" in fetch and ".partial" not in fetch
    # integrity is checked before the file is moved into the runner's path
    assert fetch.index("gzip -t") < fetch.index("mv -n")
    assert fetch.index("md5sum --check") < fetch.index("mv -n")
    assert "SAMPLE_COMPLETE" in fetch
    body = text.split("set -eo pipefail", 1)[1]
    assert "sbatch" not in body and "scancel" not in body
    assert "IFS='|'" in body


def _extension_subject():
    with MODULE.FROZEN_EXTENSION_ROSTER.open(newline="", encoding="utf-8") as handle:
        row = next(row for row in csv.DictReader(handle, delimiter="	")
                   if row["modality"] == "wes")
    return row["subject"]


def test_frozen_extension_subjects_are_refused_without_an_amendment(tmp_path, monkeypatch):
    """The frozen extension roster is staged only under the signed amendment."""
    FakeCluster(monkeypatch)
    manifest = _manifest(tmp_path, [("ext-001", _extension_subject(), "wes")])
    with pytest.raises(SystemExit, match="only with --amendment"):
        MODULE.command_control(_args(tmp_path, manifest))
    # A dry run plans nothing irreversible and needs no amendment.
    assert MODULE.command_control(_args(tmp_path, manifest, execute=False)) == 0


def test_unsigned_amendment_blocks_extension_staging(tmp_path, monkeypatch):
    FakeCluster(monkeypatch)
    manifest = _manifest(tmp_path, [("ext-001", _extension_subject(), "wes")])
    amendment = MODULE.ROOT / "decisions/20261013_extension_v350_preregistration_amendment.json"
    import json
    if json.loads(amendment.read_text(encoding="utf-8"))["gates"].get("author_signed"):
        pytest.skip("the committed amendment is signed")
    with pytest.raises(SystemExit, match="pre-registration is not signed"):
        MODULE.command_control(_args(tmp_path, manifest, amendment=amendment))


def test_runs_carry_their_own_job_name_logs_manifest_and_run_root(tmp_path):
    manifest = _manifest(tmp_path, [("ext-001", "HG00099", "wes")])
    args = _args(tmp_path, manifest, job_name="champhla_ext")
    options = MODULE.run_options(args)
    assert "--job-name=champhla_ext" in options
    assert f"--output={tmp_path / 'runs' / 'logs'}/%x_%j.out" in options
    exports = MODULE.run_exports(args)
    assert f"CHAMPHLA_DEV_MANIFEST={manifest.resolve()}" in exports
    assert f"CHAMPHLA_RUN_DIR={tmp_path / 'runs'}" in exports


def test_nci60_inputs_need_the_signed_regeneration_decision(tmp_path, monkeypatch):
    FakeCluster(monkeypatch)
    manifest = _manifest(tmp_path, [("nci60-wes-001", "NCI60_BT549", "wes")])
    unsigned = tmp_path / "decision.json"
    unsigned.write_text('{"status": "DRAFT", "authorization": {"signed": null}}', encoding="utf-8")
    monkeypatch.setattr(MODULE, "NCI60_DECISION", unsigned)
    with pytest.raises(SystemExit, match="signed"):
        MODULE.command_control(_args(tmp_path, manifest))
    monkeypatch.setattr(MODULE, "NCI60_DECISION",
                        MODULE.ROOT / "decisions/20261026_nci60_v350_regeneration.json")
    assert MODULE.command_control(_args(tmp_path, manifest)) == 0


def test_subsampled_rows_request_more_memory(tmp_path):
    """One-pass seqtk sampling of 50M pairs needs far more than the runner's 8 GB."""
    manifest = _manifest(tmp_path, [("nci60-rnaseq-001", "NCI60_7860", "rnaseq")])
    args = _args(tmp_path, manifest)
    assert f"--mem={MODULE.SUBSAMPLE_MEMORY}" in MODULE.run_options(
        args, {"subsample_pairs": "50000000"})
    assert not any(option.startswith("--mem") for option in MODULE.run_options(
        args, {"subsample_pairs": ""}))
    assert not any(option.startswith("--mem") for option in MODULE.run_options(args))
