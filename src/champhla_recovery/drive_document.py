"""Deterministic reader and review DOCX rendering with editable mathematics."""
from __future__ import annotations

import datetime as dt
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass, replace
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from lxml import etree
from xml.etree import ElementTree as ET

from .word_equations import equation_xml

from .submission import (FIGURE_CAPTION, RESULT_TAG, _figure_for,
                         _png_dimensions, _sha)

#: Author fields the authors still owe. Highlighted, never dropped: a draft
#: exists to show what is outstanding, and one that looks finished is worse
#: than one that admits it is not.
OUTSTANDING = ("TO CONFIRM", "AUTHOR INPUT REQUIRED")

COMMENT = re.compile(r"<!--.*?-->", re.S)
#: Earliest match wins; bold is tried before italic so ``**`` is never read as
#: an italic delimiter. Applied to the joined paragraph, because a bold span in
#: this source wraps across line breaks (every figure caption does).
MARKERS = (
    ("bold", re.compile(r"\*\*(.+?)\*\*", re.S)),
    ("code", re.compile(r"`([^`]+)`")),
    # Paired, as the author list writes it. Bounded so two unpaired carets in
    # one paragraph can never be joined into a span across half a sentence.
    ("sup", re.compile(r"\^([^\s^][^^]{0,24})\^")),
    # Unpaired, as an exponent: supplementary.md enumerates all 2^d sign
    # assignments, which is a power, not stray punctuation.
    ("sup", re.compile(r"\^([A-Za-z0-9]{1,3})(?![A-Za-z0-9^])")),
    ("italic", re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")),
)
TEXT_WIDTH_IN = 7.0
TEXT_HEIGHT_IN = 8.0
#: Cell type shrinks as a table widens. The supplement reaches 13 columns, which
#: at a 6.5in measure is half an inch each, so a single size either overflows the
#: wide tables or wastes the narrow ones. 7pt is the floor declared by
#: ``style_contract.minimum_font_points`` in figures/figure_manifest.json.
TABLE_FONT_PT = ((7, 9), (10, 9), (99, 8.5))
FIXED_TIMESTAMP = dt.datetime(2000, 1, 1)
#: The contents field is placed before the first body heading, so it follows
#: the front matter instead of preceding the title. The second anchor supports
#: a separately rendered Supplementary Information document.
TOC_BEFORE = ("Introduction", "S1. Cohort and reference-source audit")


@dataclass(frozen=True)
class Segment:
    """A run of text and the formatting it carries."""

    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    sup: bool = False
    highlight: bool = False


@dataclass(frozen=True)
class Block:
    kind: str
    text: str = ""
    level: int = 0
    rows: tuple[tuple[str, ...], ...] = ()
    image: str = ""


#: Stands in for an escaped asterisk while inline markup is parsed. Allele names
#: are written ``HLA-B\*57:01`` so the asterisk is not read as italic; without
#: this the italic pattern consumed the asterisks and printed ``HLA-B\57:01``.
LITERAL_STAR = ""


def tokenize(text: str, **flags: bool) -> list[Segment]:
    """Split markdown inline markup into formatted segments.

    A backslash-escaped asterisk is literal. Generated tables may contain raw
    allele strings such as ``C*03:04``; protect the allele separator too so it
    can never be consumed as an italic delimiter (SR-015).
    """
    protected = text.replace("\\*", LITERAL_STAR)
    protected = re.sub(r"(?<=[A-Za-z0-9])\*(?=[0-9])", LITERAL_STAR, protected)
    segments = _tokenize(protected, **flags)
    return [replace(segment, text=segment.text.replace(LITERAL_STAR, "*"))
            for segment in segments]


def _tokenize(text: str, **flags: bool) -> list[Segment]:
    best: tuple[str, re.Match] | None = None
    for kind, pattern in MARKERS:
        match = pattern.search(text)
        if match and (best is None or match.start() < best[1].start()):
            best = (kind, match)
    if best is None:
        return [Segment(text, **flags)] if text else []
    kind, match = best
    segments: list[Segment] = []
    if match.start():
        segments.extend(_tokenize(text[:match.start()], **flags))
    segments.extend(_tokenize(match.group(1), **{**flags, kind: True}))
    segments.extend(_tokenize(text[match.end():], **flags))
    return segments


def _mark_outstanding(segments: list[Segment]) -> list[Segment]:
    return [replace(s, highlight=True) if any(m in s.text for m in OUTSTANDING) else s
            for s in segments]


def parse_markdown(path: str | Path, strip_result_tags: bool = True,
                   figures_dir: Path | None = None, level_offset: int = 0) -> list[Block]:
    """Blocks from markdown, with comments dropped and markup left intact.

    ``level_offset`` demotes every heading, which is what lets the supplement
    nest under an appendix heading instead of opening a second title.
    """
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    blocks: list[Block] = []
    paragraph: list[str] = []
    index = 0

    def flush() -> None:
        if not paragraph:
            return
        raw = " ".join(paragraph).strip()
        paragraph.clear()
        if strip_result_tags:
            raw = RESULT_TAG.sub("", raw)
        raw = re.sub(r"\s+", " ", raw).strip()
        if not raw:
            return
        figure = _figure_for(raw, figures_dir)
        blocks.append(Block("image" if figure else "paragraph", raw, image=figure))

    while index < len(lines):
        # Strip comments first: a sentinel is not content, and dropping it also
        # breaks the paragraph so an adjacent caption starts cleanly.
        stripped = COMMENT.sub("", lines[index]).strip()
        if not stripped or stripped == "---":
            flush()
            index += 1
            continue
        if stripped.startswith("```") or stripped == "$$":
            flush()
            is_math = stripped == "$$"
            closing = "$$" if is_math else "```"
            index += 1
            content = []
            while index < len(lines) and lines[index].strip() != closing:
                content.append(lines[index])
                index += 1
            if index == len(lines):
                raise ValueError(f"unclosed {closing} block in {path}")
            blocks.append(Block("math" if is_math else "code", "\n".join(content)))
            index += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        if heading:
            flush()
            level = min(len(heading.group(1)) + level_offset, 9)
            blocks.append(Block("heading", heading.group(2).strip(), level=level))
            index += 1
        elif bullet:
            flush()
            content = [bullet.group(1).strip()]
            index += 1
            while index < len(lines):
                continuation = COMMENT.sub("", lines[index]).strip()
                if (not continuation or re.match(r"^(?:#{1,6}\s|[-*]\s|\||```|\$\$|<!--)", continuation)):
                    break
                content.append(continuation)
                index += 1
            value = " ".join(content)
            if strip_result_tags:
                value = RESULT_TAG.sub("", value)
            blocks.append(Block("bullet", value.strip()))
        elif stripped.startswith("|") and stripped.endswith("|"):
            flush()
            table_lines: list[str] = []
            while index < len(lines):
                candidate = COMMENT.sub("", lines[index]).strip()
                if not (candidate.startswith("|") and candidate.endswith("|")):
                    break
                table_lines.append(candidate)
                index += 1
            rows = [tuple(cell.strip() for cell in line.strip("|").split("|"))
                    for line in table_lines]
            if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", ""))
                                     for cell in rows[1]):
                del rows[1]
            blocks.append(Block("table", rows=tuple(rows)))
        else:
            paragraph.append(stripped)
            index += 1
    flush()
    return blocks


