import json
from pathlib import Path

from champhla_confirmation.readiness import audit_extension_readiness


def test_readiness_fails_closed_for_pending_caller(tmp_path):
    allele_list = tmp_path / "Allelelist.txt"
    allele_list.write_text("AlleleID,Allele\n1,A*01:01\n", encoding="utf-8")
    sums = tmp_path / "SHA256SUMS"
    sums.write_text("placeholder\n", encoding="utf-8")
    protocol = tmp_path / "protocol.json"
    protocol.write_text(json.dumps({"valid": True, "truth_join_permitted": True}), encoding="utf-8")
    resources = tmp_path / "resources.json"
    resources.write_text(json.dumps({
        "common_normalization_reference": {
            "allele_list": "Allelelist.txt", "sha256_manifest": "SHA256SUMS"
        },
        "callers": {"Tool": {
            "status": "pending", "database_release": "", "allele_list": "",
            "container_digest": "",
        }},
    }), encoding="utf-8")
    output = tmp_path / "audit.json"
    result = audit_extension_readiness(str(tmp_path), str(protocol), str(resources), str(output))
    assert not result["ready"]
    assert not result["truth_join_permitted"]
    assert "Tool" in result["caller_failures"]


def test_repository_permits_execution_but_not_the_truth_join(tmp_path):
    """decisions/20261009_extension_voting_panels_only.json: the six voting callers are
    ready, the four non-voting comparators are excluded by decision, and the truth join
    stays closed until a signed pre-registration records the public release DOI."""
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / "readiness.json"
    result = audit_extension_readiness(
        str(root), str(root / "artifacts" / "benchmark_resource_protocol_audit.json"),
        str(root / "configs" / "caller_resources_v2.json"), str(output),
    )
    assert result["extension_execution_permitted"]
    assert result["required_callers"] == ["ArcasHLA", "HLA-HD", "OptiType", "POLYSOLVER",
                                          "SpecHLA", "T1K"]
    assert set(result["excluded_callers"]) == {"HISAT-genotype", "HLA*LA", "Kourami", "seq2HLA"}
    assert not result["truth_join_permitted"]
    assert "no confirmatory pre-registration supplied" in result["truth_join_blockers"]


def _gate(tmp_path, callers, preregistration=None):
    (tmp_path / "Allelelist.txt").write_text("AlleleID,Allele\n1,A*01:01\n", encoding="utf-8")
    (tmp_path / "SHA256SUMS").write_text("x\n", encoding="utf-8")
    (tmp_path / "decision.json").write_text("{}", encoding="utf-8")
    protocol = tmp_path / "protocol.json"
    protocol.write_text(json.dumps({"valid": True, "truth_join_permitted": True}), encoding="utf-8")
    resources = tmp_path / "resources.json"
    resources.write_text(json.dumps({
        "common_normalization_reference": {"allele_list": "Allelelist.txt",
                                           "sha256_manifest": "SHA256SUMS"},
        "callers": callers}), encoding="utf-8")
    return audit_extension_readiness(str(tmp_path), str(protocol), str(resources),
                                     str(tmp_path / "out.json"), preregistration)


READY = {"status": "ready", "database_release": "3.40.0", "allele_list": "Allelelist.txt",
         "container_digest": "sha256:" + "0" * 64}


def test_exclusion_needs_a_recorded_decision(tmp_path):
    result = _gate(tmp_path, {"Tool": READY, "Other": {"extension_required": False}})
    assert result["caller_failures"]["Other"] == ["excluded without a recorded decision"]
    result = _gate(tmp_path, {"Tool": READY, "Other": {"extension_required": False,
                                                        "excluded_by": "decision.json"}})
    assert result["extension_execution_permitted"]
    assert result["excluded_callers"] == {"Other": "decision.json"}


def test_tampered_native_allele_list_fails(tmp_path):
    result = _gate(tmp_path, {"Tool": {**READY, "allele_list_sha256": "0" * 64}})
    assert "native allele_list checksum mismatch" in result["caller_failures"]["Tool"]


def test_truth_join_needs_a_signed_preregistration_with_a_doi(tmp_path):
    prereg = tmp_path / "prereg.json"
    prereg.write_text(json.dumps({"status": "SIGNED", "authorization": {"signed": "now"},
                                  "release": {"doi": ""}}), encoding="utf-8")
    result = _gate(tmp_path, {"Tool": READY}, str(prereg))
    assert not result["truth_join_permitted"]
    assert "pre-registration records no public release DOI" in result["truth_join_blockers"]
    prereg.write_text(json.dumps({"status": "SIGNED", "authorization": {"signed": "now"},
                                  "release": {"doi": "10.5281/zenodo.1"}}), encoding="utf-8")
    assert _gate(tmp_path, {"Tool": READY}, str(prereg))["truth_join_permitted"]


