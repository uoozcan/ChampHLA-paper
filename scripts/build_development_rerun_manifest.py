#!/usr/bin/env python3
"""Build the truth-free input manifest for the ChampHLA development rerun.

The historical normalized caller table is used only to recover the frozen set of
sample/modality identifiers.  No allele, caller output, or reference typing is
copied into the execution manifest.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CALLS = ROOT / "data/development/normalized_caller_calls.tsv"
DEFAULT_ASSAYS = ROOT / "cohorts/official_1000g_assay_manifest.tsv"
DEFAULT_TSV = ROOT / "cohorts/development_rerun_manifest.tsv"
DEFAULT_JSON = ROOT / "cohorts/development_rerun_manifest.json"
EXPECTED_COUNTS = {"wes": 130, "rnaseq": 106}
DEFAULT_BATCH_SIZE = 5

OUTPUT_FIELDS = [
    "sample_id",
    "modality",
    "population",
    "input_format",
    "expected_genome_build",
    "input_url",
    "index_url",
    "source_input_md5",
    "source_index_md5",
    "source_record",
    "batch_id",
    "roster_origin",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build_rows(
    caller_rows: list[dict[str, str]],
    assay_rows: list[dict[str, str]],
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    expected_counts: dict[str, int] | None = EXPECTED_COUNTS,
) -> list[dict[str, str]]:
    if batch_size < 1:
        raise ValueError("batch_size must be positive")

    roster = sorted({(row["subject"], row["modality"]) for row in caller_rows})
    unsupported = sorted({modality for _, modality in roster} - {"wes", "rnaseq"})
    if unsupported:
        raise ValueError(f"unsupported development modalities: {unsupported}")

    assay_index: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in assay_rows:
        assay_index[(row["sample_id"], row["modality"])].append(row)

    missing = [key for key in roster if not assay_index[key]]
    ambiguous = [key for key in roster if len(assay_index[key]) > 1]
    if missing or ambiguous:
        raise ValueError(
            f"official assay match failure: missing={missing!r}; ambiguous={ambiguous!r}"
        )

    counts = Counter(modality for _, modality in roster)
    if expected_counts is not None and dict(counts) != expected_counts:
        raise ValueError(
            f"development roster counts changed: observed={dict(counts)!r}; "
            f"expected={expected_counts!r}"
        )

    positions = Counter()
    output = []
    for sample_id, modality in roster:
        source = assay_index[(sample_id, modality)][0]
        positions[modality] += 1
        batch_number = (positions[modality] - 1) // batch_size + 1
        output.append(
            {
                "sample_id": sample_id,
                "modality": modality,
                "population": source["population"],
                "input_format": source["format"],
                "expected_genome_build": source["genome_build"],
                "input_url": source["input_url"],
                "index_url": source["index_url"],
                "source_input_md5": source["input_md5"],
                "source_index_md5": source["index_md5"],
                "source_record": source["source_record"],
                "batch_id": f"{modality}-{batch_number:03d}",
                "roster_origin": (
                    "sample/modality identifiers recovered from the historical normalized "
                    "caller table; public input metadata joined from the official assay manifest"
                ),
            }
        )
    return output


def write_outputs(
    rows: list[dict[str, str]],
    *,
    output_tsv: Path,
    output_json: Path,
    caller_path: Path,
    assay_path: Path,
    batch_size: int,
    purpose: str = "truth-free public-input manifest for the v3.5.0 development rerun",
    selection_rule_status: str = (
        "historical rule not reconstructed; convenience/development roster"),
) -> None:
    output_tsv.parent.mkdir(parents=True, exist_ok=True)
    with output_tsv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    counts = Counter(row["modality"] for row in rows)
    batches = Counter(row["batch_id"] for row in rows)
    metadata = {
        "schema_version": 1,
        "purpose": purpose,
        "selection_rule_status": selection_rule_status,
        "truth_firewall": (
            "contains sample identifiers and public input metadata only; no reference typing, "
            "alleles, caller predictions, or outcomes"
        ),
        "batch_size": batch_size,
        "counts": dict(sorted(counts.items())),
        "batch_count": len(batches),
        "source_files": {
            caller_path.resolve().relative_to(ROOT).as_posix(): sha256_file(caller_path),
            assay_path.resolve().relative_to(ROOT).as_posix(): sha256_file(assay_path),
        },
        "tsv_sha256": sha256_file(output_tsv),
    }
    output_json.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--caller-rows", type=Path, default=DEFAULT_CALLS)
    parser.add_argument("--assay-manifest", type=Path, default=DEFAULT_ASSAYS)
    parser.add_argument("--output-tsv", type=Path, default=DEFAULT_TSV)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(
        read_tsv(args.caller_rows),
        read_tsv(args.assay_manifest),
        batch_size=args.batch_size,
    )
    write_outputs(
        rows,
        output_tsv=args.output_tsv,
        output_json=args.output_json,
        caller_path=args.caller_rows,
        assay_path=args.assay_manifest,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
