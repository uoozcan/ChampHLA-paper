"""Fail-closed NCI-60 class I reference typing (Adams et al. 2005) and cell-line naming.

The rules are fixed by decisions/20261026_nci60_v350_regeneration.json:

- ``XXYY`` is two-field ``XX:YY``; ``XXYYZZ`` is three-field and reduced to ``XX:YY``;
- ``XXYYZ`` follows the 2005 nomenclature (four digits plus one synonymous digit) and
  is reduced to ``XX:YY``;
- ``XXa`` (source footnote: two-digit denominations with a superscript a) is an
  unresolved ambiguity, ``new`` a novel allele and ``N.R.`` an unresolved typing: the
  locus is excluded and listed;
- every two-field allele must exist in the pinned IPD-IMGT/HLA 3.65.0 allele list;
- one listed allele is a homozygous genotype in the primary analysis
  (``single_allele=1``; the sensitivity analysis excludes those loci);
- any other token shape excludes the locus. Nothing is guessed or truncated.

The tabulation ``nci60_classI_raw.tsv`` must agree cell for cell with the class I
table of the article's PMC XML; a disagreement stops the parse.
"""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

GENES = (("A", "A locus"), ("B", "B Locus"), ("C", "Cw Locus"))
TRUTH_FIELDS = ("cell_line", "sample_key", "gene", "allele1", "allele2", "truth_state",
                "single_allele", "source_cell", "exclusion_reason")
_TWO_FIELD = re.compile(r"^\d{4}$")
_FIVE = re.compile(r"^\d{5}$")
_SIX = re.compile(r"^\d{6}$")
_AMBIGUOUS = re.compile(r"^\d{2}a$")


def sample_key(name: str) -> str:
    """Join key for cell-line names across Adams, SRA and ENA spellings."""
    key = re.sub(r"[^A-Z0-9]", "", name.upper())
    return "7860" if key == "786O" else key  # 786-O is spelled 786-0 in the read archives


def sample_id(name: str) -> str:
    return "NCI60_" + sample_key(name)


def _cell_text(cell_xml: str) -> str:
    text = re.sub(r"<sup>\s*a\s*</sup>", "a", cell_xml)
    text = re.sub(r"<[^>]+>", "", text)
    return " ".join(text.split())


def read_xml_class_i(path: Path) -> dict[str, dict[str, str]]:
    """Cell line -> {column: text} from the article's class I table."""
    xml = path.read_text(encoding="utf-8")
    for table in re.findall(r"<table-wrap[^>]*>(.*?)</table-wrap>", xml, re.S):
        caption = re.search(r"<caption>(.*?)</caption>", table, re.S)
        if caption and "class I Loci" in re.sub(r"<[^>]+>", " ", caption.group(1)):
            rows = [[_cell_text(cell) for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
                    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", table, re.S)]
            header, body = rows[0], rows[1:]
            return {row[0]: dict(zip(header, row)) for row in body}
    raise ValueError(f"class I table not found in {path}")


def read_raw(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {row["Cell Line"]: row for row in rows}


def cross_check(raw: dict[str, dict[str, str]], xml: dict[str, dict[str, str]]) -> None:
    if set(raw) != set(xml):
        raise ValueError(f"cell lines differ: raw-only {sorted(set(raw) - set(xml))}, "
                         f"xml-only {sorted(set(xml) - set(raw))}")
    for line in raw:
        for _, column in GENES:
            left = " ".join(raw[line][column].split())
            right = xml[line][column]
            if left != right:
                raise ValueError(f"{line} {column}: tabulation {left!r} != article {right!r}")


def load_allele_list(path: Path) -> set[str]:
    """Two-field names present in the pinned IPD-IMGT/HLA allele list (e.g. ``A*02:01``)."""
    names = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or line.startswith("AlleleID"):
            continue
        allele = line.split(",", 1)[1]
        gene, _, fields = allele.partition("*")
        parts = fields.split(":")
        if len(parts) >= 2:
            names.add(f"{gene}*{parts[0]}:{re.sub(r'[A-Z]$', '', parts[1])}")
    return names


def parse_token(token: str, gene: str) -> tuple[str, str]:
    """(two-field allele, "") or ("", exclusion reason)."""
    token = token.strip()
    if _AMBIGUOUS.fullmatch(token):
        return "", "unresolved_two_digit_ambiguity"
    if "new" in token.lower():
        return "", "new_allele"
    if _TWO_FIELD.fullmatch(token) or _FIVE.fullmatch(token) or _SIX.fullmatch(token):
        return f"{gene}*{token[:2]}:{token[2:4]}", ""
    return "", f"unrecognised_token:{token}"


def parse_cell(cell: str, gene: str, alleles: set[str]) -> dict[str, str]:
    text = " ".join(cell.split())
    if not text or text.upper().startswith("N.R"):
        return {"truth_state": "excluded", "exclusion_reason": "not_resolved"}
    tokens = [part.strip() for part in text.split(",")]
    if len(tokens) > 2 or any(not part for part in tokens):
        return {"truth_state": "excluded", "exclusion_reason": f"malformed_cell:{text}"}
    parsed = []
    for token in tokens:
        allele, reason = parse_token(token, gene)
        if reason:
            return {"truth_state": "excluded", "exclusion_reason": reason}
        if allele not in alleles:
            return {"truth_state": "excluded", "exclusion_reason": f"not_in_ipd_3_65_0:{allele}"}
        parsed.append(allele)
    single = len(parsed) == 1
    first, second = sorted(parsed * 2 if single else parsed)
    return {"truth_state": "resolved", "allele1": first, "allele2": second,
            "single_allele": "1" if single else "0", "exclusion_reason": ""}


def build_truth(raw_path: Path, xml_path: Path, allele_list_path: Path) -> list[dict[str, str]]:
    raw, xml = read_raw(raw_path), read_xml_class_i(xml_path)
    cross_check(raw, xml)
    alleles = load_allele_list(allele_list_path)
    rows = []
    for line in sorted(raw):
        for gene, column in GENES:
            parsed = parse_cell(raw[line][column], gene, alleles)
            rows.append({field: "" for field in TRUTH_FIELDS} | {
                "cell_line": line, "sample_key": sample_key(line), "gene": gene,
                "source_cell": " ".join(raw[line][column].split()), **parsed,
            })
    keys = [row["sample_key"] for row in rows if row["gene"] == "A"]
    if len(keys) != len(set(keys)):
        raise ValueError("two Adams cell lines share a join key")
    return rows


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