def _write_segments(paragraph, segments: list[Segment], size: Pt | None = None,
                    force_bold: bool = False, force_highlight: bool = False) -> None:
    for segment in segments:
        run = paragraph.add_run(segment.text)
        run.bold = segment.bold or force_bold
        run.italic = segment.italic
        if segment.sup:
            run.font.superscript = True
        if segment.code:
            run.font.name = "Consolas"
        if segment.highlight or force_highlight:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW
        if size is not None:
            run.font.size = size


def _add_paragraph(document, text: str, style: str | None = None,
                   size: Pt | None = None) -> None:
    """A body paragraph. Outstanding-author blocks are flagged whole."""
    outstanding = any(marker in text for marker in OUTSTANDING)
    paragraph = document.add_paragraph(style=style)
    segments = _mark_outstanding(tokenize(text))
    _write_segments(paragraph, segments, size=size,
                    force_bold=outstanding, force_highlight=outstanding)


def _field(paragraph, instruction: str, placeholder: str = "") -> None:
    """A Word field code. Used for the contents field and the page number."""
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = placeholder
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for node in (begin, instr, separate, text, end):
        run._r.append(node)


def _repeat_header(table) -> None:
    """Carry the header across page breaks; the exclusion table runs ~44 rows."""
    if not table.rows:
        return
    properties = table.rows[0]._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    properties.append(header)


def _table_font(columns: int) -> Pt:
    return Pt(next(size for limit, size in TABLE_FONT_PT if columns <= limit))


def _fit_to_measure(table) -> None:
    """Pin the table to 100% of the measure so a wide one cannot overflow it."""
    properties = table._tbl.tblPr
    width = properties.find(qn("w:tblW"))
    if width is None:
        width = OxmlElement("w:tblW")
        properties.append(width)
    width.set(qn("w:type"), "pct")
    width.set(qn("w:w"), "5000")



