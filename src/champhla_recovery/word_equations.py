"""Editable Office Math for the small LaTeX subset used in the manuscript.

Unsupported commands fail explicitly; equations are never rasterized or silently
flattened. The canonical XML signature also participates in source/DOCX parity.
"""

from __future__ import annotations
import re
from xml.etree import ElementTree as ET

M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
ET.register_namespace("m", M)


def node(name, *children, **attrs):
    element = ET.Element(f"{{{M}}}{name}", {f"{{{M}}}{k}": str(v) for k, v in attrs.items()})
    element.extend(children)
    return element


def run(text, style=None):
    element = node("r")
    if style:
        prop = node("rPr")
        prop.append(node("scr", val="script") if style == "script" else node("sty", val=style))
        element.append(prop)
    value = node("t")
    value.text = text
    element.append(value)
    return element


class Parser:
    symbols = {"in": "∈", "ne": "≠", "varnothing": "∅", "ast": "∗"}

    def __init__(self, text):
        self.text = text
        self.pos = 0

    def space(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def group(self):
        self.space()
        if self.pos < len(self.text) and self.text[self.pos] == "{":
            self.pos += 1
            value = self.sequence("}")
            if self.pos >= len(self.text):
                raise ValueError("unclosed equation group")
            self.pos += 1
            return value
        return self.item(scripts=False)

    def sequence(self, stop=None):
        values = []
        while self.pos < len(self.text):
            self.space()
            if self.pos >= len(self.text) or self.text[self.pos] == stop:
                break
            values.append(self.item())
        return ("seq", values)

    def item(self, scripts=True):
        self.space()
        ch = self.text[self.pos]
        self.pos += 1
        if ch == "{":
            base = self.sequence("}")
            if self.pos >= len(self.text):
                raise ValueError("unclosed equation group")
            self.pos += 1
        elif ch == "\\":
            match = re.match(r"[A-Za-z]+", self.text[self.pos :])
            if match:
                command = match.group()
                self.pos += len(command)
                if command in self.symbols:
                    base = ("text", self.symbols[command])
                elif command in ("sum", "max"):
                    base = ("op", "∑" if command == "sum" else "max")
                elif command == "frac":
                    base = ("frac", self.group(), self.group())
                elif command == "hat":
                    base = ("hat", self.group())
                elif command in ("mathbf", "mathcal", "operatorname"):
                    base = (
                        "style",
                        {"mathbf": "b", "mathcal": "script", "operatorname": "p"}[command],
                        self.group(),
                    )
                else:
                    raise ValueError(f"unsupported equation command: {command}")
            else:
                if self.pos >= len(self.text):
                    raise ValueError("trailing equation escape")
                base = ("text", self.text[self.pos])
                self.pos += 1
        else:
            base = ("text", ch)
        low = high = None
        while scripts:
            self.space()
            if self.pos >= len(self.text) or self.text[self.pos] not in "_^":
                break
            kind = self.text[self.pos]
            self.pos += 1
            value = self.group()
            if kind == "_":
                low = value
            else:
                high = value
        if base == ("op", "∑"):
            return ("sum", low, high, self.group())
        if base == ("op", "max") and low is not None:
            base = ("limit", base, low)
            low = None
        return ("script", base, low, high) if low is not None or high is not None else base


def append(parent, ast, style=None):
    kind = ast[0]
    if kind == "seq":
        for child in ast[1]:
            append(parent, child, style)
    elif kind in ("text", "op"):
        parent.append(run(ast[1], style))
    elif kind == "style":
        append(parent, ast[2], ast[1])
    elif kind == "frac":
        top = node("num")
        bottom = node("den")
        append(top, ast[1])
        append(bottom, ast[2])
        parent.append(node("f", top, bottom))
    elif kind == "hat":
        value = node("e")
        append(value, ast[1], style)
        parent.append(node("acc", node("accPr", node("chr", val="̂")), value))
    elif kind == "limit":
        base = node("e")
        lower = node("lim")
        append(base, ast[1], "p")
        append(lower, ast[2])
        parent.append(node("limLow", base, lower))
    elif kind == "script":
        base = node("e")
        append(base, ast[1], style)
        lo = hi = None
        if ast[2] is not None:
            lo = node("sub")
            append(lo, ast[2])
        if ast[3] is not None:
            hi = node("sup")
            append(hi, ast[3])
        parent.append(
            node("sSubSup", base, lo, hi)
            if lo is not None and hi is not None
            else node("sSub", base, lo)
            if lo is not None
            else node("sSup", base, hi)
        )
    elif kind == "sum":
        props = node("naryPr", node("chr", val="∑"), node("limLoc", val="undOvr"))
        if ast[1] is None:
            props.append(node("subHide", val="1"))
        if ast[2] is None:
            props.append(node("supHide", val="1"))
        lo = node("sub")
        hi = node("sup")
        body = node("e")
        if ast[1] is not None:
            append(lo, ast[1])
        if ast[2] is not None:
            append(hi, ast[2])
        append(body, ast[3])
        parent.append(node("nary", props, lo, hi, body))
    else:
        raise ValueError(kind)


def equation_xml(source):
    parser = Parser(source)
    ast = parser.sequence()
    parser.space()
    if parser.pos != len(source):
        raise ValueError("unparsed equation content")
    value = node("oMath")
    append(value, ast)
    return value


def canonical(element):
    return (
        element.tag,
        tuple(sorted(element.attrib.items())),
        element.text or "",
        tuple(canonical(c) for c in element),
    )


def equation_signature(source):
    return canonical(equation_xml(source))
