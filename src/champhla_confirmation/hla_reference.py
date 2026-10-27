from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


EXPRESSION_SUFFIXES = frozenset("NLSQCA")
GROUP_SUFFIXES = frozenset("PG")
_RENAMED_RE = re.compile(
    r"(?:renamed|identical to|is now named)\s+(?:HLA-)?([A-Z0-9]+\*[0-9:]+[NLSQCA]?)",
    re.I,
)


def _strip_hla(value: str) -> str:
    token = value.strip().upper()
    return token[4:] if token.startswith("HLA-") else token


def _two_field(value: str) -> str:
    token = _strip_hla(value)
    if "*" not in token:
        return ""
    gene, fields = token.split("*", 1)
    fields = fields.rstrip("NLSQCA")
    parts = fields.split(":")
    return f"{gene}*{parts[0]}:{parts[1]}" if len(parts) >= 2 else ""


@dataclass(frozen=True)
class HLAReference:
    """Pinned IPD-IMGT/HLA nomenclature used for release-backed normalization."""

    release: str
    alleles: frozenset[str]
    two_field_alleles: frozenset[str]
    deleted_mappings: dict[str, str]
    p_groups: dict[str, frozenset[str]]
    g_groups: dict[str, frozenset[str]]
    source_sha256: dict[str, str]

    @classmethod
    def from_files(
        cls,
        release: str,
        allele_list: str | Path,
        *,
        deleted_alleles: str | Path | None = None,
        p_groups: str | Path | None = None,
        g_groups: str | Path | None = None,
    ) -> "HLAReference":
        from .io import sha256

        allele_path = Path(allele_list)
        alleles = _read_alleles(allele_path)
        deleted = _read_deleted(Path(deleted_alleles)) if deleted_alleles else {}
        p_map = _read_groups(Path(p_groups), "P") if p_groups else {}
        g_map = _read_groups(Path(g_groups), "G") if g_groups else {}
        paths = {
            "allele_list": allele_path,
            **({"deleted_alleles": Path(deleted_alleles)} if deleted_alleles else {}),
            **({"p_groups": Path(p_groups)} if p_groups else {}),
            **({"g_groups": Path(g_groups)} if g_groups else {}),
        }
        return cls(
            release=release,
            alleles=frozenset(alleles),
            two_field_alleles=frozenset(filter(None, (_two_field(x) for x in alleles))),
            deleted_mappings=deleted,
            p_groups=p_map,
            g_groups=g_map,
            source_sha256={name: sha256(path) for name, path in paths.items()},
        )

    def classify(self, token: str, two_field: str, suffix: str) -> dict[str, str]:
        canonical = _strip_hla(token)
        if suffix in GROUP_SUFFIXES:
            groups = self.p_groups if suffix == "P" else self.g_groups
            members = groups.get(canonical, frozenset())
            member_two_fields = sorted(set(filter(None, (_two_field(x) for x in members))))
            return {
                "designation_type": f"{suffix.lower()}_group",
                "membership_status": "group_member" if members else "unknown_group",
                "mapping_status": "group_unique_two_field" if len(member_two_fields) == 1
                                  else "group_ambiguous",
                "normalized_allele": member_two_fields[0] if len(member_two_fields) == 1 else "",
            }
        mapped = self.deleted_mappings.get(canonical)
        if mapped:
            mapped_two = _two_field(mapped)
            return {
                "designation_type": "allele",
                "membership_status": "deleted_or_renamed",
                "mapping_status": "mapped_to_current" if mapped_two else "deleted_unmapped",
                "normalized_allele": mapped_two,
            }
        member = canonical in self.alleles or two_field in self.two_field_alleles
        return {
            "designation_type": "allele",
            "membership_status": "current_release" if member else "release_incompatible",
            "mapping_status": "unchanged" if member else "unmapped",
            "normalized_allele": two_field if member else "",
        }

    def groups_for_two_field(self, allele: str, kind: str) -> frozenset[str]:
        """Return every official P or G group compatible with a two-field designation."""
        target = _two_field(allele)
        if not target:
            return frozenset()
        normalized_kind = kind.upper()
        if normalized_kind not in {"P", "G"}:
            raise ValueError(f"unsupported HLA group kind: {kind}")
        mapping = self.p_groups if normalized_kind == "P" else self.g_groups
        return frozenset(
            group for group, members in mapping.items()
            if any(_two_field(member) == target for member in members)
        )

    def p_groups_for_two_field(self, allele: str) -> frozenset[str]:
        return self.groups_for_two_field(allele, "P")

    def g_groups_for_two_field(self, allele: str) -> frozenset[str]:
        return self.groups_for_two_field(allele, "G")


def _data_lines(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip() and not line.startswith("#")]


def _read_alleles(path: Path) -> set[str]:
    lines = _data_lines(path)
    if not lines:
        raise ValueError(f"IPD allele list is empty: {path}")
    rows = csv.DictReader(lines)
    alleles = set()
    for row in rows:
        value = row.get("Allele") or row.get("allele") or next(iter(row.values()), "")
        token = _strip_hla(value)
        if "*" in token:
            alleles.add(token)
    if not alleles:
        raise ValueError(f"IPD allele list has no parseable alleles: {path}")
    return alleles


def _read_deleted(path: Path) -> dict[str, str]:
    rows = csv.DictReader(_data_lines(path))
    output = {}
    for row in rows:
        old = _strip_hla(row.get("Allele", ""))
        match = _RENAMED_RE.search(row.get("Description", ""))
        if old and match:
            output[old] = _strip_hla(match.group(1))
    return output


def _read_groups(path: Path, suffix: str) -> dict[str, frozenset[str]]:
    output: dict[str, frozenset[str]] = {}
    for line in _data_lines(path):
        columns = [x.strip() for x in line.split(";")]
        if len(columns) < 3:
            continue
        if columns[2].upper().endswith(suffix):
            member_field, group_field = columns[1], columns[2]
        elif columns[1].upper().endswith(suffix):
            group_field, member_field = columns[1], columns[2]
        else:
            continue
        gene_prefix = columns[0].rstrip("*").upper()
        group = _strip_hla(f"{gene_prefix}*{group_field}")
        members = []
        for value in member_field.split("/"):
            value = value.strip()
            if value:
                members.append(_strip_hla(value if "*" in value else f"{gene_prefix}*{value}"))
        output[group] = frozenset(members)
    return output
