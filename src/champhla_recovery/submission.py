"""Render a manuscript to DOCX for circulation, and check the two agree.

Ported into this tree from the superseded staging fork, with three changes the
canonical manuscript needs.

*Figures are embedded from their captions.* This manuscript carries no markdown
image tags -- it names figures in ``**Figure N. ...**`` caption paragraphs and
keeps the files in ``figures/``. A caption is matched to ``figure<N>_*.png`` and
the image is placed above it, so a reviewing co-author sees the figure rather
than a reference to one.

*``[RESULT:...]`` tags are stripped.* They are provenance citations resolved by
the claim auditor, not prose, and a reader of a Word file sees them as debris.
Stripping is explicit and on by default for drafts; the markdown keeps them.

*A draft may carry a header note.* A document circulated before its blockers are
cleared should say so on its first page rather than rely on the covering email.

Output is deterministic: fixed archive timestamps and fixed document dates, so
the same input yields the same SHA-256.
"""
from __future__ import annotations

import hashlib
import re
import struct
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": W, "r": R, "wp": WP, "a": A, "pic": PIC}
for _prefix, _uri in NS.items():
    ET.register_namespace(_prefix, _uri)

RESULT_TAG = re.compile(r"\s*\[RESULT:[A-Za-z0-9_.:-]+\]")
FIGURE_CAPTION = re.compile(
    r"^\*\*(?:(Supplementary)\s+)?Figure\s+(?:S)?(\d+)\."
)
SUPERSCRIPT = re.compile(
    r"\^([^\s^][^^]{0,24})\^|\^([A-Za-z0-9]{1,3})(?![A-Za-z0-9^])"
)


@dataclass(frozen=True)
class Block:
    kind: str
    text: str = ""
    level: int = 0
    rows: tuple[tuple[str, ...], ...] = ()
    image: str = ""


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


#: Stands in for an escaped asterisk (``HLA-B\*57:01``) while emphasis is stripped,
#: so the italic pattern cannot consume it and leave ``HLA-B\57:01`` behind.
LITERAL_STAR = ""


def _plain(text: str, strip_result_tags: bool = True) -> str:
    if strip_result_tags:
        text = RESULT_TAG.sub("", text)
    text = text.replace("\\*", LITERAL_STAR)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", text)
    text = text.replace(LITERAL_STAR, "*")
    return re.sub(r"\s+", " ", text).strip()


def _table_cells(line: str, strip_result_tags: bool) -> tuple[str, ...]:
    return tuple(_plain(cell, strip_result_tags)
                 for cell in line.strip().strip("|").split("|"))


def _figure_for(caption: str, figures_dir: Path | None) -> str:
    """The PNG a caption refers to, or "" when there is none to embed."""
    match = FIGURE_CAPTION.match(caption)
    if not match or figures_dir is None:
        return ""
    prefix = "supplementary_figure_s" if match.group(1) else "figure"
    candidates = sorted(figures_dir.glob(f"{prefix}{match.group(2)}_*.png"))
    return str(candidates[0]) if candidates else ""


def parse_markdown(path: str | Path, strip_result_tags: bool = True,
                   figures_dir: Path | None = None) -> list[Block]:
    from .drive_document import parse_markdown as rich_parse
    def plain(value):
        from .drive_document import tokenize
        return "".join("^" + segment.text + "^" if segment.sup else segment.text for segment in tokenize(value))
    return [Block(block.kind, block.text if block.kind in {"code", "math"} else plain(block.text),
                  block.level, tuple(tuple(plain(cell) for cell in row) for row in block.rows),
                  block.image)
            for block in rich_parse(path, strip_result_tags, figures_dir)]


def _qn(namespace: str, name: str) -> str:
    return f"{{{namespace}}}{name}"


def _paragraph(text: str, style: str | None = None) -> ET.Element:
    p = ET.Element(_qn(W, "p"))
    if style:
        ppr = ET.SubElement(p, _qn(W, "pPr"))
        ET.SubElement(ppr, _qn(W, "pStyle"), {_qn(W, "val"): style})

    def add_run(value: str, superscript: bool = False) -> None:
        if not value:
            return
        run = ET.SubElement(p, _qn(W, "r"))
        if superscript:
            rpr = ET.SubElement(run, _qn(W, "rPr"))
            ET.SubElement(rpr, _qn(W, "vertAlign"), {_qn(W, "val"): "superscript"})
        node = ET.SubElement(run, _qn(W, "t"))
        if value.startswith(" ") or value.endswith(" "):
            node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        node.text = value

    position = 0
    for match in SUPERSCRIPT.finditer(text):
        add_run(text[position:match.start()])
        add_run(match.group(1) or match.group(2), superscript=True)
        position = match.end()
    add_run(text[position:])
    return p


