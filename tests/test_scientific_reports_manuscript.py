"""Scientific Reports structure checks for the ChampHLA submission candidate."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscripts" / "benchmark" / "manuscript.md"


def _text() -> str:
    return MANUSCRIPT.read_text(encoding="utf-8")


def _between(text: str, start: str, end: str) -> str:
    return text.split(start, 1)[1].split(end, 1)[0]


def _words(text: str) -> list[str]:
    return re.findall(r"\b[\w*’'-]+\b", text, flags=re.UNICODE)


def _without_tables_or_tags(text: str) -> str:
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            continue
        if re.fullmatch(r"\[RESULT:[^]]+\]", stripped):
            continue
        if stripped.startswith("**Table "):
            continue
        if stripped.startswith("Concordance uses the fixed denominator"):
            continue
        kept.append(line)
    return "\n".join(kept)


def _expand_citation(expression: str) -> list[int]:
    numbers: list[int] = []
    for part in expression.split(","):
        token = part.strip()
        match = re.fullmatch(r"(\d+)[–-](\d+)", token)
        if match:
            numbers.extend(range(int(match.group(1)), int(match.group(2)) + 1))
        else:
            numbers.append(int(token))
    return numbers


def test_title_abstract_and_keywords_match_scientific_reports_limits() -> None:
    text = _text()
    title = text.splitlines()[0][2:]
    abstract = _between(text, "## Abstract", "## Keywords")
    keywords = [
        item.strip()
        for item in _between(text, "## Keywords", "## Introduction").split(";")
        if item.strip()
    ]

    assert len(_words(title)) <= 20
    assert len(_words(abstract)) <= 200
    assert not re.search(r"\*\*(Background|Results|Conclusions):\*\*", abstract)
    assert not re.search(r"\[[0-9][^]]*\]", abstract)
    assert len(keywords) <= 6


def test_required_section_order_and_bmc_headings_are_absent() -> None:
    text = _text()
    required = [
        "## Introduction",
        "## Methods",
        "## Results",
        "## Discussion",
        "## Data availability",
        "## Code availability",
        "## References",
        "## Figure legends",
        "## Supplementary information",
    ]
    positions = [text.index(heading) for heading in required]
    assert positions == sorted(positions)
    for forbidden in (
        "## Background",
        "## Declarations",
        "## Conclusions",
        "## Additional files",
        "### Consent for publication",
        "### Availability of data and materials",
    ):
        assert forbidden not in text


def test_main_text_and_display_item_limits() -> None:
    text = _text()
    introduction = _between(text, "## Introduction", "## Methods")
    results = _between(text, "## Results", "## Discussion")
    discussion = _between(text, "## Discussion", "## Data availability")
    main_text = "\n".join(
        _without_tables_or_tags(section)
        for section in (introduction, results, discussion)
    )
    displays = len(re.findall(r"^\*\*(?:Figure|Table) \d+\.", text, re.MULTILINE))

    assert len(_words(main_text)) <= 4500
    assert displays <= 8


def test_ethics_and_author_completion_are_honest_and_separate() -> None:
    text = _text()
    methods = _between(text, "## Methods", "## Results")
    assert "### Ethics and data reuse" in methods
    assert "No new participants were recruited" in methods
    assert "rather than clinical patients" in methods
    assert "controlled patient data" not in methods
    assert "PROVISIONAL" not in text and "TO CONFIRM" not in text
    assert "## Data availability" in text and "## Code availability" in text
    path = ROOT / "AUTHOR_FIELDS_TO_COMPLETE.md"
    if path.is_file():  # held back from the public snapshot (publish_snapshot.sh)
        checklist = path.read_text(encoding="utf-8")
        assert "Author contributions" in checklist and "Competing interests" in checklist
        assert "Funding" in checklist and "large language model" in checklist


def test_references_are_sequential_by_first_citation() -> None:
    text = _text()
    before_references = text.split("## References", 1)[0]
    citation_pattern = re.compile(
        r"\[([0-9]+(?:[–-][0-9]+)?(?:,\s*[0-9]+(?:[–-][0-9]+)?)*)\]"
    )
    first_seen: list[int] = []
    for match in citation_pattern.finditer(before_references):
        for number in _expand_citation(match.group(1)):
            if number not in first_seen:
                first_seen.append(number)

    reference_text = _between(text, "## References", "## Figure legends")
    listed = [int(value) for value in re.findall(r"^(\d+)\. ", reference_text, re.MULTILINE)]
    assert first_seen == list(range(1, len(first_seen) + 1))
    assert listed == list(range(1, len(listed) + 1))
    assert set(first_seen) == set(listed)
