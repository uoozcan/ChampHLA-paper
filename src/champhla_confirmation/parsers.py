from __future__ import annotations

import csv
import io
import re

from .io import (
    SINGLETON_POLICIES,
    canonical_allele,
    canonical_pair,
    declares_native_homozygosity,
    normalize_gene,
)

ALLELE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9])(?:HLA-)?[ABC]\*[0-9A-Za-z]+:[0-9A-Za-z]+(?::[0-9A-Za-z]+)*(?:[NLSQCA])?",
    re.I,
)


def _alleles(text: str, gene: str) -> list[str]:
    target = normalize_gene(gene)
    values = []
    for match in ALLELE_PATTERN.findall(text):
        try:
            allele = canonical_allele(match, target)
        except ValueError:
            continue
        values.append(allele)
    return values


def _line_pair(text: str, gene: str):
    for line in text.splitlines():
        values = _alleles(line, gene)
        if len(values) == 2:
            return canonical_pair(values[0], values[1], gene)
        if len(values) == 1 and re.search(r"(?:homo|hom|same)", line, re.I):
            return canonical_pair(values[0], values[0], gene)
    return None


def _optitype_matrix(text: str, gene: str):
    rows = [row for row in csv.reader(io.StringIO(text), delimiter="\t") if row]
    if len(rows) < 2:
        return None
    header = [value.strip().upper() for value in rows[0]]
    target = normalize_gene(gene)
    indices = [i for i, value in enumerate(header) if value in {f"{target}1", f"{target}2"}]
    if len(indices) != 2:
        return None
    values = rows[-1]
    if max(indices) >= len(values):
        return None
    return canonical_pair(values[indices[0]], values[indices[1]], target)


def native_homozygous_pair(caller: str, text: str, gene: str):
    """A ``<gene>\\t<allele>\\t<marker>`` summary line whose marker is the caller's
    documented homozygous declaration (see io.NATIVE_HOMOZYGOUS_MARKERS)."""
    target = normalize_gene(gene)
    for line in text.splitlines():
        fields = [field.strip() for field in line.split("\t")]
        if len(fields) < 3 or fields[0].startswith("#"):
            continue
        try:
            if normalize_gene(fields[0]) != target:
                continue
        except ValueError:
            continue
        if declares_native_homozygosity(caller, fields[1], fields[2]):
            try:
                return canonical_pair(fields[1], fields[1], target)
            except ValueError:
                return None
    return None


def parse_caller_pair(caller: str, text: str, gene: str, singleton_policy: str = "abstain"):
    """Parse a diploid pair from the pinned caller-native result summaries.

    Wrappers may use a normalized line-oriented summary. OptiType's standard
    matrix form is handled explicitly; other pinned wrappers are validated by
    gene-specific allele lines. Unknown or ambiguous content fails closed.
    Under ``singleton_policy="native_declaration"`` a single allele beside the
    caller's documented homozygous marker is completed into a homozygous pair.
    """
    if singleton_policy not in SINGLETON_POLICIES:
        raise ValueError(f"unknown singleton policy {singleton_policy!r}")
    if singleton_policy == "native_declaration":
        pair = native_homozygous_pair(caller, text, gene)
        if pair:
            return pair
    if caller == "OptiType":
        pair = _optitype_matrix(text, gene)
        if pair:
            return pair
    pair = _line_pair(text, gene)
    if pair:
        return pair
    values = _alleles(text, gene)
    if len(values) == 2:
        return canonical_pair(values[0], values[1], gene)
    return None
