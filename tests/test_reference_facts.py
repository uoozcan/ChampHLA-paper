"""Facts the manuscript states about pinned resources, checked against the resource,
and the numbered (Vancouver) citation scheme BMC Bioinformatics requires."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscripts" / "benchmark" / "manuscript.md"
SUPPLEMENT = ROOT / "manuscripts" / "benchmark" / "supplementary.md"
ALLELES = ROOT / "resources" / "ipd_imgt_hla" / "3.65.0" / "Allelelist.txt"
CITATION = re.compile(r"\[(\d+(?:[–,]\s*\d+)*)\]")


def _split(path: Path) -> tuple[str, list[str]]:
    """Text outside the reference list, and the numbered entries in order."""
    text = path.read_text(encoding="utf-8")
    if "## References" not in text:
        return text, []
    before, rest = text.split("## References", 1)
    references, _, after = rest.partition("\n## ")
    entries = [" ".join(e.split()) for e in references.strip().split("\n\n")]
    return before + after, entries


def _cited(text: str) -> list[int]:
    numbers = []
    for group in CITATION.findall(text):
        for part in re.split(r",\s*", group):
            first, _, last = part.partition("–")
            numbers.extend(range(int(first), int(last or first) + 1))
    return numbers


def test_stated_allele_count_matches_the_pinned_release():
    rows = [line for line in ALLELES.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#") and not line.startswith("AlleleID")]
    excluded = {"MICA", "MICB", "TAP1", "TAP2", "HFE"}
    hla_rows = [line for line in rows if line.split(",", 1)[1].split("*", 1)[0] not in excluded]
    text = " ".join(MANUSCRIPT.read_text(encoding="utf-8").split())
    match = re.search(
        r"release 3\.65\.0 .*? contains ([\d,]+) HLA allele designations .*?"
        r"\(([\d,]+) entries when MICA, MICB, TAP1, TAP2 and HFE are included\)",
        text,
    )
    assert match, "allele-count sentence not found"
    assert int(match.group(1).replace(",", "")) == len(hla_rows) == 45_421
    assert int(match.group(2).replace(",", "")) == len(rows) == 46_652


def test_sr016_factual_corrections_and_primary_citations_are_present():
    text = " ".join(MANUSCRIPT.read_text(encoding="utf-8").split())
    assert "one of the most polymorphic regions" in text
    assert "carbamazepine-induced Stevens–Johnson syndrome" in text
    assert "typing-tool-specific errors" in text
    assert "C and A were retained as opaque suffix metadata" in text
    assert "POLYSOLVER publication reports IMGT/HLA 3.10" in text
    assert "HLA-HD demo manual" in text
    for name in ("Clopper CJ", "Li H. Aligning sequence reads", "Sequence Alignment/Map", "Kurtzer GM"):
        assert name in text
    for literature in ("nf-hlamajority", "SweHLA", "Thuesen NH", "Buchkovich ML"):
        assert literature in text


def test_main_references_are_numbered_in_order_of_first_citation():
    text, entries = _split(MANUSCRIPT)
    assert [int(e.split(".", 1)[0]) for e in entries] == list(range(1, len(entries) + 1))
    cited = _cited(text)
    first_seen = list(dict.fromkeys(cited))
    assert first_seen == list(range(1, len(entries) + 1)), "uncited, unknown or out-of-order reference"


def test_supplement_continues_main_reference_numbering():
    supplement_text, supplement_entries = _split(SUPPLEMENT)
    _, main_entries = _split(MANUSCRIPT)
    assert supplement_entries == []
    assert "continue the reference numbering of the main manuscript" in supplement_text
    citations = _cited(supplement_text)
    assert citations
    assert set(citations) <= set(range(1, len(main_entries) + 1))
    abi_rached = next(
        number for number, entry in enumerate(main_entries, start=1)
        if "Abi-Rached L" in entry
    )
    assert abi_rached in citations


@pytest.mark.parametrize("path", [MANUSCRIPT, SUPPLEMENT], ids=["main", "supplement"])
def test_no_author_year_citation_remains(path):
    text, _ = _split(path)
    flat = " ".join(text.split())
    assert not re.search(r"\*et al\.\*,? \(?\d{4}\)?|[A-Z][a-z]+(?: and [A-Z][a-z]+)?, (?:19|20)\d{2}\)",
                         flat)


def test_every_article_has_a_doi_and_every_web_resource_a_url():
    _, entries = _split(MANUSCRIPT)
    web = [e for e in entries if "http" in e]
    articles = [e for e in entries if "http" not in e]
    assert [e[:12] for e in articles if "doi:10." not in e] == []
    assert all(re.search(r"https://\S+", e) for e in web)
    # Public resources carry an access date; the two project repositories gain theirs at release.
    undated = [e for e in web if "Accessed" not in e]
    assert all("github.com/uoozcan/" in e for e in undated)
