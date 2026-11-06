"""The combined shareable rendering.

These tests exist because the review drafts that ``submission.py`` builds fail
most of them: the sentinel comments, the literal carets and the lost italics are
all real defects of the committed binaries, verified before this module was
written. Several assertions below are therefore regression tests against a
rendering that once shipped, not hypotheticals.
"""
import re
from pathlib import Path

import pytest

from champhla_recovery.drive_document import (OUTSTANDING, Segment,
                                              parse_markdown,
                                              render_combined_docx, tokenize)

docx = pytest.importorskip("docx", reason="needs the documents extra")

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "manuscripts" / "benchmark"
MANUSCRIPT = BENCHMARK / "manuscript.md"
SUPPLEMENTARY = BENCHMARK / "supplementary.md"
FIGURES = ROOT / "figures"
PNG_1x1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082")


def _md(tmp_path: Path, body: str, name: str = "manuscript.md") -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def _runs(path: Path):
    document = docx.Document(str(path))
    for paragraph in document.paragraphs:
        for run in paragraph.runs:
            yield paragraph, run
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        yield paragraph, run


def _text(path: Path) -> str:
    return " ".join(run.text for _, run in _runs(path))


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> Path:
    """The real document, rendered once from the real sources."""
    if not (MANUSCRIPT.is_file() and SUPPLEMENTARY.is_file()):
        pytest.skip("manuscript sources not present")
    out = tmp_path_factory.mktemp("drive") / "combined.docx"
    render_combined_docx(MANUSCRIPT, out, supplementary_path=SUPPLEMENTARY,
                         figures_dir=FIGURES,
                         header_note=["REVIEW DRAFT - NOT FOR SUBMISSION."])
    return out


# --- inline formatting ----------------------------------------------------

def test_tokenizer_keeps_bold_and_italic_apart():
    assert tokenize("**bold** and *italic*") == [
        Segment("bold", bold=True), Segment(" and "), Segment("italic", italic=True)]


def test_tokenizer_reads_a_bold_caption_lead_in_not_two_italics():
    """The opening ** of a caption must never be taken as an italic delimiter."""
    segments = tokenize("**Figure 2. Performance.** Bars are cluster-*t* intervals.")
    assert segments[0] == Segment("Figure 2. Performance.", bold=True)
    assert Segment("t", italic=True) in segments


def test_tokenizer_handles_a_bold_span_that_wrapped_across_lines():
    """Captions wrap, so the tokenizer runs after the paragraph is joined."""
    assert tokenize("**Figure 1. A title that\nwrapped.** Body.")[0].bold


def test_superscripts_become_runs_not_carets():
    assert tokenize("Ozcan^1^") == [Segment("Ozcan"), Segment("1", sup=True)]


# --- block parsing --------------------------------------------------------

def test_generated_table_sentinels_are_dropped(tmp_path: Path):
    """The committed review drafts leak 26 of these as visible body text."""
    source = _md(tmp_path, "# T\n\n<!-- BEGIN GENERATED MAIN TABLE -->\n"
                           "**Table 1. Caption.** Body.\n"
                           "<!-- END GENERATED MAIN TABLE -->\n")
    out = tmp_path / "o.docx"
    render_combined_docx(source, out)
    text = _text(out)
    assert "GENERATED" not in text
    assert "<!--" not in text
    assert "Table 1. Caption." in text, "dropping the sentinel must not eat the caption"


def test_a_sentinel_does_not_glue_itself_to_the_following_caption(tmp_path: Path):
    """In the shipped draft the Table 1 caption is prefixed by the comment."""
    source = _md(tmp_path, "# T\n\n<!-- BEGIN GENERATED MAIN TABLE -->\n**Table 1. C.** B.\n")
    blocks = parse_markdown(source)
    assert [b.text for b in blocks if b.kind == "paragraph"] == ["**Table 1. C.** B."]


def test_separator_row_is_not_a_row(tmp_path: Path):
    source = _md(tmp_path, "# T\n\n| A | B |\n|---|---|\n| 1 | 2 |\n")
    out = tmp_path / "o.docx"
    render_combined_docx(source, out)
    assert len(docx.Document(str(out)).tables[0].rows) == 2


def test_supplementary_headings_are_demoted(tmp_path: Path):
    source = _md(tmp_path, "# Supplement\n\n## S1. Audit\n\n### Detail\n", "s.md")
    blocks = parse_markdown(source, level_offset=1)
    assert [(b.level, b.text) for b in blocks if b.kind == "heading"] == [
        (2, "Supplement"), (3, "S1. Audit"), (4, "Detail")]


# --- figures --------------------------------------------------------------

