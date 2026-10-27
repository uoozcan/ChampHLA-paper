import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from champhla_recovery.submission import (NS, W, _qn, render_docx,
                                          validate_docx_parity)

ROOT = Path(__file__).resolve().parents[1]
PNG_1x1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4"
    "890000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082")


def _docx_text(path: Path) -> str:
    root = ET.fromstring(zipfile.ZipFile(path).read("word/document.xml"))
    return " ".join(node.text or "" for node in root.iter(_qn(W, "t")))


def _md(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "manuscript.md"
    path.write_text(body, encoding="utf-8")
    return path


def test_result_tags_are_stripped_from_the_rendering(tmp_path: Path):
    """They are provenance citations for the auditor, not prose for a reader."""
    source = _md(tmp_path, "# T\n\nThe vote was correct at 365 loci [RESULT:DEV_WES_CONSENSUS].\n")
    out = tmp_path / "o.docx"
    render_docx(source, out)
    text = _docx_text(out)
    assert "[RESULT:" not in text
    assert "365 loci." in text, "stripping must not eat the sentence around the tag"


def test_result_tags_can_be_kept(tmp_path: Path):
    source = _md(tmp_path, "# T\n\nCorrect at 365 loci [RESULT:DEV_WES_CONSENSUS].\n")
    out = tmp_path / "o.docx"
    render_docx(source, out, strip_result_tags=False)
    assert "[RESULT:DEV_WES_CONSENSUS]" in _docx_text(out)


def test_layout_meets_bmc_double_spacing_line_and_page_numbers(tmp_path: Path):
    source = _md(tmp_path, "# T\n\nBody text.\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")
    out = tmp_path / "o.docx"
    render_docx(source, out)
    archive = zipfile.ZipFile(out)
    document = ET.fromstring(archive.read("word/document.xml"))
    assert document.find(f".//{_qn(W, 'sectPr')}/{_qn(W, 'lnNumType')}") is not None
    assert b'instr="PAGE"' in archive.read("word/footer1.xml")
    styles = ET.fromstring(archive.read("word/styles.xml"))
    spacing = {style.get(_qn(W, "styleId")): style.find(f".//{_qn(W, 'spacing')}").get(_qn(W, "line"))
               for style in styles.iter(_qn(W, "style"))}
    assert spacing["Normal"] == "480" and spacing["TableText"] == "240"


def test_escaped_asterisks_render_as_allele_names(tmp_path: Path):
    """PSR-036: the italic stripper used to leave ``HLA-B\\57:01`` behind."""
    source = _md(tmp_path, r"# T" + "\n\n" + r"HLA-B\*57:01 and HLA\*LA, *p* value." + "\n")
    out = tmp_path / "o.docx"
    render_docx(source, out)
    text = _docx_text(out)
    assert "HLA-B*57:01 and HLA*LA, p value." in text
    assert chr(92) not in text
    assert validate_docx_parity(source, out)["text_parity"]


def test_placeholders_are_never_silently_removed(tmp_path: Path):
    """A draft exists to show the author what is outstanding.

    Quietly dropping TO CONFIRM would turn an unfinished manuscript into one that
    looks finished.
    """
    source = _md(tmp_path, "# T\n\nCorresponding author. TO CONFIRM - name and email.\n")
    out = tmp_path / "o.docx"
    render_docx(source, out)
    assert "TO CONFIRM" in _docx_text(out)


def test_affiliation_markers_render_as_superscripts_without_literal_carets(tmp_path: Path):
    source = _md(tmp_path, "# T\n\nAuthor One^1^, Author Two^1,3^\n")
    out = tmp_path / "o.docx"
    render_docx(source, out)
    root = ET.fromstring(zipfile.ZipFile(out).read("word/document.xml"))
    superscripts = []
    for run in root.findall(".//w:r", NS):
        align = run.find("w:rPr/w:vertAlign", NS)
        if align is not None and align.get(_qn(W, "val")) == "superscript":
            superscripts.append(
                "".join(node.text or "" for node in run.findall("w:t", NS)))
    assert superscripts == ["1", "1,3"]
    assert "^" not in _docx_text(out)
    assert validate_docx_parity(source, out)["text_parity"]


def test_figure_caption_embeds_its_png(tmp_path: Path):
    figures = tmp_path / "figures"
    figures.mkdir()
    (figures / "figure2_primary_performance.png").write_bytes(PNG_1x1)
    source = _md(tmp_path, "# T\n\n**Figure 2. Head to head.** Caption body.\n")
    out = tmp_path / "o.docx"
    result = render_docx(source, out, figures_dir=figures)
    assert result["figures_embedded"] == 1
    assert "word/media/image1.png" in zipfile.ZipFile(out).namelist()


def test_supplementary_figure_caption_embeds_its_png(tmp_path: Path):
    figures = tmp_path / "figures"
    figures.mkdir()
    (figures / "supplementary_figure_s3_support_profiles.png").write_bytes(PNG_1x1)
    source = _md(
        tmp_path,
        "# Supplement\n\n**Supplementary Figure S3. Support profiles.** Caption body.\n",
    )
    out = tmp_path / "o.docx"
    result = render_docx(source, out, figures_dir=figures)
    assert result["figures_embedded"] == 1
    assert "word/media/image1.png" in zipfile.ZipFile(out).namelist()


def test_caption_without_a_matching_file_stays_a_paragraph(tmp_path: Path):
    """A missing figure must not fail the render of a draft, nor invent an image."""
    figures = tmp_path / "figures"
    figures.mkdir()
    source = _md(tmp_path, "# T\n\n**Figure 9. Absent.** Caption body.\n")
    out = tmp_path / "o.docx"
    result = render_docx(source, out, figures_dir=figures)
    assert result["figures_embedded"] == 0
    assert "Figure 9. Absent." in _docx_text(out)


def test_non_png_figure_is_refused(tmp_path: Path):
    figures = tmp_path / "figures"
    figures.mkdir()
    (figures / "figure1_x.png").write_bytes(b"not a png at all, just bytes" * 2)
    source = _md(tmp_path, "# T\n\n**Figure 1. Bad.** Caption.\n")
    with pytest.raises(ValueError, match="PNG"):
        render_docx(source, tmp_path / "o.docx", figures_dir=figures)


def test_tables_survive_with_their_separator_row_removed(tmp_path: Path):
    source = _md(tmp_path, "# T\n\n| A | B |\n|---|---|\n| 1 | 2 |\n")
    out = tmp_path / "o.docx"
    render_docx(source, out)
    root = ET.fromstring(zipfile.ZipFile(out).read("word/document.xml"))
    rows = list(list(root.iter(_qn(W, "tbl")))[0].findall("w:tr", NS))
    assert len(rows) == 2, "header plus one data row; the |---| separator is not a row"


def test_parity_detects_a_docx_that_no_longer_matches(tmp_path: Path):
    """The check has to be able to fail, or it is decoration."""
    source = _md(tmp_path, "# T\n\nOriginal sentence.\n")
    out = tmp_path / "o.docx"
    render_docx(source, out)
    assert validate_docx_parity(source, out)["text_parity"]
    source.write_text("# T\n\nA different sentence entirely.\n", encoding="utf-8")
    report = validate_docx_parity(source, out)
    assert not report["text_parity"]
    assert any("diverge at block" in f for f in report["failures"])


def test_header_note_is_not_counted_as_manuscript_content(tmp_path: Path):
    """The notice is added at render time, so parity must ignore it."""
    source = _md(tmp_path, "# T\n\nBody.\n")
    out = tmp_path / "o.docx"
    render_docx(source, out, header_note=["DRAFT - NOT FOR SUBMISSION."])
    assert "DRAFT - NOT FOR SUBMISSION." in _docx_text(out)
    assert validate_docx_parity(source, out)["text_parity"]


def test_render_is_deterministic(tmp_path: Path):
    """Same input, same bytes -- so a rebuild is diffable and checksummable."""
    source = _md(tmp_path, "# T\n\nBody paragraph.\n")
    first = render_docx(source, tmp_path / "a.docx")["sha256"]
    second = render_docx(source, tmp_path / "b.docx")["sha256"]
    assert first == second


def test_committed_review_draft_matches_the_manuscript():
    """The circulated draft must not drift from the source it claims to render."""
    docx = ROOT / "manuscripts" / "benchmark" / "ChampHLA_manuscript_REVIEW_DRAFT.docx"
    if not docx.is_file():
        pytest.skip("no review draft committed")
    report = validate_docx_parity(ROOT / "manuscripts" / "benchmark" / "manuscript.md",
                                  docx, figures_dir=ROOT / "figures")
    assert report["failures"] == [], report["failures"]
    text = _docx_text(docx)
    assert not re.search(r"\[RESULT:[A-Z]", text), "provenance tags leaked into the draft"
    assert "NOT FOR SUBMISSION" in text, "a draft must say that it is one"


def test_committed_supplementary_draft_matches_and_embeds_all_figures():
    docx = ROOT / "manuscripts" / "benchmark" / "ChampHLA_supplementary_REVIEW_DRAFT.docx"
    if not docx.is_file():
        pytest.skip("no supplementary review draft committed")
    source = ROOT / "manuscripts" / "benchmark" / "supplementary.md"
    report = validate_docx_parity(source, docx, figures_dir=ROOT / "figures")
    assert report["failures"] == [], report["failures"]
    with zipfile.ZipFile(docx) as archive:
        media = [name for name in archive.namelist() if name.startswith("word/media/")]
    assert len(media) == 9  # Supplementary Figures S1-S9
    text = _docx_text(docx)
    assert not re.search(r"\[RESULT:[A-Z]", text)
    assert "NOT FOR SUBMISSION" in text


def test_editable_equations_and_code_participate_in_parity(tmp_path: Path):
    source = _md(tmp_path, "# T\n\n$$\n" + r"G_x^{\ast} = \frac{1}{N}\sum_{x=1}^{N}{x}" +
                 "\n$$\n\n```text\nif valid:\n    report genotype\n```\n")
    out = tmp_path / "math.docx"
    render_docx(source, out)
    root = ET.fromstring(zipfile.ZipFile(out).read("word/document.xml"))
    math_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
    assert root.find(".//" + math_ns + "f") is not None
    assert root.find(".//" + math_ns + "nary") is not None
    assert root.find(".//" + math_ns + "sSubSup") is not None
    assert validate_docx_parity(source, out)["text_parity"]
    source.write_text(source.read_text(encoding="utf-8").replace("{1}", "{2}"), encoding="utf-8")
    assert not validate_docx_parity(source, out)["text_parity"]
