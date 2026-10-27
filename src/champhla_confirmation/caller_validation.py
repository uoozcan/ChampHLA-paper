"""Validate that a caller actually produced calls, not merely a file.

The pilot run framework validated caller output by checking a file existed and
recording its sha256. Two callers passed that check while emitting nothing at all:
on 2026-09-16, SpecHLA and POLYSOLVER each wrote a header-only file for both pilot
subjects, so a five-caller WES panel silently became three, and `CALLERS_COMPLETE`
was still written.

A checksum proves a file has not changed. It says nothing about whether the file
contains a result. This module answers the second question.

The check is deliberately format-agnostic: every supported caller writes allele
designations in the standard `GENE*FIELD:FIELD` form, so counting lines that carry
one works across native formats without a parser per caller.
"""
from __future__ import annotations

import re
from pathlib import Path

from .panels import GENES, PANELS

# HLA allele designation: HLA-A*01:01:01, A*29:02, DRB1*07:01 ...
ALLELE = re.compile(r"\b(?:HLA-)?([A-Z]{1,5}[0-9]{0,2})\*\d+(?::\d+)+")

# A leading '#' marks a comment in every native format used here.
COMMENT = "#"


def count_calls(path: Path) -> tuple[int, set[str]]:
    """Return the number of rows carrying an allele, and the genes seen."""
    rows = 0
    genes: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith(COMMENT):
            continue
        found = ALLELE.findall(stripped)
        if found:
            rows += 1
            genes.update(found)
    return rows, genes


def validate_caller(path: Path, expect_genes: tuple[str, ...] = GENES) -> dict:
    """Validate one caller's native summary."""
    if not path.is_file():
        return {"caller": path.stem, "status": "missing", "call_rows": 0,
                "genes_called": "", "detail": f"no such file: {path}"}

    call_rows, genes = count_calls(path)
    class_i = sorted(g for g in genes if g in expect_genes)

    if call_rows == 0:
        return {"caller": path.stem, "status": "empty", "call_rows": 0,
                "genes_called": "",
                "detail": ("file exists and is non-empty but contains no allele "
                           "designation: the caller produced no call")}
    missing = [g for g in expect_genes if g not in class_i]
    if missing:
        return {"caller": path.stem, "status": "incomplete", "call_rows": call_rows,
                "genes_called": ",".join(class_i),
                "detail": f"no call for {','.join(missing)}"}
    return {"caller": path.stem, "status": "ok", "call_rows": call_rows,
            "genes_called": ",".join(class_i), "detail": ""}


def validate_panel(outputs: dict[str, Path], modality: str) -> dict:
    """Validate every panel member for a modality.

    ``outputs`` maps caller name to its native summary file. Callers outside the
    modality's panel are reported but cannot fail the panel, since they do not vote.
    """
    if modality not in PANELS:
        raise ValueError(f"unknown modality: {modality}")
    panel = PANELS[modality]

    rows = []
    for caller in sorted(outputs):
        record = validate_caller(outputs[caller])
        record["caller"] = caller
        record["in_panel"] = int(caller in panel)
        rows.append(record)

    present = {r["caller"] for r in rows}
    for caller in panel:
        if caller not in present:
            rows.append({"caller": caller, "in_panel": 1, "status": "missing",
                         "call_rows": 0, "genes_called": "",
                         "detail": "panel member produced no output file"})

    failures = [r for r in rows if r["in_panel"] and r["status"] != "ok"]
    return {
        "modality": modality,
        "panel": list(panel),
        "rows": sorted(rows, key=lambda r: (-r["in_panel"], r["caller"])),
        "failures": [f"{r['caller']}:{r['status']}" for r in failures],
        "panel_complete": not failures,
        "callers_with_calls": sum(1 for r in rows if r["in_panel"] and r["status"] == "ok"),
        "panel_size": len(panel),
    }