def test_figure_is_embedded_above_its_caption(tmp_path: Path):
    figures = tmp_path / "figures"
    figures.mkdir()
    (figures / "figure2_primary_performance.png").write_bytes(PNG_1x1)
    source = _md(tmp_path, "# T\n\n**Figure 2. Performance.** Caption body.\n")
    out = tmp_path / "o.docx"
    result = render_combined_docx(source, out, figures_dir=figures)
    assert result["figures_embedded"] == 1
    paragraphs = [p.text for p in docx.Document(str(out)).paragraphs]
    caption = next(i for i, t in enumerate(paragraphs) if "Figure 2. Performance." in t)
    assert docx.Document(str(out)).paragraphs[caption].style.name == "Caption"
    assert caption > 0


def test_a_missing_figure_stays_a_paragraph(tmp_path: Path):
    figures = tmp_path / "figures"
    figures.mkdir()
    source = _md(tmp_path, "# T\n\n**Figure 9. Absent.** Caption body.\n")
    out = tmp_path / "o.docx"
    assert render_combined_docx(source, out, figures_dir=figures)["figures_embedded"] == 0
    assert "Figure 9. Absent." in _text(out)


# --- outstanding author input --------------------------------------------

def test_outstanding_markers_are_kept_and_highlighted(tmp_path: Path):
    """Preserved for the same reason submission.py preserves them, and flagged
    so a co-author can see at a glance what is still owed."""
    source = _md(tmp_path, "# T\n\nIkonen^TO CONFIRM^\n\n"
                           "**AUTHOR INPUT REQUIRED BEFORE SUBMISSION:** ORCIDs.\n")
    out = tmp_path / "o.docx"
    render_combined_docx(source, out)
    highlighted = [run.text for _, run in _runs(out)
                   if run.font.highlight_color is not None]
    assert any("TO CONFIRM" in text for text in highlighted)
    assert any("AUTHOR INPUT REQUIRED" in text for text in highlighted)


# --- the real document ----------------------------------------------------

def test_no_provenance_tags_or_sentinels_survive(built: Path):
    text = _text(built)
    assert "[RESULT:" not in text
    assert "GENERATED" not in text
    assert "<!--" not in text


def test_no_literal_carets_survive(built: Path):
    """The main review draft carries 14 of these."""
    assert "^" not in _text(built)


def test_escaped_asterisks_render_as_allele_names(built: Path, tmp_path: Path):
    r"""PSR-036: ``HLA-B\*57:01`` used to render as ``HLA-B\57:01``."""
    text = _text(built)
    assert "HLA-B*57:01" in text
    # Shell line continuations in code blocks are a backslash before a space.
    assert not re.search(r"\\(?=[A-Za-z0-9*])", text)
    # Exercise the tool-name case without requiring an unused tool in the paper.
    source = _md(tmp_path, "# T\n\n" + r"HLA-B\*57:01 and HLA\*LA." + "\n")
    out = tmp_path / "escaped.docx"
    render_combined_docx(source, out)
    sample_text = _text(out)
    assert "HLA-B*57:01 and HLA*LA." in sample_text
    assert not re.search(r"\\(?=[A-Za-z0-9*])", sample_text)


def test_tokenize_keeps_escaped_asterisks_literal():
    segments = tokenize(r"HLA-B\*57:01 and *p*")
    assert [(s.text, s.italic) for s in segments] == [("HLA-B*57:01 and ", False), ("p", True)]


def test_tokenize_protects_unescaped_generated_table_alleles():
    segments = tokenize("C*03:04+C*03:04 and A*02; *p*=0.2")
    assert "".join(segment.text for segment in segments) == "C*03:04+C*03:04 and A*02; p=0.2"
    assert [segment.text for segment in segments if segment.italic] == ["p"]


def test_no_rendered_allele_loses_its_asterisk(built: Path):
    text = _text(built)
    malformed = re.findall(r"(?<!HLA-)\b[ABC]\d{2}(?=:\d{2}|[/+\s,;])|HLA-[ABC]\d{2}(?=:\d{2})", text)
    assert malformed == [], f"allele-like strings lost their asterisk: {sorted(set(malformed))}"


def test_unconfirmed_author_metadata_is_kept_outside_the_reader_copy(built: Path):
    text = _text(built)
    assert "PROVISIONAL" not in text and "TO CONFIRM BEFORE SUBMISSION" not in text
    path = ROOT / "AUTHOR_FIELDS_TO_COMPLETE.md"
    if not path.is_file():  # held back from the public snapshot (publish_snapshot.sh)
        return
    checklist = path.read_text(encoding="utf-8")
    assert "PROVISIONAL AUTHOR METADATA" in checklist
    assert "TO CONFIRM BEFORE SUBMISSION" in checklist


