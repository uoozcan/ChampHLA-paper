from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/roihu_run_development_sample.sbatch"


def test_runner_is_truth_free_and_uses_released_paper_profile():
    text = RUNNER.read_text(encoding="utf-8")
    lowered = text.lower()

    assert "-profile roihu,singularity,paper" in text
    assert "--require_full_panel true" in text
    assert '--release_commit "${RELEASE_COMMIT}"' in text
    assert "66d949da90861da6cf60cf1d4bee2f094f2518bd" in text
    assert "panelhla-3.5.0" in lowered
    assert "reference_typing" not in lowered
    assert "ground_truth" not in lowered
    assert "truth.tsv" not in lowered
    assert 'source "${PIPELINE}/bin/roihu_env.sh"' in text
    assert '-name "champhla_dev_${modality}_${sample_id}_${SLURM_JOB_ID}"' in text


def test_runner_freezes_required_provenance_before_pruning():
    text = RUNNER.read_text(encoding="utf-8")

    for required in (
        "input_sha256.txt",
        "container_sha256.txt",
        "spechla_git_commit.txt",
        "workflow_files_sha256.txt",
        "execution_trace.txt",
        "caller_dispositions.tsv",
        "result_files_sha256.txt",
        "*.parser.json",
        "SAMPLE_COMPLETE",
    ):
        assert required in text

    assert text.index('touch "${SAMPLE_ROOT}/SAMPLE_COMPLETE"') < text.index(
        'rm -rf -- "${WORK_DIR}"'
    )


def test_runner_fails_on_unsafe_identifiers_and_unaccounted_callers():
    text = RUNNER.read_text(encoding="utf-8")

    assert "Unsafe sample or modality" in text
    assert "missing_without_trace" in text
    assert "T1K produced output but exactly one parser audit was not preserved" in text
    assert 'if [[ -d ${RESULTS}/${sample_id}/t1k ]]' in text
    assert "REQUIRE_T1K_SUCCESS" in text
    assert "current nine-column schema" in text
