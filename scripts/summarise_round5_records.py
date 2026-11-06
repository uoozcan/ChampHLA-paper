#!/usr/bin/env python3
"""Round 5, items R1, R3, R4 and R5, from the archived per-sample run records.

decisions/20261106_roihu_descriptions_round5.json. The records were read back once from
the Allas archive of the v3.5.0 development rerun (tar SHA-256 c344844f...) and every file
with a hash in sample_run_provenance.tsv is checked against it before anything is read.

- R1: per caller and assay, the image and its SHA-256, the recorded version, the T1K
  index named in the task logs, the run's command-line overrides, and the code-read
  database source, parameters and input route (main.nf, nextflow.config, conf/ and
  modules/ at workflow commit 66d949d, whose three manifest-hashed files match every run).
- R3: totals of the per-sample rescue tables. They record counts only; no read class.
- R4: per caller and assay, CPU hours, peak memory and failed task attempts per sample,
  from the execution traces of the final launch of each run.
- R5: one complete sample's per-sample provenance files, copied after the hash check.

Development subjects only; no reference typing is read.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
import shutil
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROVENANCE = ROOT / "provenance/development_rerun_v350/truth_free_collection/sample_run_provenance.tsv"
MANIFEST = ROOT / "cohorts/development_rerun_manifest.tsv"
OUTPUT = ROOT / "artifacts/development_characterisation"
REPRESENTATIVE = ROOT / "provenance/development_rerun_v350/representative_sample"

HASHED = {
    "panel_provenance_sha256": "results/pipeline_info/panel_provenance.json",
    "execution_trace_sha256": "results/pipeline_info/execution_trace.txt",
    "caller_dispositions_sha256": "caller_dispositions.tsv",
    "completion_sha256_sha256": "completion_sha256.txt",
    "input_provenance_sha256": "input_provenance.tsv",
    "input_sha256_manifest_sha256": "input_sha256.txt",
    "container_sha256_manifest_sha256": "container_sha256.txt",
    "workflow_files_sha256_manifest_sha256": "workflow_files_sha256.txt",
    "environment_sha256": "environment.txt",
    "nextflow_command_sha256": "nextflow_command.sh",
    "result_files_inventory_sha256": "result_files_sha256.txt",
}
# R5: the per-sample provenance files the signed item names.
REPRESENTATIVE_FILES = ("input_sha256.txt", "input_provenance.tsv", "container_sha256.txt",
                        "workflow_files_sha256.txt", "results/pipeline_info/execution_trace.txt",
                        "result_files_sha256.txt")

PANELS = {"wes": ("HLA-HD", "OptiType", "POLYSOLVER", "SpecHLA", "T1K"),
          "rnaseq": ("arcasHLA", "HLA-HD", "OptiType", "T1K")}
PROCESS_CALLER = {"ARCASHLA_BAM": "arcasHLA", "HLAHD_BAM": "HLA-HD", "HLAHD_FASTQ": "HLA-HD",
                  "OPTITYPE": "OptiType", "POLYSOLVER": "POLYSOLVER", "SPECHLA_BAM": "SpecHLA",
                  "T1K_FASTQ": "T1K"}
CALLER_DIR = {"arcasHLA": "arcashla", "HLA-HD": "hlahd", "OptiType": "optitype",
              "POLYSOLVER": "polysolver", "SpecHLA": "spechla", "T1K": "t1k"}
IMAGE = {"arcasHLA": "arcashla.sif", "HLA-HD": "hlahd.sif", "OptiType": "optitype.sif",
         "POLYSOLVER": "polysolver.sif", "SpecHLA": "native installation", "T1K": "t1k.sif"}

# Read from the workflow at commit 66d949da90861da6cf60cf1d4bee2f094f2518bd.
WES_ROUTE = ("CRAM; reads in chr6:28,000,000-34,000,000, on HLA-allele and alternate contigs "
             "and unplaced, realigned to primary chr6 with BWA-MEM (RESCUE_HLA_READS)")
RNA_ROUTE = "GRCh37 BAM as distributed; no rescue"
CODE_READING = {
    ("wes", "HLA-HD"): ("database inside the image (/app/hlahd.1.4.0; conf/roihu_params.yaml)",
                        "-c 0.95; -m half the read length, at most 50 (modules/hlahd.nf)",
                        WES_ROUTE + "; then the same window as FASTQ (EXTRACT_HLA_AND_CONVERT)"),
    ("wes", "OptiType"): ("reference bundled in the image", "--dna (nextflow.config)",
                          WES_ROUTE + "; then the same window as FASTQ"),
    ("wes", "POLYSOLVER"): ("allele list bundled in the image",
                            "race Unknown, includeFreq 0, insertCalc 0 (modules/polysolver.nf)",
                            WES_ROUTE + "; BAM"),
    ("wes", "SpecHLA"): ("database of the native installation (/projappl/project_2008084/SpecHLAx)",
                         "-u 1, exon reads only (--spechla_exon_only 1 on the command line)",
                         WES_ROUTE + "; BAM"),
    ("wes", "T1K"): ("index built from hla.dat (t1k_hlaidx; conf/roihu_params.yaml)",
                     "run-t1k defaults; index named in the task logs",
                     WES_ROUTE + "; then the same window as FASTQ"),
    ("rnaseq", "arcasHLA"): ("database inside the image", "genotype --min_count 75 "
                             "(modules/arcashla.nf, RNA)", RNA_ROUTE + "; arcasHLA extract on "
                             "the whole BAM"),
    ("rnaseq", "HLA-HD"): ("database inside the image (/app/hlahd.1.4.0)",
                           "-c 0.95; -m half the read length, at most 50; reads first "
                           "filtered with Bowtie2 against the HLA-HD dictionary (modules/hlahd.nf)",
                           RNA_ROUTE + "; whole BAM"),
    ("rnaseq", "OptiType"): ("reference bundled in the image",
                             "--rna (--optitype_seq_type rna on the command line)",
                             RNA_ROUTE + "; chr6:28,000,000-34,000,000 as FASTQ "
                             "(EXTRACT_HLA_AND_CONVERT)"),
    ("rnaseq", "T1K"): ("index built from hla.dat (t1k_hlaidx; conf/roihu_params.yaml)",
                        "run-t1k defaults; index named in the task logs",
                        RNA_ROUTE + "; chr6:28,000,000-34,000,000 as FASTQ"),
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verified_runs(records: Path, provenance: list[dict[str, str]]) -> dict[tuple[str, str], Path]:
    runs = {}
    for row in sorted(provenance, key=lambda r: (r["modality"], r["subject"])):
        folder = records / row["modality"] / row["subject"]
        for column, relative in HASHED.items():
            if sha256(folder / relative) != row[column]:
                raise SystemExit(f"hash mismatch: {folder / relative}")
        runs[(row["modality"], row["subject"])] = folder
    return runs


def duration_hours(text: str) -> float:
    units = {"d": 86400, "h": 3600, "m": 60, "s": 1, "ms": 0.001}
    total = 0.0
    for value, unit in re.findall(r"([\d.]+)\s*(ms|d|h|m|s)", text):
        total += float(value) * units[unit]
    return total / 3600


def memory_gb(text: str) -> float:
    match = re.fullmatch(r"\s*([\d.]+)\s*(B|KB|MB|GB|TB)?\s*", text)
    if not match:
        return 0.0
    # Nextflow prints binary units (1 GB = 1024^3 bytes); report GiB.
    binary = {"B": 1 / 1024 ** 3, "KB": 1 / 1024 ** 2, "MB": 1 / 1024, "GB": 1.0,
              "TB": 1024.0, None: 1 / 1024 ** 3}
    return float(match.group(1)) * binary[match.group(2)]


def trace_costs(trace: Path) -> dict[str, dict[str, float]]:
    """Per caller: CPU hours (realtime x %cpu), peak RSS in GiB and failed attempts."""
    costs: dict[str, dict[str, float]] = defaultdict(lambda: {"cpu_hours": 0.0,
                                                             "peak_gib": 0.0, "failed": 0})
    for row in read_tsv(trace):
        process = row["name"].split(" (")[0]
        caller = PROCESS_CALLER.get(process, "shared steps")
        entry = costs[caller]
        if row["status"] in {"FAILED", "ABORTED"}:
            entry["failed"] += 1
        cpu = float(row["%cpu"].rstrip("%") or 0) / 100 if row["%cpu"] not in {"-", ""} else 0.0
        if row["realtime"] not in {"-", ""}:
            entry["cpu_hours"] += duration_hours(row["realtime"]) * cpu
        if row["peak_rss"] not in {"-", ""}:
            entry["peak_gib"] = max(entry["peak_gib"], memory_gb(row["peak_rss"]))
    return costs


def spread(values: list[float], digits: int) -> dict[str, str]:
    fmt = f"{{:.{digits}f}}"
    return {"median": fmt.format(statistics.median(values)), "min": fmt.format(min(values)),
            "max": fmt.format(max(values))}


def r4_rows(runs: dict[tuple[str, str], Path]) -> list[dict]:
    collected: dict[tuple[str, str], list[dict[str, float]]] = defaultdict(list)
    for (modality, _), folder in runs.items():
        for caller, cost in trace_costs(folder / HASHED["execution_trace_sha256"]).items():
            collected[(modality, caller)].append(cost)
    rows = []
    for (modality, caller) in sorted(collected):
        items = collected[(modality, caller)]
        cpu, peak = spread([i["cpu_hours"] for i in items], 3), spread([i["peak_gib"] for i in items], 2)
        rows.append({"modality": modality, "caller": caller, "runs": len(items),
                     "cpu_hours_median": cpu["median"], "cpu_hours_min": cpu["min"],
                     "cpu_hours_max": cpu["max"], "peak_rss_gib_median": peak["median"],
                     "peak_rss_gib_min": peak["min"], "peak_rss_gib_max": peak["max"],
                     "failed_task_attempts": int(sum(i["failed"] for i in items))})
    return rows


def r3_rows(runs: dict[tuple[str, str], Path]) -> list[dict]:
    tables = [read_tsv(folder / "results/pipeline_info/hla_rescue.tsv")[0]
              for (modality, _), folder in runs.items() if modality == "wes"]
    row = {"modality": "wes", "runs": len(tables),
           "modes": ";".join(sorted({t["mode"] for t in tables}))}
    for column in ("alt_or_hla_contigs", "selected_records", "realigned_pairs", "output_records"):
        values = [int(t[column]) for t in tables]
        row[f"{column}_total"] = sum(values) if column != "alt_or_hla_contigs" else ""
        row[f"{column}_median"] = int(statistics.median(values))
        row[f"{column}_min"], row[f"{column}_max"] = min(values), max(values)
    row["read_classes"] = ("not recorded: the rescue table holds counts only and the realigned "
                           "BAMs were pruned after completion")
    return [row]


def one_value(values: set[str], label: str) -> str:
    if len(values) != 1:
        raise SystemExit(f"{label} differs between runs: {sorted(values)}")
    return next(iter(values))


def caller_version(folder: Path, subject: str, caller: str) -> str:
    if caller == "T1K":
        log = folder / f"results/{subject}/t1k/t1k_out/t1k_stderr.log"
        match = re.search(r"run-t1k (v\S+) begins", log.read_text(encoding="utf-8"))
        return match.group(1) if match else "not recorded"
    text = (folder / f"results/{subject}/{CALLER_DIR[caller]}/versions.yml").read_text(
        encoding="utf-8")
    key = CALLER_DIR[caller]
    match = re.search(rf"^\s+{key}:\s*(.*)$", text, re.MULTILINE)
    value = match.group(1).strip().strip('"') if match else ""
    if not value or value.startswith("usage:"):
        return "not recorded"
    value = value.replace("HLA-HD version ", "")
    if caller == "SpecHLA":
        commit = (folder / "spechla_git_commit.txt").read_text(encoding="utf-8").split()[0]
        value += f" (native installation at git {commit[:7]})"
    return value


def command_overrides(folder: Path, subject: str) -> str:
    words = (folder / "nextflow_command.sh").read_text(encoding="utf-8").split()
    keep = []
    for flag, value in zip(words, words[1:]):
        if flag in {"--spechla_exon_only", "--optitype_seq_type", "--seq_type", "--input_type",
                    "--reference_build", "--run_modality", "--require_full_panel"}:
            keep.append(f"{flag} {value}")
        if flag == "-profile":
            keep.append(f"-profile {value.replace(chr(92), '')}")
    return " ".join(keep).replace(subject, "<subject>")


def r1_rows(runs: dict[tuple[str, str], Path]) -> list[dict]:
    rows = []
    for modality, panel in PANELS.items():
        folders = {s: f for (m, s), f in runs.items() if m == modality}
        for caller in panel:
            digests, versions, indexes, commands = set(), set(), set(), set()
            for subject, folder in folders.items():
                manifest = dict(line.split()[::-1] for line in
                                (folder / "container_sha256.txt").read_text(
                                    encoding="utf-8").splitlines() if line.strip())
                if IMAGE[caller].endswith(".sif"):
                    digests.add(next(v for k, v in manifest.items() if k.endswith("/" + IMAGE[caller])))
                versions.add(caller_version(folder, subject, caller))
                commands.add(command_overrides(folder, subject))
                if caller == "T1K":
                    log = folder / f"results/{subject}/t1k/t1k_out/t1k_stderr.log"
                    indexes |= set(re.findall(r" -f (\S+)", log.read_text(encoding="utf-8")))
            database, parameters, route = CODE_READING[(modality, caller)]
            rows.append({
                "modality": modality, "caller": caller, "runs": len(folders),
                "image": IMAGE[caller],
                "image_sha256": one_value(digests, f"{caller} image") if digests else "",
                "recorded_version": one_value(versions, f"{caller} version"),
                "database_source": database,
                "t1k_index_in_task_logs": one_value(indexes, "T1K index") if indexes else "",
                "parameters": parameters, "input_route": route,
                "command_line_overrides": one_value(commands, "command"),
            })
    return rows


def representative_subject(manifest: list[dict[str, str]]) -> str:
    assays: dict[str, set[str]] = defaultdict(set)
    for row in manifest:
        assays[row["sample_id"]].add(row["modality"])
    return next(s for s in sorted(assays) if {"wes", "rnaseq"} <= assays[s])


def copy_representative(runs: dict[tuple[str, str], Path], subject: str,
                        provenance: list[dict[str, str]], destination: Path) -> list[dict]:
    if destination.exists():
        # Copied once; a later pass only re-checks the copies against their hashes.
        copied = read_tsv(destination / "manifest.tsv")
        for row in copied:
            path = destination / row["modality"] / row["subject"] / row["file"]
            if sha256(path) != row["sha256"]:
                raise SystemExit(f"representative copy changed: {path}")
        return copied
    rows = []
    hashes = {(r["modality"], r["subject"]): r for r in provenance}
    for modality in ("wes", "rnaseq"):
        source = runs[(modality, subject)]
        for relative in REPRESENTATIVE_FILES:
            column = next(c for c, p in HASHED.items() if p == relative)
            data = (source / relative).read_bytes()
            if hashlib.sha256(data).hexdigest() != hashes[(modality, subject)][column]:
                raise SystemExit(f"hash mismatch: {source / relative}")
            target = destination / modality / subject / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / relative, target)
            rows.append({"modality": modality, "subject": subject, "file": relative,
                         "sha256": hashes[(modality, subject)][column],
                         "provenance_column": column})
    return rows


def tally(items: list[dict[str, str]], field: str) -> str:
    return ";".join(f"{value} {sum(r[field] == value for r in items)}"
                    for value in sorted({r[field] for r in items}))


def r2_summary(inputs: list[dict[str, str]]) -> list[dict]:
    """R2 by assay: layouts, builds, median read length and mean exon depth (median, range)."""
    rows = []
    for modality in sorted({row["modality"] for row in inputs}):
        items = [row for row in inputs if row["modality"] == modality]
        lengths = [float(row["median_read_length"]) for row in items]
        depths = [float(row["mean_exon_depth"]) for row in items]
        length, depth = spread(lengths, 0), spread(depths, 1)
        rows.append({"modality": modality, "inputs": len(items),
                     "detected_builds": tally(items, "detected_build"),
                     "layouts": tally(items, "layout"),
                     "read_length_median": length["median"], "read_length_min": length["min"],
                     "read_length_max": length["max"], "exon_depth_median": depth["median"],
                     "exon_depth_min": depth["min"], "exon_depth_max": depth["max"]})
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--records", type=Path,
                        help="extracted development/samples folder (R1, R3, R4, R5)")
    parser.add_argument("--r2-inputs", type=Path, help="input_read_depth.tsv from Roihu (R2)")
    parser.add_argument("--r2-exons", type=Path, help="exon_coordinates.tsv from Roihu (R2)")
    args = parser.parse_args(argv)
    if args.r2_inputs:
        inputs = read_tsv(args.r2_inputs)
        expected = {(r["modality"], r["sample_id"]) for r in read_tsv(MANIFEST)}
        if {(r["modality"], r["subject"]) for r in inputs} != expected or len(inputs) != len(expected):
            raise SystemExit("R2 inputs do not cover the development manifest exactly")
        shutil.copyfile(args.r2_exons, OUTPUT / "round5_exon_coordinates.tsv")
        shutil.copyfile(args.r2_inputs, OUTPUT / "round5_input_read_depth.tsv")
        write_tsv(OUTPUT / "round5_input_read_depth_summary.tsv", r2_summary(inputs))
        return 0
    provenance = read_tsv(PROVENANCE)
    runs = verified_runs(args.records, provenance)
    print(f"verified {len(runs)} runs, {len(runs) * len(HASHED)} files")
    write_tsv(OUTPUT / "round5_caller_deployment.tsv", r1_rows(runs))
    write_tsv(OUTPUT / "round5_rescue_totals.tsv", r3_rows(runs))
    write_tsv(OUTPUT / "round5_run_cost.tsv", r4_rows(runs))
    subject = representative_subject(read_tsv(MANIFEST))
    copied = copy_representative(runs, subject, provenance, REPRESENTATIVE)
    write_tsv(REPRESENTATIVE / "manifest.tsv", copied)
    print(f"representative subject {subject}: {len(copied)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
