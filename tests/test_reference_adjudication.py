"""Second-typing adjudication (decisions/20261009_reference_adjudication.json)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import adjudicate_reference_discordance as adjudicate  # noqa: E402

HEADER = ("Region\tPopulation\tSample ID\tHLA-A 1\tHLA-A 2\tHLA-B 1\tHLA-B 2\t"
          "HLA-C 1\tHLA-C 2\tHLA-DQB1 1\tHLA-DQB1 2\tHLA-DRB1 1\tHLA-DRB1 2\n")


def write_typing(path: Path, rows: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(HEADER + "".join(rows))


def test_second_typing_keeps_only_development_subjects(tmp_path, monkeypatch):
    path = tmp_path / "typing.txt"
    write_typing(path, [
        "EUR\tGBR\tDEV1\t01:01\t02:01:01\t07:02\t08:01\t07:01\t07:02\t-\t-\t-\t-\n",
        "EUR\tGBR\tEXT1\t03:01\t11:01\t35:01\t44:02\t04:01\t05:01\t-\t-\t-\t-\n",
        "EUR\tGBR\tDEV2\t01:01\t\t07:02\t08:01\t07:01\t07:02\t-\t-\t-\t-\n",
    ])
    monkeypatch.setattr(adjudicate, "SECOND_SHA256", adjudicate.sha256(path))
    typing = adjudicate.load_second_typing(path, {"DEV1", "DEV2"})
    assert {subject for subject, _ in typing} == {"DEV1", "DEV2"}
    # Three fields are reduced to two; a blank allele makes the locus unavailable.
    assert typing[("DEV1", "A")] == ("A*01:01", "A*02:01")
    assert typing[("DEV2", "A")] is None
    assert typing[("DEV2", "B")] == ("B*07:02", "B*08:01")


def test_second_typing_checksum_is_enforced(tmp_path):
    path = tmp_path / "typing.txt"
    write_typing(path, [])
    with pytest.raises(SystemExit, match="checksum mismatch"):
        adjudicate.load_second_typing(path, set())


def test_unparseable_values_are_unavailable():
    assert adjudicate._allele("A", "02:01") == "A*02:01"
    assert adjudicate._allele("A", "02:01:01:02") == "A*02:01"
    for value in ("", "-", "02", "02:XX", "02:01/02:02"):
        assert adjudicate._allele("A", value) is None


class StubReference:
    groups = {
        "G": {
            "C*02:02": {"C*02:02:01G"}, "C*02:10": {"C*02:02:01G"},
            "C*06:02": {"C*06:02:01G"}, "C*07:01": {"C*07:01:01G"},
        },
        "P": {
            "C*02:02": {"C*02:02P"}, "C*02:10": {"C*02:02P"},
            "C*06:02": {"C*06:02P"}, "C*07:01": {"C*07:01P"},
        },
    }

    def groups_for_two_field(self, allele, kind):
        return frozenset(self.groups[kind].get(allele, ()))


def test_g_equivalence_pairs_alleles_in_either_order():
    reference = StubReference()
    assert adjudicate.g_equivalent(reference, ("C*02:10", "C*06:02"), ("C*02:02", "C*06:02"))
    assert adjudicate.g_equivalent(reference, ("C*06:02", "C*02:10"), ("C*02:02", "C*06:02"))
    assert not adjudicate.g_equivalent(reference, ("C*02:10", "C*07:01"), ("C*02:02", "C*06:02"))
    # Both consensus alleles may not claim the same reference allele.
    assert not adjudicate.g_equivalent(reference, ("C*02:10", "C*02:02"), ("C*02:02", "C*06:02"))


def test_official_p_group_equivalence_pairs_alleles_bijectively():
    reference = StubReference()
    assert adjudicate.p_group_equivalent(
        reference, ("C*02:10", "C*06:02"), ("C*02:02", "C*06:02")
    )
    assert not adjudicate.p_group_equivalent(
        reference, ("C*02:10", "C*07:01"), ("C*02:02", "C*06:02")
    )