def _display_text(text: str) -> str:
    """Text as rendered after the Markdown superscript delimiters are removed."""
    return SUPERSCRIPT.sub(lambda match: match.group(1) or match.group(2), text)


def _table(rows: tuple[tuple[str, ...], ...]) -> ET.Element:
    table = ET.Element(_qn(W, "tbl"))
    props = ET.SubElement(table, _qn(W, "tblPr"))
    borders = ET.SubElement(props, _qn(W, "tblBorders"))
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        ET.SubElement(borders, _qn(W, edge), {
            _qn(W, "val"): "single", _qn(W, "sz"): "4", _qn(W, "color"): "B7B7B7"})
    for row_index, row in enumerate(rows):
        tr = ET.SubElement(table, _qn(W, "tr"))
        for value in row:
            tc = ET.SubElement(tr, _qn(W, "tc"))
            p = _paragraph(value, "TableText")
            if row_index == 0:
                ET.SubElement(ET.SubElement(p.find(_qn(W, "r")), _qn(W, "rPr")), _qn(W, "b"))
            tc.append(p)
    return table


def _png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"the DOCX renderer accepts PNG figures only: {path}")
    return struct.unpack(">II", data[16:24])


def _xml_attr(text: str) -> str:
    return (text.replace("&", "&amp;").replace('"', "&quot;")
            .replace("<", "&lt;").replace(">", "&gt;"))


def _drawing(rel_id: str, alt: str, image_id: int, width: int, height: int) -> ET.Element:
    cx = min(6.2 * 914400, width / 300 * 914400)
    cy = cx * height / width
    return ET.fromstring(f"""<w:p xmlns:w="{W}" xmlns:r="{R}" xmlns:wp="{WP}"
      xmlns:a="{A}" xmlns:pic="{PIC}"><w:r><w:drawing><wp:inline>
      <wp:extent cx="{int(cx)}" cy="{int(cy)}"/><wp:docPr id="{image_id}"
      name="Figure {image_id}" descr="{_xml_attr(alt)}"/>
      <a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
      <pic:pic><pic:nvPicPr><pic:cNvPr id="{image_id}" name="image{image_id}.png"/>
      <pic:cNvPicPr/></pic:nvPicPr>
      <pic:blipFill><a:blip r:embed="{rel_id}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
      <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{int(cx)}" cy="{int(cy)}"/></a:xfrm>
      <a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>
      </a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>""")


def _xml_bytes(element: ET.Element) -> bytes:
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + ET.tostring(
        element, encoding="utf-8")


#: BMC asks for double-spaced text with line numbers; table cells stay single-spaced
#: and unnumbered so the tables remain readable.
DOUBLE_SPACED = {"Normal", "ListBullet", "Caption"}
FOOTER_REL = "rIdFooter1"


def _footer() -> bytes:
    """A centred PAGE field: BMC asks for page numbers."""
    root = ET.Element(_qn(W, "ftr"))
    p = ET.SubElement(root, _qn(W, "p"))
    ET.SubElement(ET.SubElement(p, _qn(W, "pPr")), _qn(W, "jc"), {_qn(W, "val"): "center"})
    field = ET.SubElement(p, _qn(W, "fldSimple"), {_qn(W, "instr"): "PAGE"})
    ET.SubElement(ET.SubElement(field, _qn(W, "r")), _qn(W, "t")).text = "1"
    return _xml_bytes(root)


def _styles() -> bytes:
    root = ET.Element(_qn(W, "styles"))
    for style_id, name, size, bold in (
        ("Normal", "Normal", "22", False), ("Title", "Title", "32", True),
        ("Heading1", "heading 1", "28", True), ("Heading2", "heading 2", "25", True),
        ("Heading3", "heading 3", "23", True), ("ListBullet", "List Bullet", "22", False),
        ("Caption", "Caption", "20", False), ("DraftNotice", "Draft Notice", "20", True),
        ("TableText", "Table Text", "18", False),
        ("Code", "Code", "18", False),
    ):
        style = ET.SubElement(root, _qn(W, "style"),
                              {_qn(W, "type"): "paragraph", _qn(W, "styleId"): style_id})
        ET.SubElement(style, _qn(W, "name"), {_qn(W, "val"): name})
        ppr = ET.SubElement(style, _qn(W, "pPr"))
        if style_id == "TableText":
            ET.SubElement(ppr, _qn(W, "suppressLineNumbers"))
        ET.SubElement(ppr, _qn(W, "spacing"), {
            _qn(W, "after"): "120" if style_id != "TableText" else "0",
            _qn(W, "line"): "480" if style_id in DOUBLE_SPACED else "240",
            _qn(W, "lineRule"): "auto"})
        rpr = ET.SubElement(style, _qn(W, "rPr"))
        ET.SubElement(rpr, _qn(W, "sz"), {_qn(W, "val"): size})
        if style_id == "Code":
            ET.SubElement(rpr, _qn(W, "rFonts"), {_qn(W, "ascii"): "Consolas", _qn(W, "hAnsi"): "Consolas"})
        if bold:
            ET.SubElement(rpr, _qn(W, "b"))
    return _xml_bytes(root)