def _amendment_root(tmp_path):
    """A minimal tree holding every frozen extension path and the amended record."""
    from champhla_confirmation.readiness import EXTENSION_ANALYSIS_PATHS

    for relative in EXTENSION_ANALYSIS_PATHS:
        path = tmp_path / relative
        if relative.endswith((".py", ".json", ".tsv")):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"frozen {relative}\n", encoding="utf-8")
        else:
            path.mkdir(parents=True, exist_ok=True)
            (path / "module.py").write_text("frozen = True\n", encoding="utf-8")
    original = tmp_path / "decisions" / "original.json"
    original.parent.mkdir(parents=True, exist_ok=True)
    original.write_text("{}\n", encoding="utf-8")
    return original


def _amendment(tmp_path, original, **overrides):
    from champhla_confirmation.io import sha256
    from champhla_confirmation.readiness import (
        AMENDMENT_SCHEMA, PINNED_RELEASE_COMMIT, extension_analysis_code_sha256)

    record = {
        "schema_version": AMENDMENT_SCHEMA,
        "status": "SIGNED - test",
        "amends_without_rewriting": {"record": "decisions/original.json",
                                     "sha256": sha256(original)},
        "release_pin": {"commit": PINNED_RELEASE_COMMIT, "analysis_commit": "a" * 40,
                        "analysis_code_sha256": extension_analysis_code_sha256(tmp_path)},
        "zenodo": {"reserved_doi": "10.5281/zenodo.1",
                   "publication_record": "decisions/published.json"},
        "authorization": {"signed": "now"},
        "gates": {"author_signed": True, "analysis_commit_pinned": True,
                  "zenodo_bundle_updated": True,
                  "extension_stage_or_submit_permitted": True},
    }
    publish = overrides.pop("publish", True)
    for dotted, value in overrides.items():
        target = record
        *parents, leaf = dotted.split("__")
        for key in parents:
            target = target[key]
        target[leaf] = value
    path = tmp_path / "decisions" / "amendment.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    published = tmp_path / "decisions" / "published.json"
    if publish:
        published.write_text(json.dumps({"published": True, "doi": "10.5281/zenodo.1",
                                         "amendment_sha256": sha256(path)}), encoding="utf-8")
    elif published.exists():
        published.unlink()
    return str(path)


def test_amendment_permits_the_truth_join_only_when_signed_pinned_and_published(tmp_path):
    from champhla_confirmation.readiness import _preregistration_blockers

    original = _amendment_root(tmp_path)
    assert _preregistration_blockers(tmp_path, _amendment(tmp_path, original)) == []

    unsigned = _amendment(tmp_path, original, status="DRAFT", authorization__signed=None,
                          gates__author_signed=False)
    assert "pre-registration is not signed" in _preregistration_blockers(tmp_path, unsigned)

    unpublished = _amendment(tmp_path, original, publish=False)
    assert _preregistration_blockers(tmp_path, unpublished) == [
        "Zenodo pre-registration deposit is not published"]

    # A deposit published for a different (earlier) amendment text does not count.
    stale = _amendment(tmp_path, original)
    Path(stale).write_text(Path(stale).read_text(encoding="utf-8") + " ", encoding="utf-8")
    assert "published deposit does not hold this signed amendment" in _preregistration_blockers(
        tmp_path, stale)

    wrong_release = _amendment(tmp_path, original, release_pin__commit="b" * 40)
    assert "amendment does not pin workflow release 3.5.0" in _preregistration_blockers(
        tmp_path, wrong_release)


def test_amendment_refuses_code_changed_after_the_pin_or_a_rewritten_original(tmp_path):
    from champhla_confirmation.readiness import _preregistration_blockers

    original = _amendment_root(tmp_path)
    path = _amendment(tmp_path, original)
    (tmp_path / "scripts" / "run_extension.py").write_text("changed\n", encoding="utf-8")
    assert "extension analysis code changed after the pin" in _preregistration_blockers(
        tmp_path, path)
    original.write_text('{"rewritten": true}\n', encoding="utf-8")
    assert "amended pre-registration was rewritten or is missing" in _preregistration_blockers(
        tmp_path, path)


def test_staging_needs_the_signature_but_not_yet_the_zenodo_publication(tmp_path):
    from champhla_confirmation.readiness import extension_staging_blockers

    original = _amendment_root(tmp_path)
    unpublished = _amendment(tmp_path, original, publish=False)
    assert extension_staging_blockers(str(tmp_path), unpublished) == []
    closed = _amendment(tmp_path, original, gates__extension_stage_or_submit_permitted=False)
    assert "amendment does not permit extension staging" in extension_staging_blockers(
        str(tmp_path), closed)
    unsigned = _amendment(tmp_path, original, status="DRAFT", gates__author_signed=False)
    assert "pre-registration is not signed" in extension_staging_blockers(str(tmp_path), unsigned)


def test_repository_amendment_blocks_staging_until_it_is_signed():
    """The committed amendment stays fail-closed until its signature is recorded."""
    from champhla_confirmation.readiness import extension_staging_blockers

    root = Path(__file__).resolve().parents[1]
    amendment = "decisions/20261013_extension_v350_preregistration_amendment.json"
    record = json.loads((root / amendment).read_text(encoding="utf-8"))
    blockers = extension_staging_blockers(str(root), amendment)
    if not record["gates"].get("author_signed"):
        assert "pre-registration is not signed" in blockers
    else:
        assert blockers == []
