import json
from pathlib import Path
from typing import List, Optional

from champhla_recovery.cli import audit_manuscript_claims_main
from champhla_recovery.io import sha256
from champhla_recovery.manuscript import audit_claims
from champhla_recovery.registry import validate_registry


def _registry(tmp_path: Path) -> Path:
    artifact = tmp_path / "artifact.tsv"
    artifact.write_text("x\n1\n", encoding="utf-8")
    registry = tmp_path / "registry.tsv"
    registry.write_text(
        "result_id\tcohort\tmodality\tmethod\tanalysis_status\tvalidity\tsubjects\tloci\tcorrect\taccuracy\tartifact_path\tartifact_sha256\tabstract_allowed\tclaim_boundary\n"
        f"GOOD\tdev\twes\tmethod\tdiscovery\tvalid\t1\t3\t3\t1.0\tartifact.tsv\t{sha256(artifact)}\t0\ttest\n"
        f"BAD\tdev\twgs\tmethod\tdiscovery\tinvalid\t1\t3\t1\t0.333\tartifact.tsv\t{sha256(artifact)}\t0\ttest\n",
        encoding="utf-8",
    )
    return registry


def test_registry_rejects_invalid_abstract_claim(tmp_path: Path):
    registry = _registry(tmp_path)
    text = registry.read_text(encoding="utf-8").replace("BAD\tdev\twgs\tmethod\tdiscovery\tinvalid", "BAD\tdev\twgs\tmethod\tdiscovery\tinvalid").replace("\t0\ttest\n", "\t1\ttest\n", 2)
    registry.write_text(text, encoding="utf-8")
    assert validate_registry(str(registry), str(tmp_path))


def test_versioned_registry_rejects_mixed_schema(tmp_path: Path):
    registry = _registry(tmp_path)
    lines = registry.read_text(encoding="utf-8").splitlines()
    lines[0] += "\tschema_version\tendpoint\tintended_denominator\tacquired_denominator\ttruth_evaluable_denominator\tcallable_denominator\tci_lo\tci_hi\tinterval_method\traw_p\tadjusted_p\tsensitivity_adjusted_p\tinference_family\tfamily_size\tfitted_status\tdevelopment_status\trecord_type\tworkflow_session\tworkflow_commit\tresource_record_count\tsource_artifact_sha256\tresult_kind\testimate\tci_low\tci_high\tunit\tevents"
    artifact_hash = lines[1].split("\t")[11]
    tail = "\texact\t3\t3\t3\t3\t0.5\t1\tbootstrap\t\t\t\t\t\tnot_fitted\tdevelopment\tscientific_result\t\t\t\t" + artifact_hash + "\tperformance\t1\t0.5\t1\tproportion\t"
    lines[1] += "\tpanelhla-result-registry-4" + tail
    lines[2] += "\tpanelhla-result-registry-1" + tail
    registry.write_text("\n".join(lines) + "\n", encoding="utf-8")
    failures = validate_registry(str(registry), str(tmp_path))
    assert any("unknown or mixed schema_version" in failure for failure in failures)


def test_active_result_registry_is_versioned_and_valid():
    root = Path(__file__).resolve().parents[1]
    assert validate_registry(str(root / "result_registry.tsv"), str(root)) == []


def test_registry_rejects_unknown_analysis_status(tmp_path: Path):
    registry = _registry(tmp_path)
    registry.write_text(
        registry.read_text(encoding="utf-8").replace("\tdiscovery\t", "\tnot_a_status\t"),
        encoding="utf-8",
    )
    failures = validate_registry(str(registry), str(tmp_path))
    assert any("unknown analysis_status" in failure for failure in failures)