def render_docx(markdown_path: str | Path, output_path: str | Path,
                figures_dir: str | Path | None = None,
                strip_result_tags: bool = True,
                header_note: list[str] | None = None,
                title: str = "ChampHLA manuscript") -> dict:
    source = Path(markdown_path).resolve()
    output = Path(output_path)
    figures = Path(figures_dir).resolve() if figures_dir else None
    blocks = parse_markdown(source, strip_result_tags, figures)

    document = ET.Element(_qn(W, "document"))
    body = ET.SubElement(document, _qn(W, "body"))
    relationships: list[tuple[str, str]] = []
    media: list[tuple[str, bytes]] = []
    figure_order: list[str] = []
    embedded = 0

    for line in header_note or []:
        body.append(_paragraph(line, "DraftNotice"))

    for block in blocks:
        if block.kind == "heading":
            body.append(_paragraph(
                block.text, "Title" if block.level == 1 else f"Heading{min(block.level - 1, 3)}"))
        elif block.kind == "paragraph":
            body.append(_paragraph(block.text))
        elif block.kind == "bullet":
            body.append(_paragraph(f"• {block.text}", "ListBullet"))
        elif block.kind == "math":
            from .word_equations import equation_xml
            paragraph = ET.SubElement(body, _qn(W, "p"))
            paragraph.append(equation_xml(block.text))
        elif block.kind == "code":
            paragraph = ET.SubElement(body, _qn(W, "p"))
            props = ET.SubElement(paragraph, _qn(W, "pPr"))
            ET.SubElement(props, _qn(W, "pStyle"), {_qn(W, "val"): "Code"})
            for index, line in enumerate(block.text.split("\n")):
                run = ET.SubElement(paragraph, _qn(W, "r"))
                if index:
                    ET.SubElement(run, _qn(W, "br"))
                text = ET.SubElement(run, _qn(W, "t"), {"{http://www.w3.org/XML/1998/namespace}space": "preserve"})
                text.text = line
        elif block.kind == "table":
            body.append(_table(block.rows))
        elif block.kind == "image":
            image_path = Path(block.image)
            if not image_path.is_file():
                raise FileNotFoundError(f"figure missing: {image_path}")
            width, height = _png_dimensions(image_path)
            image_id = len(media) + 1
            rel_id = f"rId{image_id}"
            relationships.append((rel_id, f"media/image{image_id}.png"))
            media.append((f"image{image_id}.png", image_path.read_bytes()))
            body.append(_drawing(rel_id, block.text, image_id, width, height))
            body.append(_paragraph(block.text, "Caption"))
            figure_order.append(block.text)
            embedded += 1

    sect = ET.SubElement(body, _qn(W, "sectPr"))
    ET.SubElement(sect, _qn(W, "footerReference"),
                  {_qn(W, "type"): "default", _qn(R, "id"): FOOTER_REL})
    ET.SubElement(sect, _qn(W, "pgSz"), {_qn(W, "w"): "12240", _qn(W, "h"): "15840"})
    ET.SubElement(sect, _qn(W, "pgMar"), {
        _qn(W, "top"): "1080", _qn(W, "right"): "1080", _qn(W, "bottom"): "1080",
        _qn(W, "left"): "1080", _qn(W, "header"): "720", _qn(W, "footer"): "720"})
    ET.SubElement(sect, _qn(W, "lnNumType"), {
        _qn(W, "countBy"): "1", _qn(W, "restart"): "continuous"})

    rel_root = ET.Element("Relationships", xmlns=PKG_REL)
    ET.SubElement(rel_root, "Relationship", {
        "Id": FOOTER_REL, "Target": "footer1.xml",
        "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"})
    for rel_id, target in relationships:
        ET.SubElement(rel_root, "Relationship", {
            "Id": rel_id, "Target": target,
            "Type": "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"})

    parts = {
        "[Content_Types].xml": b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>''',
        "_rels/.rels": b'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
</Relationships>''',
        "docProps/core.xml": ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"'
            ' xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/"'
            ' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f'<dc:title>{_xml_attr(title)}</dc:title><dc:creator>ChampHLA authors</dc:creator>'
            '<dcterms:created xsi:type="dcterms:W3CDTF">2000-01-01T00:00:00Z</dcterms:created>'
            '<dcterms:modified xsi:type="dcterms:W3CDTF">2000-01-01T00:00:00Z</dcterms:modified>'
            '</cp:coreProperties>').encode("utf-8"),
        "word/document.xml": _xml_bytes(document),
        "word/styles.xml": _styles(),
        "word/footer1.xml": _footer(),
        "word/_rels/document.xml.rels": _xml_bytes(rel_root),
    }
    parts.update({f"word/media/{name}": data for name, data in media})
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in sorted(parts):
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, parts[name])
    return {"blocks": len(blocks), "figures_embedded": embedded,
            "figure_order": figure_order, "header_note_lines": len(header_note or []),
            "result_tags_stripped": strip_result_tags, "sha256": _sha(output)}


