#!/usr/bin/env python3
"""Build the truth-free NCI-60 input manifest (decisions/20261026_nci60_v350_regeneration.json).

Every cell line in the Adams et al. 2005 class I table that has public paired reads in
the ENA file reports of SRP150855 (WES) and PRJNA433861 (RNA-seq) gets one run per
assay. Names are joined by ``champhla_recovery.nci60.sample_key``; an unmatched or
ambiguous name stops the build, and read-archive lines without Adams typing are listed.
Only identifiers, URLs and checksums are written; no allele enters the manifest.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from champhla_recovery.nci60 import read_raw, sample_id, sample_key, sha256  # noqa: E402

RESOURCES = ROOT / "resources/nci60"
STUDIES = {"wes": "ena_SRP150855_md5.tsv", "rnaseq": "ena_PRJNA433861_md5.tsv"}
STRATEGY = {"wes": "Targeted-Capture", "rnaseq": "RNA-Seq"}
SUBSAMPLE = {"wes": ("", ""), "rnaseq": ("50000000", "100")}
BATCH_SIZE = 5
FIELDS = ("sample_id", "modality", "population", "input_format", "expected_genome_build",
          "input_url", "index_url", "source_input_md5", "source_index_md5", "source_record",
          "batch_id", "roster_origin", "cell_line", "subsample_pairs", "subsample_seed",
          "unpaired_fastq_bytes")
MAP_FIELDS = ("cell_line", "sample_key", "sample_id", "wes_run", "rnaseq_run")


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build(resources: Path = RESOURCES) -> tuple[list[dict], list[dict], dict]:
    adams = sorted(read_raw(resources / "nci60_classI_raw.tsv"))
    runs: dict[str, dict[str, dict[str, str]]] = {}
    unmatched_archive: dict[str, list[str]] = {}
    for modality, name in STUDIES.items():
        by_key: dict[str, list[dict[str, str]]] = {}
        for row in _rows(resources / name):
            if row["library_strategy"] != STRATEGY[modality] or row["library_layout"] != "PAIRED":
                raise SystemExit(f"unexpected {modality} run type: {row['run_accession']}")
            by_key.setdefault(sample_key(row["sample_alias"]), []).append(row)
        ambiguous = {key: [r["run_accession"] for r in rows]
                     for key, rows in by_key.items() if len(rows) > 1}
        if ambiguous:
            raise SystemExit(f"{modality}: several runs share a cell line: {ambiguous}")
        missing = [line for line in adams if sample_key(line) not in by_key]
        if missing:
            raise SystemExit(f"{modality}: Adams lines without public reads: {missing}")
        runs[modality] = {key: rows[0] for key, rows in by_key.items()}
        unmatched_archive[modality] = sorted(
            rows[0]["sample_alias"] for key, rows in by_key.items()
            if key not in {sample_key(line) for line in adams})

    manifest, name_map = [], []
    excluded: dict[str, dict[str, str]] = {modality: {} for modality in STUDIES}
    for line in adams:
        key = sample_key(line)
        name_map.append({"cell_line": line, "sample_key": key, "sample_id": sample_id(line),
                         "wes_run": runs["wes"][key]["run_accession"],
                         "rnaseq_run": runs["rnaseq"][key]["run_accession"]})
    for modality in STUDIES:
        position = 0
        for line in adams:
            run = runs[modality][sample_key(line)]
            files = list(zip(run["fastq_ftp"].split(";"), run["fastq_md5"].split(";"),
                             run["fastq_bytes"].split(";")))
            first = [f for f in files if f[0].endswith("_1.fastq.gz")]
            second = [f for f in files if f[0].endswith("_2.fastq.gz")]
            unpaired = [f for f in files if f not in first + second]
            if len(first) != 1 or len(second) != 1:
                # The decision admits paired FASTQ only; the line is excluded and listed.
                excluded[modality][line] = f"{run['run_accession']}: no paired FASTQ in the ENA report"
                continue
            urls = [first[0][0], second[0][0]]
            md5s = [first[0][1], second[0][1]]
            pairs, seed = SUBSAMPLE[modality]
            manifest.append({
                "sample_id": sample_id(line), "modality": modality, "population": "NCI-60",
                "input_format": "FASTQ", "expected_genome_build": "none",
                "input_url": "https://" + urls[0], "index_url": "https://" + urls[1],
                "source_input_md5": md5s[0], "source_index_md5": md5s[1],
                "source_record": run["run_accession"],
                "batch_id": f"nci60-{modality}-{position // BATCH_SIZE + 1:03d}",
                "roster_origin": ("Adams et al. 2005 class I table joined to the ENA file "
                                  "report by cell-line name key"),
                "cell_line": line, "subsample_pairs": pairs, "subsample_seed": seed,
                "unpaired_fastq_bytes": str(sum(int(f[2]) for f in unpaired)),
            })
            position += 1
    metadata = {
        "schema_version": 1,
        "purpose": "truth-free public-input manifest for the NCI-60 v3.5.0 regeneration",
        "decision": "decisions/20261026_nci60_v350_regeneration.json",
        "counts": {modality: sum(row["modality"] == modality for row in manifest)
                   for modality in STUDIES},
        "excluded_without_paired_reads": excluded,
        "archive_lines_without_adams_typing": unmatched_archive,
        "truth_firewall": "identifiers, URLs and checksums only; no reference typing",
        "source_files": {name: sha256(resources / name)
                         for name in ("nci60_classI_raw.tsv", *STUDIES.values())},
    }
    return manifest, name_map, metadata


def _write(path: Path, rows: list[dict], fields) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields), delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-tsv", type=Path, default=ROOT / "cohorts/nci60_v350_manifest.tsv")
    parser.add_argument("--map-tsv", type=Path, default=ROOT / "cohorts/nci60_cell_line_map.tsv")
    parser.add_argument("--output-json", type=Path, default=ROOT / "cohorts/nci60_v350_manifest.json")
    args = parser.parse_args(argv)
    manifest, name_map, metadata = build()
    _write(args.output_tsv, manifest, FIELDS)
    _write(args.map_tsv, name_map, MAP_FIELDS)
    metadata["tsv_sha256"] = sha256(args.output_tsv)
    metadata["map_sha256"] = sha256(args.map_tsv)
    with args.output_json.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    print(metadata["counts"], metadata["archive_lines_without_adams_typing"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