def _add_table(document, rows: tuple[tuple[str, ...], ...]) -> None:
    columns = max(len(row) for row in rows)
    table = document.add_table(rows=0, cols=columns)
    # Table Grid carries real borders and a tblGrid, which the hand-built w:tbl
    # in submission.py omits entirely -- invalid OOXML that renders badly.
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    _fit_to_measure(table)
    size = _table_font(columns)
    # Allocate more room to method names and prose than to short count columns.
    section = document.sections[-1]
    measure = (section.page_width - section.left_margin - section.right_margin) / 914400
    weights = []
    for index in range(columns):
        values = sorted(len(row[index]) for row in rows if len(row) > index)
        typical = values[int(0.8 * (len(values) - 1))]
        weights.append(min(2.6, max(0.75, typical / 15)))
    for column, weight in zip(table.columns, weights):
        column.width = Inches(measure * weight / sum(weights))

    for row_index, row in enumerate(rows):
        table_row = table.add_row()
        table_row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))
        cells = table_row.cells
        for cell_index in range(columns):
            value = row[cell_index] if cell_index < len(row) else ""
            cells[cell_index].width = table.columns[cell_index].width
            paragraph = cells[cell_index].paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(2)
            paragraph.paragraph_format.space_before = Pt(2)
            paragraph.paragraph_format.line_spacing = 1.0
            _write_segments(paragraph,
                            _mark_outstanding(tokenize(value)),
                            size=size, force_bold=row_index == 0)
    _repeat_header(table)
    # An intervening paragraph prevents Word merging adjacent source tables.
    spacer = document.add_paragraph()
    spacer.paragraph_format.space_after = Pt(0)
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.line_spacing = Pt(2)
    spacer.add_run().font.size = Pt(2)


def _add_figure(document, caption: str, image: str) -> None:
    """The image, then its caption. Sized to the measure, not to source dpi.

    ``submission._drawing`` divides pixel width by 300 to get inches; these
    figures are rendered at 600 dpi per ``figures/figure_manifest.json``, so
    that assumption is wrong and merely saturates its own 6.2in cap.
    """
    width, height = _png_dimensions(Path(image))
    inches = TEXT_WIDTH_IN
    if inches * height / width > TEXT_HEIGHT_IN:
        inches = TEXT_HEIGHT_IN * width / height
    holder = document.add_paragraph()
    holder.paragraph_format.keep_with_next = True
    holder.alignment = WD_ALIGN_PARAGRAPH.CENTER
    holder.add_run().add_picture(image, width=Inches(inches))
    legend = document.add_paragraph(style="Caption")
    _write_segments(legend, _mark_outstanding(tokenize(caption)))


def _add_contents(document) -> None:
    heading = document.add_paragraph()
    heading.add_run("Contents").bold = True
    _field(document.add_paragraph(), r'TOC \o "1-3" \h \z \u',
           "Use the document outline to navigate.")


def _orientation(document, landscape):
    section = document.sections[-1]
    desired = WD_ORIENT.LANDSCAPE if landscape else WD_ORIENT.PORTRAIT
    if section.orientation == desired:
        return
    section = document.add_section(WD_SECTION.NEW_PAGE)
    section.orientation = desired
    section.page_width = Inches(11 if landscape else 8.5)
    section.page_height = Inches(8.5 if landscape else 11)


def _add_blocks(document, blocks: list[Block], toc_before: tuple[str, ...] | None = None) -> dict:
    figures: list[str] = []
    tables = 0
    index = 0
    while index < len(blocks):
        block = blocks[index]
        # Place the caption on the same sheet as its wide table.
        caption = (block.kind == "paragraph"
                   and index + 1 < len(blocks) and blocks[index + 1].kind == "table")
        if caption:
            _orientation(document, max(map(len, blocks[index + 1].rows)) >= 8)
        elif block.kind == "table":
            _orientation(document, max(map(len, block.rows)) >= 8)
        elif not (block.kind == "paragraph" and index > 0
                  and blocks[index - 1].kind == "table"):
            _orientation(document, False)
        if block.kind == "heading":
            if toc_before and block.text.strip() in toc_before:
                _add_contents(document)
                toc_before = None
            style = "Title" if block.level == 1 else f"Heading {min(block.level - 1, 9)}"
            _add_paragraph(document, block.text, style=style)
        elif block.kind == "paragraph":
            _add_paragraph(document, block.text)
            if caption:
                document.paragraphs[-1].paragraph_format.keep_with_next = True
        elif block.kind == "bullet":
            _add_paragraph(document, block.text, style="List Bullet")
        elif block.kind == "code":
            paragraph = document.add_paragraph(style="Code")
            paragraph.add_run(block.text)
        elif block.kind == "math":
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph._p.append(etree.fromstring(ET.tostring(equation_xml(block.text))))
        elif block.kind == "table":
            _add_table(document, block.rows)
            tables += 1
        elif block.kind == "image":
            _add_figure(document, block.text, block.image)
            figures.append(FIGURE_CAPTION.match(block.text).group(0).strip("*").rstrip("."))
        index += 1
    _orientation(document, False)
    return {"figures": figures, "tables": tables, "toc_pending": toc_before}