def _block_signature(block: Block) -> tuple:
    if block.kind == "math":
        from .word_equations import equation_signature
        return ("math", equation_signature(block.text))
    if block.kind == "code":
        return ("code", block.text)
    if block.kind == "table":
        return ("table", tuple(tuple(_display_text(cell) for cell in row)
                               for row in block.rows))
    if block.kind == "image":
        return ("image", _display_text(block.text))
    return (block.kind, _display_text(block.text))


def _rendered(text: str) -> str:
    """Normalise DOCX text like markdown, treating every asterisk as literal.

    Rendered text carries no emphasis markup, so an asterisk in it is part of an
    allele name (``HLA-B*57:01``) and must not be paired as italic.
    """
    return _plain(text.replace("*", "\\*"))


def _docx_signatures(path: Path) -> tuple[list[tuple], list[str], list[str]]:
    failures: list[str] = []
    with zipfile.ZipFile(path) as archive:
        prohibited = [name for name in archive.namelist()
                      if name.endswith("vbaProject.bin") or "comments" in name
                      or "people.xml" in name]
        if prohibited:
            failures.append(f"prohibited DOCX parts: {prohibited}")
        body = ET.fromstring(archive.read("word/document.xml")).find("w:body", NS)
    signatures: list[tuple] = []
    figure_order: list[str] = []
    for child in list(body):
        if child.tag == _qn(W, "sectPr"):
            continue
        if child.tag == _qn(W, "tbl"):
            signatures.append(("table", tuple(
                tuple(_rendered("".join(tc.itertext())) for tc in tr.findall("w:tc", NS))
                for tr in child.findall("w:tr", NS))))
            continue
        style_node = child.find("w:pPr/w:pStyle", NS)
        style = style_node.get(_qn(W, "val")) if style_node is not None else ""
        text = _rendered("".join(node.text or "" for node in child.findall(".//w:t", NS)))
        doc_pr = child.find(".//wp:docPr", NS)
        if doc_pr is not None:
            signatures.append(("image", doc_pr.get("descr", "")))
            figure_order.append(doc_pr.get("descr", ""))
        elif child.find("{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath") is not None:
            from .word_equations import canonical
            signatures.append(("math", canonical(child.find("{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath"))))
        elif style == "Code":
            value = "".join("\n" if node.tag == _qn(W, "br") else node.text or ""
                            for node in child.iter() if node.tag in {_qn(W, "br"), _qn(W, "t")})
            signatures.append(("code", value))
        elif style in {"Caption", "DraftNotice"}:
            continue  # the caption repeats its image's alt text; the notice is not source
        elif style == "Title" or style.startswith("Heading"):
            signatures.append(("heading", text))
        elif style == "ListBullet":
            signatures.append(("bullet", text[2:] if text.startswith("• ") else text))
        else:
            signatures.append(("paragraph", text))
    return signatures, figure_order, failures


def validate_docx_parity(markdown: str | Path, docx: str | Path,
                         figures_dir: str | Path | None = None,
                         strip_result_tags: bool = True) -> dict:
    """Does the DOCX say what the markdown says?

    Compared against the markdown as transformed for rendering, so the
    documented transformations do not register as drift while a real
    divergence still does.
    """
    figures = Path(figures_dir).resolve() if figures_dir else None
    expected_blocks = parse_markdown(markdown, strip_result_tags, figures)
    expected = [_block_signature(block) for block in expected_blocks]
    actual, actual_figures, failures = _docx_signatures(Path(docx))
    expected_figures = [b.text for b in expected_blocks if b.kind == "image"]
    if expected != actual:
        first = next((i for i, (e, a) in enumerate(zip(expected, actual)) if e != a),
                     min(len(expected), len(actual)))
        failures.append(f"markdown and DOCX diverge at block {first}")
    if expected_figures != actual_figures:
        failures.append("figure order differs between markdown and DOCX")
    return {"text_parity": expected == actual,
            "figure_order_valid": expected_figures == actual_figures,
            "blocks_compared": len(expected), "failures": failures}
