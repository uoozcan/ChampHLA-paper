"""Measure the harmonisation defect, per caller, on the cohort the paper reports.

When a caller could not determine a second allele it emitted a placeholder, and
harmonisation replaced that placeholder with a copy of the first allele, turning a
partial call into a confident homozygous genotype. A second mechanism compounds it:
two distinct high-resolution alleles can collapse to the same two-field group.

This reads the harmonised benchmark rows, which keep the raw caller output beside
the harmonised result, and writes a **truth-free** counts table. The input carries
reference-typing columns and is therefore not version-controlled; the output
contains no truth and is the artifact the supplement is generated from.

Earlier reporting of this defect used ``benchmark_*_all_samples`` (7,235 WES rows
over 138 samples) while the paper reports on ``benchmark_*_truthbacked`` (2,655 WES
rows over 130 samples), which is why its WES rates did not describe this cohort.

Usage:
    python scripts/harmonisation_defect_table.py <wes_rows.tsv> <rna_rows.tsv> <out_dir>
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import PANELS  # noqa: E402

# Tokens a caller uses to say "I could not determine this allele".
PLACEHOLDERS = {"", "-", ".", "NA", "na", "N/A", "none", "None", "no", "not typed"}

TRUTH_PREFIX = "truth"
MODALITY = {"wes": "wes", "rna": "rnaseq"}


def _cell(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def measure(path: Path, modality: str) -> list[dict]:
    """Per-caller defect counts. Reads no truth column."""
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    panel = set(PANELS[modality])
    per_tool: dict[str, dict[str, int]] = {}
    for row in rows:
        tool = _cell(row, "tool")
        raw1, raw2 = _cell(row, "allele1_raw"), _cell(row, "allele2_raw")
        out1, out2 = _cell(row, "allele1"), _cell(row, "allele2")
        record = per_tool.setdefault(tool, {
            "rows": 0, "placeholder": 0, "manufactured": 0, "collapsed": 0,
            "homozygous": 0,
        })
        record["rows"] += 1
        homozygous = bool(out1) and out1 == out2
        if homozygous:
            record["homozygous"] += 1
        if raw2 in PLACEHOLDERS:
            record["placeholder"] += 1
            if homozygous:
                record["manufactured"] += 1
        elif raw1 and raw2 and raw1 != raw2 and homozygous:
            # Two distinct alleles reported, collapsing to one two-field group.
            record["collapsed"] += 1

    out = []
    for tool in sorted(per_tool):
        record = per_tool[tool]
        false_hom = record["manufactured"] + record["collapsed"]
        out.append({
            "modality": modality,
            "caller": tool,
            "in_panel": int(tool in panel),
            "rows": record["rows"],
            "placeholder_second_allele": record["placeholder"],
            "manufactured_homozygous": record["manufactured"],
            "collapsed_to_one_group": record["collapsed"],
            "false_homozygous": false_hom,
            "false_homozygous_rate": f"{false_hom / record['rows']:.6f}" if record["rows"] else "",
            "homozygous_calls": record["homozygous"],
        })
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__)
        return 2
    wes_path, rna_path, out_dir = Path(argv[1]), Path(argv[2]), Path(argv[3])

    rows: list[dict] = []
    for path, modality in ((wes_path, "wes"), (rna_path, "rnaseq")):
        if not path.is_file():
            raise SystemExit(f"missing input: {path}")
        with path.open(encoding="utf-8", errors="replace") as handle:
            header = handle.readline()
        if "allele2_raw" not in header:
            raise SystemExit(f"{path} has no allele2_raw column; the raw caller "
                             "output is required to identify the defect")
        rows.extend(measure(path, modality))

    # The output must carry no reference typing.
    for row in rows:
        leaked = [k for k in row if k.lower().startswith(TRUTH_PREFIX)]
        if leaked:
            raise SystemExit(f"refusing to write truth-bearing columns: {leaked}")

    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "harmonisation_defect_counts.tsv"
    write_tsv(target, rows)
    print(f"wrote {target} ({len(rows)} rows)")

    for modality in ("wes", "rnaseq"):
        subset = [r for r in rows if r["modality"] == modality]
        panel = [r for r in subset if r["in_panel"]]
        for label, group in (("all callers", subset), ("panel only", panel)):
            total = sum(r["rows"] for r in group)
            false_hom = sum(r["false_homozygous"] for r in group)
            if total:
                print(f"  {modality:<7} {label:<12} {false_hom:>4} / {total:<5} "
                      f"= {100 * false_hom / total:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
