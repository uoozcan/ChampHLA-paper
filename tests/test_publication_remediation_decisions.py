import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = (
    ROOT / "decisions/20261013_workflow_rerun_primary.json",
    ROOT / "decisions/20261013_corrected_reference_presentation.json",
    ROOT / "decisions/20261013_fimm_venex_scope_and_gate.json",
)


def test_locked_decisions_have_distinct_signed_records():
    records = [json.loads(path.read_text(encoding="utf-8")) for path in FILES]
    assert len({record["decision_id"] for record in records}) == 3
    assert all(record["status"] == "SIGNED" for record in records)
    assert all(record["authorization"]["signed"] for record in records)
    assert all(record["supersedes_fields_of"] for record in records)


def test_workflow_record_pins_the_accepted_release_and_full_rosters():
    record = json.loads(FILES[0].read_text(encoding="utf-8"))["decision"]
    assert record["commit"] == "66d949da90861da6cf60cf1d4bee2f094f2518bd"
    assert record["archive_sha256"] == "22d9ed3bd808aec7364fbe869ad048c561be38bd02479dff530fe13fee4da7ed"
    assert "130 WES and 106 RNA-seq" in record["development_scope"]
    assert "sole source" in record["primary_evidence"]


def test_reference_and_patient_scope_guards_are_explicit():
    reference = json.loads(FILES[1].read_text(encoding="utf-8"))["decision"]
    cohorts = json.loads(FILES[2].read_text(encoding="utf-8"))["decision"]
    assert "every method" in reference["presentation"]
    assert "historical stored-output" in reference["historical_checksums"]
    assert "block submission" in cohorts["submission_gate"]
    assert "outside public" in cohorts["privacy"]