def _figure_label(caption: str) -> tuple[bool, str] | None:
    """(is_supplementary, number) for a figure caption, or None."""
    match = FIGURE_CAPTION.match(caption)
    if not match:
        return None
    return bool(match.group(1)), match.group(2)


def _citation_pattern(supplementary: bool, number: str) -> re.Pattern[str]:
    r"""Matches a reference to this figure in body text.

    Main and supplementary numbering cannot collide because the supplement
    always carries the S: "Figure S2" never matches ``Figure\s+2\b``. A panel
    citation such as "Figure 1A" counts as citing Figure 1; "Figure 10" does
    not, because a digit is not a panel letter.
    """
    body = rf"S{number}" if supplementary else number
    return re.compile(rf"\bFigures?\s+{body}[A-Z]?\b")


def _inline_figures(blocks: list[Block]) -> list[Block]:
    """Move each figure to just after the paragraph that first cites it.

    Journals want legends collected in their own section, so the markdown
    keeps them there and this runs only for the Drive rendering, where the
    reviewer asked to see each figure in place.

    A figure no paragraph cites is left exactly where it was. Supplementary
    Figures S1-S4 are referenced only from the main text, so relocating them
    to the end of the supplement would scatter a set that currently reads in
    order.
    """
    targets: dict[int, int] = {}
    for index, block in enumerate(blocks):
        if block.kind != "image":
            continue
        label = _figure_label(block.text)
        if label is None:
            continue
        pattern = _citation_pattern(*label)
        citation = next(
            (other for other, candidate in enumerate(blocks)
             if candidate.kind in ("paragraph", "bullet")
             and pattern.search(candidate.text)),
            None)
        if citation is not None:
            targets[index] = citation
    if not targets:
        return blocks
    following: dict[int, list[int]] = {}
    for figure, citation in targets.items():
        following.setdefault(citation, []).append(figure)
    ordered: list[Block] = []
    for index, block in enumerate(blocks):
        if index not in targets:
            ordered.append(block)
        for figure in following.get(index, ()):
            ordered.append(blocks[figure])
    return ordered


def _drop_empty_legend_heading(blocks: list[Block]) -> list[Block]:
    """Remove the now-empty "Figure legends" heading left by _inline_figures."""
    kept: list[Block] = []
    for index, block in enumerate(blocks):
        if (block.kind == "heading"
                and block.text.strip().lower() == "figure legends"):
            following = blocks[index + 1:]
            nothing_under = not following or (
                following[0].kind == "heading"
                and following[0].level <= block.level)
            if nothing_under:
                continue
        kept.append(block)
    return kept


def _retitle_appendix(blocks: list[Block], heading: str) -> list[Block]:
    """Rename the supplement's own top heading rather than adding another.

    Inserting a separate appendix heading left two adjacent Heading 1 entries
    saying nearly the same thing, so the supplement still read as a sibling of
    the paper rather than as its appendix.
    """
    for index, block in enumerate(blocks):
        if block.kind == "heading":
            return [*blocks[:index], replace(block, text=heading), *blocks[index + 1:]]
    return blocks


