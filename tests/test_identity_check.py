"""Sample-identity controls (decisions/20261008_identity_check_na07000.json)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from champhla_confirmation.development import _partition_by_identity, identity_check

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "development"


def row(subject: str, modality: str, gene: str = "A", caller: str = "OptiType",
        a1: str = "A*01:01", a2: str = "A*02:01") -> dict[str, str]:
    return {"cohort": "c", "subject": subject, "modality": modality, "gene": gene,
            "caller": caller, "allele1": a1, "allele2": a2, "call_status": "callable"}


def test_unmanifested_input_fails_closed_unless_recorded():
    admitted = {("S1", "wes")}
    excluded = {("S2", "rnaseq"): {"reason": "identity"}}
    kept, withheld = _partition_by_identity(
        [row("S1", "wes"), row("S2", "rnaseq")], admitted, excluded, "caller input")
    assert [r["subject"] for r in kept] == ["S1"]
    assert [r["subject"] for r in withheld] == ["S2"]
    with pytest.raises(ValueError, match="not in the official assay manifest"):
        _partition_by_identity([row("S3", "rnaseq")], admitted, excluded, "caller input")


def test_identity_check_counts_shared_alleles(tmp_path: Path):
    same = [row("S1", m, g, c, f"{g}*01:01", f"{g}*02:01")
            for m, callers in (("wes", ("OptiType", "POLYSOLVER")),
                               ("rnaseq", ("OptiType", "HLA-HD")))
            for c in callers for g in "ABC"]
    swapped = [row("S2", "wes", g, c, f"{g}*01:01", f"{g}*02:01")
               for c in ("OptiType", "POLYSOLVER") for g in "ABC"]
    swapped += [row("S2", "rnaseq", g, c, f"{g}*03:01", f"{g}*04:01")
                for c in ("OptiType", "HLA-HD") for g in "ABC"]
    calls = tmp_path / "calls.tsv"
    with calls.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(same[0]), delimiter="\t")
        writer.writeheader()
        writer.writerows(same + swapped)
    manifest = tmp_path / "manifest.tsv"
    manifest.write_text("sample_id\tmodality\nS1\twes\nS1\trnaseq\nS2\twes\n", encoding="utf-8")
    result = {r["subject"]: r for r in identity_check([str(calls)], str(manifest),
                                                       str(tmp_path / "identity.tsv"))}
    assert (result["S1"]["alleles_shared"], result["S1"]["alleles_compared"]) == ("6", "6")
    assert result["S2"]["alleles_shared"] == "0"
    assert result["S2"]["rnaseq_in_assay_manifest"] == "0"


def test_released_inputs_enforce_the_manifest_and_withhold_na07000_rnaseq():
    rerun_roster = ROOT / "cohorts" / "development_rerun_manifest.tsv"
    for directory in (DATA, DATA / "sensitivity_abstain"):
        manifest = json.loads((directory / "input_manifest.json").read_text(encoding="utf-8"))
        identity = manifest["identity_controls"]
        with (directory / "normalized_caller_calls.tsv").open(encoding="utf-8") as handle:
            kept = list(csv.DictReader(handle, delimiter="\t"))
        assert not any(r["subject"] == "NA07000" and r["modality"] == "rnaseq" for r in kept)
        assert any(r["subject"] == "NA07000" and r["modality"] == "wes" for r in kept)
        with (directory / "excluded_caller_calls.tsv").open(encoding="utf-8") as handle:
            withheld = list(csv.DictReader(handle, delimiter="\t"))
        if manifest.get("schema_version") == "champhla-development-rerun-inputs-1":
            # The v3.5.0 rerun applies the identity control upstream: the signed rerun
            # roster never schedules NA07000 RNA-seq, so nothing is left to withhold.
            assert identity["rerun_manifest_enforced"]
            with rerun_roster.open(encoding="utf-8") as handle:
                roster = {(r["sample_id"], r["modality"])
                          for r in csv.DictReader(handle, delimiter="\t")}
            assert ("NA07000", "rnaseq") not in roster and ("NA07000", "wes") in roster
            assert identity["excluded_subject_assays"] == [] and withheld == []
        else:
            assert identity["assay_manifest_enforced"]
            assert identity["excluded_subject_assays"] == ["NA07000:rnaseq"]
            assert {(r["subject"], r["modality"]) for r in withheld} == {("NA07000", "rnaseq")}


def test_empty_withheld_table_scores_nothing(tmp_path):
    from champhla_confirmation.development import CALLER_INPUT_FIELDS, withheld_input_effect
    from champhla_confirmation.io import write_tsv
    excluded = tmp_path / "excluded_caller_calls.tsv"
    write_tsv(excluded, [], CALLER_INPUT_FIELDS)
    out = tmp_path / "effect.tsv"
    # an empty table must never reach the truth loader
    assert withheld_input_effect(str(excluded), str(tmp_path / "absent_truth.txt"),
                                 str(tmp_path / "work"), str(out)) == []
    assert out.is_file()
