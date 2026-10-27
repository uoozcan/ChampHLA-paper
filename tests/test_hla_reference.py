from pathlib import Path

import pytest

from champhla_confirmation.hla_reference import HLAReference
from champhla_confirmation.io import normalize_allele, normalize_diploid_call
from champhla_confirmation.schema import normalize_caller_row


def _reference(tmp_path: Path) -> HLAReference:
    allele = tmp_path / "Allelelist.txt"
    allele.write_text(
        "AlleleID,Allele\nHLA00001,A*01:01:01:01\nHLA00002,A*02:01:01\n"
        "HLA00003,A*03:01:01N\n",
        encoding="utf-8",
    )
    deleted = tmp_path / "Deleted_alleles.txt"
    deleted.write_text(
        "AlleleID,Allele,Description\nHLA99999,A*02:99,Sequence renamed A*02:01:01\n",
        encoding="utf-8",
    )
    p_groups = tmp_path / "hla_nom_p.txt"
    p_groups.write_text(
        "# version: 3.65.0\nA*;01:01P;01:01:01:01\n"
        "A*;02:99P;01:01:01:01/02:01:01\n",
        encoding="utf-8",
    )
    g_groups = tmp_path / "hla_nom_g.txt"
    g_groups.write_text("# version: 3.65.0\nA*;02:01:01G;02:01:01\n", encoding="utf-8")
    return HLAReference.from_files(
        "3.65.0", allele, deleted_alleles=deleted,
        p_groups=p_groups, g_groups=g_groups,
    )


def test_release_backed_current_expression_and_deleted_mapping(tmp_path):
    reference = _reference(tmp_path)
    current = normalize_allele("HLA-A*03:01:01N", "A", reference)
    assert current.two_field == "A*03:01"
    assert current.suffix == "N"
    assert current.membership_status == "current_release"
    renamed = normalize_allele("A*02:99", "A", reference)
    assert renamed.two_field == "A*02:01"
    assert renamed.membership_status == "deleted_or_renamed"
    assert renamed.mapping_status == "mapped_to_current"


def test_groups_are_not_expression_suffixes(tmp_path):
    reference = _reference(tmp_path)
    unique = normalize_allele("A*01:01P", "A", reference)
    assert unique.designation_type == "p_group"
    assert unique.two_field == "A*01:01"
    with pytest.raises(ValueError, match="group designation"):
        normalize_allele("A*02:99P", "A", reference)


def test_unknown_release_allele_is_invalid_and_traceable(tmp_path):
    reference = _reference(tmp_path)
    result = normalize_diploid_call("A*01:01", "A*88:88", "A", reference=reference)
    assert result["call_status"] == "invalid"
    assert "absent from IPD-IMGT/HLA 3.65.0" in result["no_call_reason"]

    row = normalize_caller_row({
        "subject": "S1", "modality": "wes", "gene": "A", "caller": "Tool",
        "allele1": "A*01:01", "allele2": "A*02:01",
        "container_digest": "sha256:abc", "source_sha256": "def",
    }, reference=reference)
    assert row["original_allele1"] == "A*01:01"
    assert row["normalization_release"] == "3.65.0"
    assert row["allele1_membership_status"] == "current_release"