def _page_setup(document, running_title: str) -> None:
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    for side in ("top", "bottom", "left", "right"):
        setattr(section, f"{side}_margin", Inches(0.75 if side in ("left", "right") else 0.7))
    section.header_distance = Inches(0.3)
    section.footer_distance = Inches(0.3)
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1.1
    normal.paragraph_format.space_after = Pt(6)
    for name, points in (("Title", 18), ("Heading 1", 14), ("Heading 2", 12),
                         ("Heading 3", 11), ("Caption", 9), ("Subtitle", 10)):
        style = document.styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(points)
        style.font.color.rgb = RGBColor(0, 0, 0)
        if name in ("Title", "Heading 1", "Heading 2", "Heading 3"):
            style.font.bold = True
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.line_spacing = 1.0 if name == "Caption" else 1.1
        if style.element.pPr is not None:
            border = style.element.pPr.find(qn("w:pBdr"))
            if border is not None:
                style.element.pPr.remove(border)
    if "Code" not in document.styles:
        document.styles.add_style("Code", WD_STYLE_TYPE.PARAGRAPH)
    code = document.styles["Code"]
    code.font.name = "Consolas"
    code.font.size = Pt(9)
    code.paragraph_format.line_spacing = 1.0
    code.paragraph_format.keep_together = True
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_run = header.add_run("Consensus HLA genotyping benchmark")
    header_run.italic = True
    header_run.font.size = Pt(9)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _field(footer, "PAGE", "1")


def _normalize(path: Path) -> None:
    """Rewrite the archive with fixed timestamps so a rebuild is checksummable.

    python-docx stamps the current time into every ZipInfo, so without this the
    same manuscript renders to a different SHA-256 on every run.
    """
    with zipfile.ZipFile(path) as archive:
        parts = {name: archive.read(name) for name in sorted(archive.namelist())}
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=".docx", dir=str(path.parent))
    handle.close()
    temporary = Path(handle.name)
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, blob in parts.items():
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, blob)
    shutil.move(str(temporary), str(path))


def render_combined_docx(manuscript_path: str | Path, output_path: str | Path,
                         supplementary_path: str | Path | None = None,
                         figures_dir: str | Path | None = None,
                         strip_result_tags: bool = True,
                         header_note: list[str] | None = None,
                         title: str = "ChampHLA manuscript",
                         appendix_heading: str = "Appendix: Supplementary material",
                         inline_figures: bool = True,
                         preface_path: str | Path | None = None) -> dict:
    """One document: the paper, then the supplement nested beneath an appendix.

    ``inline_figures`` moves each main-text figure to just after the paragraph
    that first cites it, which is how the reviewer asked to read the Drive
    copy. The markdown keeps its journal-style collected legend section either
    way, because journals require it. The supplement is left collected: only
    S5-S7 are cited within it, so inlining there would break numeric order.

    ``preface_path`` is a markdown note rendered ahead of the paper on its own
    page -- for a shared copy, a summary of what changed since the last one. It
    belongs to that copy only, never to the manuscript, so it should use level-2
    headings and carry no figures or tables.
    """
    figures = Path(figures_dir).resolve() if figures_dir else None
    output = Path(output_path)
    document = Document()
    _page_setup(document, title)

    for line in header_note or []:
        _add_paragraph(document, line, style="Subtitle")

    if preface_path:
        preface = parse_markdown(preface_path, strip_result_tags, figures)
        if any(block.kind in ("table", "image") for block in preface):
            raise ValueError("a preface must not carry tables or figures: they would "
                             "shift the manuscript's numbering")
        _add_blocks(document, preface)
        document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    main = parse_markdown(manuscript_path, strip_result_tags, figures)
    if inline_figures:
        main = _drop_empty_legend_heading(_inline_figures(main))
    summary = _add_blocks(document, main, toc_before=TOC_BEFORE)
    if summary["toc_pending"]:
        # The anchor heading was not found, so the contents field would other-
        # wise be dropped silently.
        _add_contents(document)

    supplement: list[Block] = []
    if supplementary_path:
        document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        # Demoted one level so the supplement nests under its own appendix
        # heading rather than opening a second Title and splitting the outline.
        supplement = _retitle_appendix(
            parse_markdown(supplementary_path, strip_result_tags, figures, level_offset=1),
            appendix_heading)
        # Deliberately not inlined. Only S5-S7 are cited inside the supplement,
        # so relocating them would leave S1-S4 stranded after them and the
        # supplementary figures would no longer read in numeric order.
        extra = _add_blocks(document, supplement)
        summary = {"figures": summary["figures"] + extra["figures"],
                   "tables": summary["tables"] + extra["tables"]}

    properties = document.core_properties
    properties.title = title
    properties.author = "ChampHLA authors"
    properties.created = FIXED_TIMESTAMP
    properties.modified = FIXED_TIMESTAMP
    properties.revision = 1

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(str(output))
    _normalize(output)
    return {"blocks": len(main) + len(supplement), "figures_embedded": len(summary["figures"]),
            "figure_order": summary["figures"], "tables": summary["tables"],
            "header_note_lines": len(header_note or []),
            "result_tags_stripped": strip_result_tags, "sha256": _sha(output)}