def test_manuscript_accepts_registered_valid_result(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript_dir = tmp_path / "benchmark"
    manuscript_dir.mkdir()
    manuscript = manuscript_dir / "manuscript.md"
    manuscript.write_text("# Results\nVerified result [RESULT:GOOD].\n", encoding="utf-8")
    claims = tmp_path / "claims.tsv"
    claims.write_text(
        "claim_id\tdraft\tsection\tclaim\tstatus\tevidence_result_id\taction\n"
        "C1\tbenchmark\tResults\tVerified\tsupported\tGOOD\tretain\n",
        encoding="utf-8",
    )
    result = audit_claims(str(manuscript), str(registry), str(claims), str(tmp_path / "audit.json"), str(tmp_path))
    # The claim and registry side is clean: a registered, valid result is cited.
    assert result["failures"] == []
    assert result["result_references"] == ["GOOD"]
    assert result["manuscript"] == "benchmark/manuscript.md"
    # Submission readiness is a stricter property, and this fixture is a stub, so
    # it is withheld -- see test_manuscript_requires_submission_elements.
    assert result["submission_ready"] is False


def test_manuscript_requires_submission_elements(tmp_path: Path):
    """Front and back matter are part of readiness, not optional polish.

    A manuscript can cite every result correctly and still be unsubmittable for
    want of references, authors, ethics, funding, competing interests or a
    figure. The audit used to report submission_ready for exactly such a draft.
    """
    registry = _registry(tmp_path)
    manuscript_dir = tmp_path / "benchmark"
    manuscript_dir.mkdir()
    manuscript = manuscript_dir / "manuscript.md"
    manuscript.write_text("# Results\nVerified result [RESULT:GOOD].\n", encoding="utf-8")
    claims = tmp_path / "claims.tsv"
    claims.write_text(
        "claim_id\tdraft\tsection\tclaim\tstatus\tevidence_result_id\taction\n"
        "C1\tbenchmark\tResults\tVerified\tsupported\tGOOD\tretain\n",
        encoding="utf-8",
    )
    result = audit_claims(str(manuscript), str(registry), str(claims), str(tmp_path / "audit.json"), str(tmp_path))
    missing = set(result["missing_submission_elements"])
    for element in ("references", "author list", "ethics statement", "funding statement",
                    "competing interests", "numbered figure reference"):
        assert element in missing, f"{element} should be reported missing"
    assert result["submission_ready"] is False


def test_manuscript_rejects_unrecognised_claim_status(tmp_path: Path):
    """An unknown status passed silently, so a typo disabled the check."""
    registry = _registry(tmp_path)
    manuscript = tmp_path / "source.md"
    manuscript.write_text("Nothing cited here.\n", encoding="utf-8")
    claims = tmp_path / "claims.tsv"
    claims.write_text(
        "claim_id\tdraft\tsection\tclaim\tstatus\tevidence_result_id\taction\n"
        "C1\tsource_original\tResults\tbad\tsuported\tGOOD\tretain\n",
        encoding="utf-8",
    )
    result = audit_claims(str(manuscript), str(registry), str(claims), str(tmp_path / "audit.json"), str(tmp_path))
    assert any("unrecognised status" in failure for failure in result["failures"])


def test_manuscript_flags_unresolved_to_confirm_block(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript = tmp_path / "source.md"
    manuscript.write_text("### TO CONFIRM\nInsert the SpecHLA reference.\n", encoding="utf-8")
    claims = tmp_path / "claims.tsv"
    claims.write_text(
        "claim_id\tdraft\tsection\tclaim\tstatus\tevidence_result_id\taction\n"
        "C1\tsource_original\tResults\tok\tsupported\tGOOD\tretain\n",
        encoding="utf-8",
    )
    result = audit_claims(str(manuscript), str(registry), str(claims), str(tmp_path / "audit.json"), str(tmp_path))
    assert any("placeholder" in failure for failure in result["failures"])


def _claims(tmp_path: Path, row: str, header_extra: str = "") -> Path:
    claims = tmp_path / "claims.tsv"
    claims.write_text(
        f"claim_id\tdraft\tsection\tclaim\tstatus\tevidence_result_id{header_extra}\taction\n{row}\n",
        encoding="utf-8",
    )
    return claims


def _benchmark_manuscript(tmp_path: Path, body: str) -> Path:
    manuscript_dir = tmp_path / "benchmark"
    manuscript_dir.mkdir(exist_ok=True)
    manuscript = manuscript_dir / "manuscript.md"
    manuscript.write_text(body, encoding="utf-8")
    return manuscript


def _audit(tmp_path: Path, manuscript: Path, registry: Path, claims: Path,
           author_gate: Optional[Path] = None) -> dict:
    return audit_claims(
        str(manuscript), str(registry), str(claims),
        str(tmp_path / "audit.json"), str(tmp_path),
        author_gate=str(author_gate) if author_gate else None,
    )


def _author_gate(tmp_path: Path, *, submission_allowed: bool = False,
                 blocking_items: Optional[List[str]] = None,
                 schema_version: str = "panelhla-fimm-submission-gate-2") -> Path:
    if blocking_items is None:
        blocking_items = [] if submission_allowed else ["ethics identifier", "secure manifest"]
    gate = tmp_path / "fimm_gate.json"
    gate.write_text(json.dumps({
        "schema_version": schema_version,
        "status": "READY" if submission_allowed else "BLOCKED_AUTHOR_AND_SECURE_PROVENANCE",
        "submission_allowed": submission_allowed,
        "blocking_items": blocking_items,
    }), encoding="utf-8")
    return gate


def test_author_gate_adds_pending_items_without_scientific_failure(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript = _benchmark_manuscript(tmp_path, "## Results\n\nExploratory result [RESULT:GOOD].\n")
    claims = _claims(tmp_path, "C1\tbenchmark\tResults\tResult\tsupported\tGOOD\tretain")
    gate = _author_gate(tmp_path)

    result = _audit(tmp_path, manuscript, registry, claims, gate)

    assert result["blocking_failures"] == []
    assert result["author_gate"] == "fimm_gate.json"
    assert result["author_gate_status"] == "BLOCKED_AUTHOR_AND_SECURE_PROVENANCE"
    assert result["pending_author_input"] == [
        "FIMM: ethics identifier", "FIMM: secure manifest",
    ]
    assert result["failures"] == ["author gate has 2 unresolved item(s)"]


def test_resolved_author_gate_allows_clean_source_audit(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript = tmp_path / "source.md"
    manuscript.write_text("Verified result [RESULT:GOOD].\n", encoding="utf-8")
    claims = _claims(
        tmp_path, "C1\tsource_original\tResults\tResult\tsupported\tGOOD\tretain")
    gate = _author_gate(tmp_path, submission_allowed=True)

    result = _audit(tmp_path, manuscript, registry, claims, gate)

    assert result["pending_author_input"] == []
    assert result["blocking_failures"] == []
    assert result["failures"] == []
    assert result["submission_ready"] is True


def test_missing_author_gate_fails_closed(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript = tmp_path / "source.md"
    manuscript.write_text("Verified result [RESULT:GOOD].\n", encoding="utf-8")
    claims = _claims(
        tmp_path, "C1\tsource_original\tResults\tResult\tsupported\tGOOD\tretain")

    result = _audit(tmp_path, manuscript, registry, claims, tmp_path / "missing.json")

    assert any("author gate is missing" in failure for failure in result["blocking_failures"])


def test_invalid_author_gate_schema_fails_closed(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript = tmp_path / "source.md"
    manuscript.write_text("Verified result [RESULT:GOOD].\n", encoding="utf-8")
    claims = _claims(
        tmp_path, "C1\tsource_original\tResults\tResult\tsupported\tGOOD\tretain")
    gate = _author_gate(tmp_path, schema_version="unknown-gate-schema")

    result = _audit(tmp_path, manuscript, registry, claims, gate)

    assert any("unknown schema_version" in failure for failure in result["blocking_failures"])


def test_malformed_author_gate_fails_closed(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript = tmp_path / "source.md"
    manuscript.write_text("Verified result [RESULT:GOOD].\n", encoding="utf-8")
    claims = _claims(
        tmp_path, "C1\tsource_original\tResults\tResult\tsupported\tGOOD\tretain")
    gate = tmp_path / "fimm_gate.json"
    gate.write_text("{not json", encoding="utf-8")

    result = _audit(tmp_path, manuscript, registry, claims, gate)

    assert any("author gate cannot be read" in failure for failure in result["blocking_failures"])


def test_cli_waives_pending_gate_only_in_review_mode(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript = _benchmark_manuscript(tmp_path, "## Results\n\nExploratory result [RESULT:GOOD].\n")
    claims = _claims(tmp_path, "C1\tbenchmark\tResults\tResult\tsupported\tGOOD\tretain")
    gate = _author_gate(tmp_path)
    base = [
        "--manuscript", str(manuscript),
        "--registry", str(registry),
        "--claims", str(claims),
        "--output", str(tmp_path / "audit.json"),
        "--root", str(tmp_path),
        "--author-gate", str(gate),
    ]

    assert audit_manuscript_claims_main([*base, "--allow-pending-author-input"]) == 0
    assert audit_manuscript_claims_main(base) == 2


def test_exploratory_claim_passes_when_hedged_in_its_section(tmp_path: Path):
    """The hedge is what makes an exploratory claim honest, so the check reads it.

    This warning used to fire for every exploratory row without ever opening the
    manuscript, while its message asserted it had checked "the text".
    """
    registry = _registry(tmp_path)
    manuscript = _benchmark_manuscript(
        tmp_path,
        "## Results\n\nThe method reached 3 of 3 loci [RESULT:GOOD], but the paired\n"
        "test does not reach significance and the result is development evidence.\n",
    )
    claims = _claims(tmp_path, "C1\tbenchmark\tResults\tHedged\texploratory\tGOOD\tretain")
    result = _audit(tmp_path, manuscript, registry, claims)
    assert not any("exploratory" in warning for warning in result["warnings"]), result["warnings"]


def test_exploratory_claim_warns_when_its_section_drops_the_hedge(tmp_path: Path):
    """Deleting the hedge must fail the check rather than pass silently."""
    registry = _registry(tmp_path)
    manuscript = _benchmark_manuscript(
        tmp_path,
        "## Results\n\nThe method reached 3 of 3 loci [RESULT:GOOD] and is the\n"
        "recommended choice for every assay.\n",
    )
    claims = _claims(tmp_path, "C1\tbenchmark\tResults\tUnhedged\texploratory\tGOOD\tretain")
    result = _audit(tmp_path, manuscript, registry, claims)
    assert any("not labelled as exploratory" in warning for warning in result["warnings"]), \
        result["warnings"]


def test_exploratory_claim_is_not_this_documents_job_when_absent(tmp_path: Path):
    """A claim the document never makes cannot be mislabelled by it.

    The supplementary inherited warnings about claims only the main text asserts.
    """
    registry = _registry(tmp_path)
    manuscript = _benchmark_manuscript(tmp_path, "## Results\n\nNo registry claim is cited here.\n")
    claims = _claims(tmp_path, "C1\tbenchmark\tResults\tElsewhere\texploratory\tGOOD\tretain")
    result = _audit(tmp_path, manuscript, registry, claims)
    assert not any("exploratory" in warning for warning in result["warnings"]), result["warnings"]


def test_hedge_is_matched_across_a_line_break(tmp_path: Path):
    """The manuscript is hard-wrapped, so markers split across lines.

    Matching without collapsing whitespace warns on correctly hedged prose.
    """
    registry = _registry(tmp_path)
    manuscript = _benchmark_manuscript(
        tmp_path,
        "## Results\n\nThe method reached 3 of 3 loci [RESULT:GOOD] and was not\nsignificant.\n",
    )
    claims = _claims(tmp_path, "C1\tbenchmark\tResults\tWrapped\texploratory\tGOOD\tretain")
    result = _audit(tmp_path, manuscript, registry, claims)
    assert not any("exploratory" in warning for warning in result["warnings"]), result["warnings"]


def test_supported_claim_may_cite_a_non_registry_evidence_source(tmp_path: Path):
    """Not every supported claim is a measured result with a registry row.

    A statement about the software, or a diagnosis recorded outside the registry,
    is evidenced by a file rather than by a row.
    """
    registry = _registry(tmp_path)
    (tmp_path / "DIAGNOSIS.md").write_text("evidence\n", encoding="utf-8")
    manuscript = _benchmark_manuscript(tmp_path, "## Results\n\nA design property holds.\n")
    claims = _claims(
        tmp_path,
        "C1\tbenchmark\tResults\tDesign\tsupported\t\tDIAGNOSIS.md\tretain",
        header_extra="\tevidence_source",
    )
    result = _audit(tmp_path, manuscript, registry, claims)
    assert not any("cites neither" in warning for warning in result["warnings"]), result["warnings"]
    assert result["failures"] == []


def test_supported_claim_warns_without_any_evidence(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript = _benchmark_manuscript(tmp_path, "## Results\n\nA bare assertion.\n")
    claims = _claims(tmp_path, "C1\tbenchmark\tResults\tBare\tsupported\t\tretain")
    result = _audit(tmp_path, manuscript, registry, claims)
    assert any("cites neither" in warning for warning in result["warnings"]), result["warnings"]


def test_missing_evidence_source_file_is_a_failure(tmp_path: Path):
    """An evidence source must exist, or the escape hatch becomes free text."""
    registry = _registry(tmp_path)
    manuscript = _benchmark_manuscript(tmp_path, "## Results\n\nA design property holds.\n")
    claims = _claims(
        tmp_path,
        "C1\tbenchmark\tResults\tDesign\tsupported\t\tno_such_file.md\tretain",
        header_extra="\tevidence_source",
    )
    result = _audit(tmp_path, manuscript, registry, claims)
    assert any("missing evidence source" in failure for failure in result["failures"]), \
        result["failures"]


def test_manuscript_rejects_placeholder_and_invalid_wgs_number(tmp_path: Path):
    registry = _registry(tmp_path)
    manuscript = tmp_path / "source.md"
    manuscript.write_text("[AUTHOR: confirm] WGS was 0.399 and 0.494. [RESULT:BAD]\n", encoding="utf-8")
    claims = tmp_path / "claims.tsv"
    claims.write_text(
        "claim_id\tdraft\tsection\tclaim\tstatus\tevidence_result_id\taction\n"
        "C1\tsource_original\tResults\tbad\tremove\tBAD\tremove\n",
        encoding="utf-8",
    )
    result = audit_claims(str(manuscript), str(registry), str(claims), str(tmp_path / "audit.json"), str(tmp_path))
    assert result["submission_ready"] is False
    assert any("invalid-WGS" in failure for failure in result["failures"])


def _abstract_audit(tmp_path: Path, abstract: str, numbers_allowed: bool) -> dict:
    registry = _registry(tmp_path)
    (tmp_path / "decisions").mkdir()
    (tmp_path / "decisions" / "publication_route.json").write_text(
        json.dumps({"abstract_numeric_performance_allowed": numbers_allowed}), encoding="utf-8")
    manuscript_dir = tmp_path / "benchmark"
    manuscript_dir.mkdir()
    manuscript = manuscript_dir / "manuscript.md"
    manuscript.write_text(f"# Title\n\n## Abstract\n\n{abstract}\n\n## Introduction\n\nText.\n",
                          encoding="utf-8")
    claims = tmp_path / "claims.tsv"
    claims.write_text(
        "claim_id\tdraft\tsection\tclaim\tstatus\tevidence_result_id\taction\n"
        "C1\tbenchmark\tResults\tVerified\tsupported\tGOOD\tretain\n",
        encoding="utf-8",
    )
    return audit_claims(str(manuscript), str(registry), str(claims),
                        str(tmp_path / "audit.json"), str(tmp_path))


def test_abstract_without_numbers_passes_when_numbers_are_not_allowed(tmp_path: Path):
    result = _abstract_audit(tmp_path, "153 WES loci from 63 subjects were scored.", False)
    assert not any("abstract" in failure for failure in result["failures"])


def test_abstract_numbers_fail_when_the_route_forbids_them(tmp_path: Path):
    result = _abstract_audit(tmp_path, "Concordance was 143/153 (93.5%), phi 0.16.", False)
    failure = next(f for f in result["failures"] if "numeric performance" in f)
    assert "143/153" in failure and "93.5" in failure and ".16" in failure


def test_abstract_numbers_pass_when_the_route_allows_them(tmp_path: Path):
    result = _abstract_audit(tmp_path, "Concordance was 143/153 (93.5%).", True)
    assert not any("numeric performance" in failure for failure in result["failures"])


def test_abstract_may_cite_only_abstract_allowed_results(tmp_path: Path):
    result = _abstract_audit(tmp_path, "See [RESULT:GOOD].", True)
    assert "abstract cites a result not allowed in the abstract: GOOD" in result["failures"]
