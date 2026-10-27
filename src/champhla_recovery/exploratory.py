"""Validation and provenance for the aggregate-only FIMM and VenEx release."""
from __future__ import annotations

import csv
import hashlib
import re
from pathlib import Path

from .fimm import wilson_interval


FIMM_AGGREGATES = (
    "artifacts/fimm_consensus/cohort_flow.tsv",
    "artifacts/fimm_consensus/cross_modality/cross_modality_agreement.tsv",
    "artifacts/fimm_consensus/cross_modality/donor_collapse_conflicts.tsv",
    "artifacts/fimm_consensus/cross_modality/disjoint_caller_sensitivity.tsv",
    "artifacts/fimm_consensus/FIMM-AML-WES/panel3/panel_composition.tsv",
    "artifacts/fimm_consensus/FIMM-AML-BulkRNA/panel3/panel_composition.tsv",
    "artifacts/fimm_consensus/FIMM-AML-SCRNA/panel3/panel_composition.tsv",
    "artifacts/fimm/tierC/cohort_flow.tsv",
    "artifacts/fimm/tierC/bb72_metrics.tsv",
    "artifacts/fimm/tierC/provenance.json",
)
VENEX_AGGREGATES = (
    "artifacts/venex/caller_validation_summary.tsv",
    "artifacts/venex/method_summary.tsv",
    "artifacts/venex/panel_composition.tsv",
    "artifacts/venex/plurality_vs_caller.tsv",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(left - right) <= tolerance


def validate_aggregate_estimates(root: Path) -> list[str]:
    """Independently recount every published aggregate estimate and denominator."""
    failures: list[str] = []
    cross = read_tsv(root / FIMM_AGGREGATES[1])
    for row in cross:
        overlap, agreement = int(row["overlap"]), int(row["agreement"])
        if row.get("eligibility") not in {"all_callable", "contested_both"}:
            failures.append(f"unknown cross-modality eligibility: {row}")
        if overlap == 0:
            if agreement != 0 or any(row[field] for field in ("estimate", "ci_lo", "ci_hi")):
                failures.append(f"non-estimable cross-modality row is not empty: {row}")
            continue
        estimate = agreement / overlap
        low, high = wilson_interval(agreement, overlap)
        if not _close(float(row["estimate"]), estimate):
            failures.append(f"cross-modality estimate mismatch: {row}")
        if low is None or high is None or not _close(float(row["ci_lo"]), low):
            failures.append(f"cross-modality lower interval mismatch: {row}")
        if high is None or not _close(float(row["ci_hi"]), high):
            failures.append(f"cross-modality upper interval mismatch: {row}")

    for relative in FIMM_AGGREGATES[4:7]:
        rows = read_tsv(root / relative)
        total = sum(int(row["loci"]) for row in rows)
        if not rows or total <= 0:
            failures.append(f"empty panel-composition aggregate: {relative}")
        for row in rows:
            expected = int(row["loci"]) / total
            if not _close(float(row["share"]), expected):
                failures.append(f"panel-composition share mismatch: {relative}: {row}")

    bb72 = read_tsv(root / FIMM_AGGREGATES[8])
    for row in bb72:
        tp, tn, fp, fn = (int(row[field]) for field in ("tp", "tn", "fp", "fn"))
        metric = row["metric"]
        parts = {
            "sensitivity": (tp, tp + fn), "specificity": (tn, tn + fp),
            "ppv": (tp, tp + fp), "npv": (tn, tn + fn),
            "accuracy": (tp + tn, tp + tn + fp + fn),
        }
        successes, denominator = parts[metric]
        low, high = wilson_interval(successes, denominator)
        if tp + tn + fp + fn != int(row["informative"]):
            failures.append(f"BB7.2 denominator mismatch: {row}")
        if not _close(float(row["estimate"]), successes / denominator):
            failures.append(f"BB7.2 estimate mismatch: {row}")
        if low is None or high is None or not _close(float(row["ci_lo"]), low):
            failures.append(f"BB7.2 lower interval mismatch: {row}")
        if high is None or not _close(float(row["ci_hi"]), high):
            failures.append(f"BB7.2 upper interval mismatch: {row}")

    venex = read_tsv(root / VENEX_AGGREGATES[3])
    for row in venex:
        denominator = int(row["contested_mutually_callable_loci"])
        dissents = int(row["contested_dissents"])
        if denominator == 0:
            if row["contested_dissent_rate"]:
                failures.append(f"non-estimable VenEx row has an estimate: {row}")
            continue
        low, high = wilson_interval(dissents, denominator)
        if not _close(float(row["contested_dissent_rate"]), dissents / denominator):
            failures.append(f"VenEx dissent mismatch: {row}")
        if low is None or high is None or not _close(float(row["contested_dissent_ci_lo"]), low):
            failures.append(f"VenEx lower interval mismatch: {row}")
        if high is None or not _close(float(row["contested_dissent_ci_hi"]), high):
            failures.append(f"VenEx upper interval mismatch: {row}")
    return failures


def write_checksum_manifest(root: Path, paths: tuple[str, ...], output: Path) -> None:
    rows = []
    for relative in paths:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        count = len(read_tsv(path)) if path.suffix == ".tsv" else 1
        rows.append({"artifact": relative, "sha256": sha256(path), "records": count})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=("artifact", "sha256", "records"),
            delimiter="\t", lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def privacy_failures(root: Path) -> list[str]:
    """Scan exportable FIMM/VenEx artifacts without opening secure ignored tables."""
    failures = []
    forbidden = {
        "real donor identifier": re.compile(r"\b(?:FHRB[._-]?\d|FH\d{2,})\b", re.I),
        "secure absolute path": re.compile(r"(?:/scratch/|/projappl/|[A-Za-z]:\\\\Roihu)"),
    }
    paths = [root / item for item in FIMM_AGGREGATES + VENEX_AGGREGATES]
    paths += [root / "artifacts/fimm_consensus/README.md", root / "artifacts/venex/README.md"]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for label, pattern in forbidden.items():
            if pattern.search(text):
                failures.append(f"{label} in {path.relative_to(root)}")
    return failures


def freeze_exploratory_aggregates(root: Path) -> None:
    failures = validate_aggregate_estimates(root) + privacy_failures(root)
    if failures:
        raise ValueError("; ".join(failures))
    write_checksum_manifest(
        root, FIMM_AGGREGATES, root / "artifacts/fimm_consensus/aggregate_checksums.tsv")
    write_checksum_manifest(
        root, VENEX_AGGREGATES, root / "artifacts/venex/aggregate_checksums.tsv")