def test_every_outstanding_marker_is_highlighted(built: Path):
    for _, run in _runs(built):
        if any(marker in run.text for marker in OUTSTANDING):
            assert run.font.highlight_color is not None, run.text[:60]


def test_main_figures_sit_after_the_paragraph_that_cites_them(built: Path):
    """Tanoli, 2026-10-05: "place all figures and tables directly in text".

    Only the main text is inlined. The supplement keeps its collected legends
    because S1-S4 are cited from the main text, not from inside the supplement.
    """
    paragraphs = [p.text.strip() for p in docx.Document(str(built)).paragraphs]
    for number in ("1", "2", "3", "4"):
        legend = next(i for i, t in enumerate(paragraphs)
                      if t.startswith(f"Figure {number}."))
        citation = next(
            (i for i, t in enumerate(paragraphs)
             if i != legend and re.search(rf"\bFigures?\s+{number}[A-Z]?\b", t)),
            None)
        assert citation is not None, f"Figure {number} is never cited"
        assert citation < legend, f"Figure {number} precedes the text citing it"


def test_the_emptied_figure_legends_heading_is_dropped(built: Path):
    headings = [p.text.strip().lower() for p in docx.Document(str(built)).paragraphs
                if p.style.name.startswith("Heading")]
    assert "figure legends" not in headings


def test_inlining_is_optional_and_off_leaves_legends_collected(tmp_path: Path):
    output = tmp_path / "collected.docx"
    result = render_combined_docx(
        MANUSCRIPT, output, supplementary_path=SUPPLEMENTARY,
        figures_dir=FIGURES, inline_figures=False)
    assert result["figures_embedded"] == 10
    headings = [p.text.strip().lower() for p in docx.Document(str(output)).paragraphs
                if p.style.name.startswith("Heading")]
    assert "figure legends" in headings


def test_all_ten_figures_are_embedded_in_order(built: Path):
    result = docx.Document(str(built))
    captions = [p.text for p in result.paragraphs if p.style.name == "Caption"]
    assert len(captions) == 10
    expected = ["Figure 1.", "Figure 2.", "Figure 3.", "Figure 4.",
                "Supplementary Figure S1.", "Supplementary Figure S2.",
                "Supplementary Figure S3.", "Supplementary Figure S4.",
                "Supplementary Figure S5.", "Supplementary Figure S6."]
    for caption, prefix in zip(captions, expected):
        assert caption.startswith(prefix), caption[:60]


def test_every_table_renders(built: Path):
    """Includes the non-scientific historical-material disposition table.

    Two main-text tables (callers, performance) plus thirty-five supplementary
    tables, including the two S1 truth-selection tables, the S2
    singleton-sensitivity table, the S3 family-sensitivity table, the S7
    adjudication, reference-agreement (concordance, error phi and vote
    correction) and power tables, the consolidated S9 aggregate table, the two
    S11 workflow tables and the four S12 tables. The legacy NCI-60 table was withdrawn
    (decisions/20261009_nci60_estimates_withdrawn.json).
    """
    tables = docx.Document(str(built)).tables
    # plus the three S10 v3.5.0 rerun tables (caller task states, stored-to-rerun
    # cells, truth-free character of the changed cells)
    rerun = (ROOT / "provenance/development_rerun_v350/truth_free_collection").is_dir()
    # decisions/20261105_patient_cohorts_removed.json removed the four S9 cohort tables;
    # decisions/20261106_roihu_descriptions_round5.json added Tables S10.4-S10.6.
    assert len(tables) == (48 if rerun else 45)
    # the performance table gains the corrected-reference column on rerun inputs; Table 1
    # gained the study-run version and settings column (round 5, R1)
    assert sorted(len(table.columns) for table in tables[:2]) == ([6, 9] if rerun else [6, 8])
    assert max(len(t.columns) for t in tables) == 13


def test_wide_tables_are_pinned_to_the_measure(built: Path):
    """A 13-column table at 6.5in would otherwise run off the page."""
    for table in docx.Document(str(built)).tables:
        assert table._tbl.tblPr.find(
            "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblW"
        ) is not None


def test_references_are_numbered_and_p_stays_italic(built: Path):
    italics = {run.text for _, run in _runs(built) if run.italic}
    assert "p" in italics, "the statistical p must stay italic"
    texts = [p.text for p in docx.Document(str(built)).paragraphs]
    assert any(text.startswith("1. Trowsdale J, Knight JC.") for text in texts)


