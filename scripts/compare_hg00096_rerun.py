"""Compare HG00096's stored development caller calls with re-runs of the workflow.

Two comparisons: the September 2026 re-run (WES from an HLA-region pre-extract,
RNA-seq from FASTQ), and whole-exome runs of releases 3.3.0 and 3.4.0
(provenance/hg00096_wes_release), which isolate the alt-contig read loss fixed in 3.4.0.

Both sides go through the paper's normalizer (native-declaration singleton rule), so a
difference is a difference in the caller's reported genotype, not in parsing. Class I
panel callers only. Truth-free: no reference typing is read.

    python scripts/compare_hg00096_rerun.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import GENES, PANELS  # noqa: E402
from champhla_confirmation.schema import normalize_caller_row  # noqa: E402

# The stored calls are the archived outputs from before the v3.5.0 study run;
# data/development now holds the study-run calls (decisions/20261106_posthoc_round3_amendment.json, A1).
STORED = (ROOT / "provenance" / "development_rerun_v350" / "historical_inputs_pre_v350"
          / "normalized_caller_calls.tsv")
RERUN = ROOT / "provenance" / "hg00096_rerun"
OUTPUT = ROOT / "artifacts" / "development_characterisation" / "hg00096_rerun_comparison.tsv"
RELEASES = ROOT / "provenance" / "hg00096_wes_release"
RELEASE_RUNS = {"v3_3_0": "v3.3.0_job2121882_aggregated_calls.tsv",
                "v3_4_0": "v3.4.0_job2128858_aggregated_calls.tsv"}
RELEASE_OUTPUT = (ROOT / "artifacts" / "development_characterisation"
                  / "hg00096_wes_release_comparison.tsv")
RNA_RELEASE = ROOT / "provenance" / "hg00096_rna_release" / "v3.4.0_job2129989_aggregated_calls.tsv"
RNA_RELEASE_OUTPUT = (ROOT / "artifacts" / "development_characterisation"
                      / "hg00096_rna_release_comparison.tsv")
TOOL = {"hlahd": "HLA-HD", "optitype": "OptiType", "polysolver": "POLYSOLVER",
        "spechla": "SpecHLA", "t1k": "T1K", "arcashla": "ArcasHLA"}


def _state(row: dict) -> str:
    return f"{row['allele1']}+{row['allele2']}" if row["call_status"] == "callable" else row["call_status"]


def _release_calls(path: Path, modality: str = "wes") -> dict[tuple[str, str], str]:
    calls = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="	"):
            caller = TOOL.get(row["tool"])
            if row["gene"] not in GENES or caller not in PANELS[modality]:
                continue
            calls[(row["gene"], caller)] = _state(normalize_caller_row(
                {"subject": "HG00096", "caller": caller, "modality": modality,
                 "gene": row["gene"], "allele1_raw": row["allele1"],
                 "allele2_raw": row["allele2"]},
                "rerun", singleton_policy="native_declaration"))
    return calls


def compare_wes_releases(stored: dict) -> list[dict]:
    """Stored WES calls against whole-exome runs of releases 3.3.0 and 3.4.0."""
    runs = {name: _release_calls(RELEASES / file) for name, file in RELEASE_RUNS.items()}
    rows = []
    for (modality, gene, caller) in sorted(stored):
        if modality != "wes":
            continue
        row = {"gene": gene, "caller": caller, "stored": _state(stored[(modality, gene, caller)])}
        for name, calls in runs.items():
            row[name] = calls.get((gene, caller), "absent")
            row[f"agree_{name}"] = str(int(row[name] == row["stored"]))
        rows.append(row)
    write_tsv(RELEASE_OUTPUT, rows, ["gene", "caller", "stored", *runs,
                                     *(f"agree_{name}" for name in runs)])
    for name in runs:
        print(f"wes whole exome {name}: {sum(r[f'agree_{name}'] == '1' for r in rows)}/"
              f"{len(rows)} caller-gene calls agree with the stored calls")
    return rows


def compare_rna_release(stored: dict) -> list[dict]:
    """Stored RNA-seq calls against release 3.4.0 on the Geuvadis BAM the extension stages."""
    calls = _release_calls(RNA_RELEASE, "rnaseq")
    rows = []
    for (modality, gene, caller) in sorted(stored):
        if modality != "rnaseq":
            continue
        before = _state(stored[(modality, gene, caller)])
        after = calls.get((gene, caller), "absent")
        rows.append({"gene": gene, "caller": caller, "stored": before, "v3_4_0_bam": after,
                     "agree_v3_4_0_bam": str(int(before == after))})
    write_tsv(RNA_RELEASE_OUTPUT, rows, ["gene", "caller", "stored", "v3_4_0_bam",
                                         "agree_v3_4_0_bam"])
    print(f"rnaseq BAM v3_4_0: {sum(r['agree_v3_4_0_bam'] == '1' for r in rows)}/{len(rows)} "
          "caller-gene calls agree with the stored calls")
    return rows


def main() -> int:
    with STORED.open(encoding="utf-8") as handle:
        stored = {(r["modality"], r["gene"], r["caller"]): r
                  for r in csv.DictReader(handle, delimiter="\t") if r["subject"] == "HG00096"}
    rerun = {}
    for name in ("wes_aggregated_calls.tsv", "rna_aggregated_calls.tsv"):
        with (RERUN / name).open(encoding="utf-8") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                modality = "rnaseq" if row["modality"] in {"rna", "rnaseq"} else row["modality"]
                caller = TOOL.get(row["tool"])
                if row["gene"] not in GENES or caller not in PANELS[modality]:
                    continue
                rerun[(modality, row["gene"], caller)] = normalize_caller_row(
                    {"subject": "HG00096", "caller": caller, "modality": modality,
                     "gene": row["gene"], "allele1_raw": row["allele1"],
                     "allele2_raw": row["allele2"]},
                    "rerun", singleton_policy="native_declaration")
    rows = []
    for key in sorted(stored):
        modality, gene, caller = key
        before = _state(stored[key])
        after = _state(rerun[key]) if key in rerun else "not_rerun"
        rows.append({"modality": modality, "gene": gene, "caller": caller,
                     "stored": before, "rerun": after,
                     "agree": str(int(key in rerun and before == after))})
    write_tsv(OUTPUT, rows, ["modality", "gene", "caller", "stored", "rerun", "agree"])
    for modality in ("wes", "rnaseq"):
        part = [r for r in rows if r["modality"] == modality and r["rerun"] != "not_rerun"]
        print(f"{modality}: {sum(r['agree'] == '1' for r in part)}/{len(part)} re-run caller-gene calls agree")
    compare_wes_releases(stored)
    compare_rna_release(stored)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
