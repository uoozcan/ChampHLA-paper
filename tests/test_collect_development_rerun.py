from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "collect_development_rerun", ROOT / "scripts/collect_development_rerun.py"
)
assert SPEC and SPEC.loader
COLLECTOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COLLECTOR)


def _write_dispositions(sample_root: Path, callers: list[str]) -> None:
    sample_root.mkdir(parents=True)
    rows = ["caller\toutput_file_count\ttrace_statuses\tdisposition"]
    rows.extend(f"{caller}\t1\tCOMPLETED:exit=0\toutputs_present" for caller in callers)
    (sample_root / "caller_dispositions.tsv").write_text(
        "\n".join(rows) + "\n", encoding="utf-8"
    )


def test_dispositions_normalizes_workflow_directories_to_paper_caller_names(tmp_path):
    sample_root = tmp_path / "sample"
    _write_dispositions(sample_root, ["hlahd", "optitype", "polysolver", "spechla", "t1k"])

    observed = COLLECTOR._dispositions(sample_root)

    assert set(observed) == {"HLA-HD", "OptiType", "POLYSOLVER", "SpecHLA", "T1K"}
    assert observed["T1K"]["caller"] == "t1k"


def test_dispositions_rejects_unknown_workflow_directory(tmp_path):
    sample_root = tmp_path / "sample"
    _write_dispositions(sample_root, ["t1k", "surprise"])

    with pytest.raises(ValueError, match="unknown caller directory 'surprise'"):
        COLLECTOR._dispositions(sample_root)


def test_aggregate_rows_preserves_explicit_noncall(tmp_path):
    aggregate = tmp_path / "aggregated_calls.tsv"
    aggregate.write_text(
        "sample\ttool\tmodality\tgene\tallele1\tallele2\tis_callable\n"
        "HG00097\thlahd\twes\tB\tHLA-B*07:02:01\t-\t0\n",
        encoding="utf-8",
    )

    observed = COLLECTOR._aggregate_rows(aggregate, "HG00097", "wes")

    assert observed[("HLA-HD", "B")]["_is_callable"] is False
    assert observed[("HLA-HD", "B")]["allele1"] == "HLA-B*07:02:01"