def test_the_outline_has_one_title_and_a_supplementary_appendix(built: Path):
    result = docx.Document(str(built))
    titles = [p.text for p in result.paragraphs if p.style.name == "Title"]
    assert len(titles) == 1, "a second Title would split the document outline"
    assert titles[0].startswith("An auditable plurality vote for HLA class I")
    headings = [p.text for p in result.paragraphs if p.style.name == "Heading 1"]
    assert "Appendix: Supplementary material" in headings
    # The supplement's own top heading IS the appendix heading, renamed. A bare
    # "Supplementary material" alongside it would be a duplicate.
    assert "Supplementary material" not in headings
    assert "S1. Cohort and reference-source audit" in [
        p.text for p in result.paragraphs if p.style.name == "Heading 2"]


def test_contents_field_follows_the_front_matter(built: Path):
    result = docx.Document(str(built))
    texts = [p.text for p in result.paragraphs]
    assert "Contents" in texts
    assert texts.index("Contents") < texts.index("Introduction")
    assert texts.index("Abstract") < texts.index("Contents")


def test_render_is_deterministic(tmp_path: Path):
    """python-docx stamps the clock into the archive; _normalize undoes that."""
    source = _md(tmp_path, "# T\n\nBody paragraph.\n")
    first = render_combined_docx(source, tmp_path / "a.docx")["sha256"]
    second = render_combined_docx(source, tmp_path / "b.docx")["sha256"]
    assert first == second


def test_a_preface_renders_first_on_its_own_page(tmp_path: Path):
    source = _md(tmp_path, "# Paper\n\n## Abstract\n\nAbstract text.\n")
    preface = _md(tmp_path, "## Changes since v2\n\n- One change.\n", name="preface.md")
    out = tmp_path / "p.docx"
    render_combined_docx(source, out, preface_path=preface)
    result = docx.Document(str(out))
    texts = [p.text for p in result.paragraphs]
    assert texts.index("Changes since v2") < texts.index("Paper") < texts.index("Abstract")
    assert [p.text for p in result.paragraphs if p.style.name == "Title"] == ["Paper"]
    assert 'w:type="page"' in result.element.body.xml


def test_without_a_preface_the_rendering_is_unchanged(tmp_path: Path):
    source = _md(tmp_path, "# T\n\nBody paragraph.\n")
    plain = render_combined_docx(source, tmp_path / "a.docx")["sha256"]
    explicit = render_combined_docx(source, tmp_path / "b.docx", preface_path=None)["sha256"]
    assert plain == explicit


def test_a_preface_may_not_carry_tables(tmp_path: Path):
    source = _md(tmp_path, "# T\n\nBody.\n")
    preface = _md(tmp_path, "## P\n\n| a |\n|---|\n| 1 |\n", name="preface.md")
    with pytest.raises(ValueError, match="tables or figures"):
        render_combined_docx(source, tmp_path / "x.docx", preface_path=preface)


def test_panel_citations_count_as_citing_the_figure():
    from champhla_recovery.drive_document import _citation_pattern
    main1 = _citation_pattern(False, "1")
    assert main1.search("as shown (Figure 1A).")
    assert main1.search("see Figure 1.")
    assert not main1.search("see Figure 10.")
    assert not main1.search("see Figure S1.")
    assert _citation_pattern(True, "5").search("(Supplementary Figure S5)")


def test_wide_tables_have_landscape_pages_and_remain_distinct(tmp_path: Path):
    source = _md(tmp_path, "# T\n\n" + "| " + " | ".join("ABCDEFGH") + " |\n" +
                 "|" + "---|" * 8 + "\n| " + " | ".join("12345678") + " |\n\n" +
                 "| A | B |\n|---|---|\n| 1 | 2 |\n")
    out = tmp_path / "tables.docx"
    render_combined_docx(source, out)
    document = docx.Document(str(out))
    assert len(document.tables) == 2
    assert any(section.page_width > section.page_height for section in document.sections)
    body = list(document.element.body)
    assert not any(left.tag.endswith("}tbl") and right.tag.endswith("}tbl")
                   for left, right in zip(body, body[1:]))


def test_wrapped_bullet_sentences_remain_one_formatted_paragraph(tmp_path: Path):
    source = _md(tmp_path, "# T\n\n- **One finding.** This sentence continues\n"
                           "on the next source line.\n\nA separate paragraph.\n")
    blocks = parse_markdown(source)
    assert [(block.kind, block.text) for block in blocks[1:]] == [
        ("bullet", "**One finding.** This sentence continues on the next source line."),
        ("paragraph", "A separate paragraph.")]
    out = tmp_path / "bullets.docx"
    render_combined_docx(source, out)
    paragraphs = docx.Document(str(out)).paragraphs
    assert any(paragraph.style.name == "List Bullet" and paragraph.text.endswith("next source line.")
               for paragraph in paragraphs)
