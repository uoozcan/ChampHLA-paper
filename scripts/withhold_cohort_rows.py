#!/usr/bin/env python3
"""Withhold the FIMM and VenEx aggregate rows from the published provenance copies.

decisions/20261106_public_snapshot_scope.json, item S2. Each archived registry and its
delta move unchanged to provenance/cohort_rows_withheld_20261106/, which the public
snapshot holds back; filtered copies take their place. A registry drops every row whose
cohort is a withheld cohort, and a delta drops every row whose result_id is one of those
registry rows. Every other byte is kept. No value in the withheld rows is read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WITHHELD_COHORTS = ("FIMM_AML_MDS", "VENEX_WES", "FIMM-AML-BulkRNA", "FIMM-AML-SCRNA",
                    "FIMM-AML-WES")
DIRECTORIES = ("provenance/development_rerun_v350",
               "provenance/development_rerun_v350_superseded_20261025")
REGISTRY = "historical_result_registry_pre_v350.tsv"
DELTA = "result_registry_delta.tsv"
DESTINATION = "provenance/cohort_rows_withheld_20261106"
MANIFEST = "provenance/cohort_rows_withheld_20261106.json"
# The pipeline rewrites the current delta at every run, so only its first filtered hash is
# in the manifest; the other three files are static records.
REGENERATED = ("provenance/development_rerun_v350/result_registry_delta.tsv",)


def split(data: bytes) -> tuple[bytes, list[bytes]]:
    """Header and data lines of an LF-terminated TSV with one record per line."""
    if not data.endswith(b"\n") or b"\r" in data or b'"' in data:
        raise SystemExit("expected LF line endings and no quoted fields")
    header, *lines = data.split(b"\n")[:-1]
    return header, lines


def column(header: bytes, name: str) -> int:
    fields = header.split(b"\t")
    return fields.index(name.encode())


def filter_registry(data: bytes) -> tuple[bytes, set[str]]:
    header, lines = split(data)
    cohort, result_id = column(header, "cohort"), column(header, "result_id")
    withheld = {cohort.encode() for cohort in WITHHELD_COHORTS}
    kept, dropped = [], set()
    for line in lines:
        fields = line.split(b"\t")
        if fields[cohort] in withheld:
            dropped.add(fields[result_id].decode())
        else:
            kept.append(line)
    return b"\n".join([header, *kept]) + b"\n", dropped


def filter_delta(data: bytes, dropped: set[str]) -> tuple[bytes, int]:
    header, lines = split(data)
    result_id = column(header, "result_id")
    kept = [line for line in lines if line.split(b"\t")[result_id].decode() not in dropped]
    return b"\n".join([header, *kept]) + b"\n", len(lines) - len(kept)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rows(data: bytes) -> int:
    return len(split(data)[1])


def withhold(root: Path) -> dict:
    destination = root / DESTINATION
    if destination.exists() or (root / MANIFEST).exists():
        raise SystemExit(f"already withheld: {DESTINATION}; this step runs once")
    entries, planned = [], []
    for directory in DIRECTORIES:
        registry = (root / directory / REGISTRY).read_bytes()
        delta = (root / directory / DELTA).read_bytes()
        filtered_registry, dropped = filter_registry(registry)
        filtered_delta, removed = filter_delta(delta, dropped)
        for name, before, after in ((REGISTRY, registry, filtered_registry),
                                    (DELTA, delta, filtered_delta)):
            path = f"{directory}/{name}"
            planned.append((path, before, after))
            entries.append({
                "path": path,
                "withheld_copy": f"{DESTINATION}/{path}",
                "rows_before": rows(before), "rows_after": rows(after),
                "sha256_before": sha256(before), "sha256_after": sha256(after),
            })
        if removed > len(dropped):
            raise SystemExit(f"{directory}: delta repeats a withheld result_id")
    for path, before, after in planned:
        copy = destination / path
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(before)
        if sha256(copy.read_bytes()) != sha256(before):
            raise SystemExit(f"withheld copy differs: {copy}")
        (root / path).write_bytes(after)
    manifest = {
        "schema_version": "champhla-cohort-rows-withheld-1",
        "decision_record": "decisions/20261106_public_snapshot_scope.json",
        "rule": ("A registry drops every row whose cohort is one of withheld_cohorts; a delta "
                 "drops every row whose result_id is one of the rows dropped from the registry "
                 "in the same directory. Every other byte is unchanged."),
        "withheld_cohorts": list(WITHHELD_COHORTS),
        "withheld_copies": f"{DESTINATION}/ (private repository only; held back from the "
                           "public snapshot)",
        "files": entries,
    }
    (root / MANIFEST).write_bytes(
        (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)
    manifest = withhold(args.root)
    for entry in manifest["files"]:
        print(f"{entry['path']}: {entry['rows_before']} -> {entry['rows_after']} rows; "
              f"{entry['sha256_before'][:12]} -> {entry['sha256_after'][:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