def test_aggregate_rows_rejects_invalid_callability_token(tmp_path):
    aggregate = tmp_path / "aggregated_calls.tsv"
    aggregate.write_text(
        "sample\ttool\tmodality\tgene\tallele1\tallele2\tis_callable\n"
        "HG00097\tt1k\twes\tA\tA*01:01\tA*02:01\tmaybe\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="invalid is_callable"):
        COLLECTOR._aggregate_rows(aggregate, "HG00097", "wes")


def _normalized(subject: str, status: str, first: str = "", second: str = ""):
    return {
        "subject": subject, "modality": "wes", "gene": "A", "caller": "T1K",
        "call_status": status, "allele1": first, "allele2": second,
        "homozygosity_basis": "caller_native_declaration" if first == second and first else "",
        "no_call_reason": "",
    }


def test_cell_comparison_is_truth_free_and_classifies_state_changes():
    stored = [_normalized("S1", "callable", "A*01:01", "A*02:01")]
    rerun = [_normalized("S1", "callable", "A*01:01", "A*03:01")]

    rows = COLLECTOR.compare_stored_and_rerun_calls(stored, rerun)

    assert rows[0]["difference_class"] == "call_changed"
    assert rows[0]["same_state_and_pair"] == 0
    assert not any("truth" in field for field in rows[0])


def test_abstain_sensitivity_removes_only_native_homozygous_declarations():
    native = _normalized("S1", "callable", "A*01:01", "A*01:01")
    heterozygous = _normalized("S2", "callable", "A*01:01", "A*02:01")

    rows = COLLECTOR.abstain_native_declarations([native, heterozygous])

    assert rows[0]["call_status"] == "partial"
    assert rows[0]["allele1"] == rows[0]["allele2"] == ""
    assert rows[1] == heterozygous
    assert native["call_status"] == "callable"


def _versions(result_sample: Path, text: str) -> None:
    (result_sample / "arcashla").mkdir(parents=True, exist_ok=True)
    (result_sample / "arcashla" / "versions.yml").write_text(text, encoding="utf-8")


def test_native_completion_follows_the_signed_singleton_policy(tmp_path):
    # decisions/20261008_singleton_native_homozygosity.json: HLA-HD's '-' is a
    # declaration; arcasHLA's single allele is one only before release 0.4.0.
    sample = tmp_path / "S1"
    assert COLLECTOR.native_completion_eligible("HLA-HD", sample)
    assert not COLLECTOR.native_completion_eligible("ArcasHLA", sample)  # unknown version
    _versions(sample, '"ARCASHLA":\n    arcashla: 0.2.0\n')
    assert COLLECTOR.arcashla_version(sample) == (0, 2, 0)
    assert COLLECTOR.native_completion_eligible("ArcasHLA", sample)
    _versions(sample, '"ARCASHLA":\n    arcashla: 0.5.0\n')
    assert not COLLECTOR.native_completion_eligible("ArcasHLA", sample)
    _versions(sample, '"ARCASHLA":\n    arcashla: unknown\n')
    assert not COLLECTOR.native_completion_eligible("ArcasHLA", sample)
    for caller in ("OptiType", "T1K", "POLYSOLVER", "SpecHLA"):
        assert not COLLECTOR.native_completion_eligible(caller, sample)


def test_declared_hlahd_homozygote_is_completed_and_then_abstains_in_sensitivity():
    from champhla_confirmation.parsers import native_homozygous_pair
    from champhla_confirmation.schema import normalize_caller_row
    reference = COLLECTOR._reference()
    summary = "A\tHLA-A*01:01:01\tHLA-A*03:01:01\nB\tHLA-B*07:02:01\t-\n"
    declared = native_homozygous_pair("HLA-HD", summary, "B")
    base = {"cohort": "c", "subject": "S1", "population": "", "modality": "rnaseq",
            "gene": "B", "caller": "HLA-HD", "allele1_raw": "HLA-B*07:02:01",
            "allele2_raw": "-", "database_version": "", "database_version_basis": "",
            "input_reference_build": "GRCh37", "source_path": "", "source_sha256": ""}
    # the aggregate's single allele alone abstains ...
    assert normalize_caller_row(base, reference=reference,
                                singleton_policy="abstain")["call_status"] == "partial"
    # ... and the collector's completion yields exactly the declared pair
    completed = normalize_caller_row({**base, "allele2_raw": base["allele1_raw"]},
                                     reference=reference, singleton_policy="abstain")
    assert completed["call_status"] == "callable"
    assert (completed["allele1"], completed["allele2"]) == tuple(declared)
    # the collector restores the caller's literal second field after completion
    row = {**completed, "allele2_raw": base["allele2_raw"],
           "homozygosity_basis": "caller_native_declaration"}
    assert row["allele2_raw"] == "-"
    sensitivity = COLLECTOR.abstain_native_declarations([row])[0]
    assert sensitivity["call_status"] == "partial" and sensitivity["allele1"] == ""
    # a heterozygous line is never a declaration
    assert native_homozygous_pair("HLA-HD", summary, "A") is None


def test_arcashla_release_falls_back_to_the_pinned_container(tmp_path):
    sample_root = tmp_path / "samples/rnaseq/S1"
    result_sample = sample_root / "results" / "S1"
    _versions(result_sample, '"ARCASHLA_BAM":\n    arcashla: \n')  # the v3.5.0 probe output
    assert COLLECTOR.arcashla_version(result_sample) is None
    digest = next(iter(COLLECTOR.ARCASHLA_CONTAINER_VERSIONS))
    (sample_root / "container_sha256.txt").write_text(
        f"{digest}  /scratch/x/containers/arcashla.sif\n", encoding="utf-8")
    assert COLLECTOR.arcashla_version(result_sample) == (0, 2, 0)
    assert COLLECTOR.native_completion_eligible("ArcasHLA", result_sample)
    (sample_root / "container_sha256.txt").write_text(
        f"{'0' * 64}  /scratch/x/containers/arcashla.sif\n", encoding="utf-8")
    assert not COLLECTOR.native_completion_eligible("ArcasHLA", result_sample)


def test_a_roster_without_stored_calls_collects_with_an_empty_comparison(tmp_path, monkeypatch):
    """The frozen extension has no historical calls: --no-stored-calls skips the
    stored-to-rerun comparison instead of comparing against the development table."""
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text("sample_id\tmodality\tbatch_id\nHG99999\twes\text-wes-001\n",
                        encoding="utf-8")
    calls = [_normalized("HG99999", "callable", "A*01:01", "A*02:01")]
    calls = [dict(calls[0], gene=gene, caller=caller)
             for gene in COLLECTOR.GENES for caller in COLLECTOR.PANELS["wes"]]
    monkeypatch.setattr(COLLECTOR, "_reference", lambda: None)
    monkeypatch.setattr(COLLECTOR, "collect_sample",
                        lambda row, run_root, reference, commit: (calls, [], {"subject": "HG99999"}, []))
    output = tmp_path / "collection"
    assert COLLECTOR.main(["--manifest", str(manifest), "--output-dir", str(output),
                           "--no-stored-calls"]) == 0
    manifest_json = __import__("json").loads(
        (output / "collection_manifest.json").read_text(encoding="utf-8"))
    assert manifest_json["stored_vs_rerun_cell_rows"] == 0
    assert manifest_json["stored_calls_sha256"] == ""
    assert manifest_json["caller_rows"] == len(calls)
