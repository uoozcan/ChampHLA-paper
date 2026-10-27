"""Import the FIMM AML per-caller HLA predictions workbook into a normalized calls table.

    python scripts/import_fimm_caller_predictions.py <workbook.xlsx> \
        --output data/fimm/normalized_caller_calls.tsv \
        --cohort-flow data/fimm/cohort_flow.tsv

The workbook is one row per (specimen, caller, assay) with six allele columns. This script
unpivots it to one row per locus and normalises each call through the same
`normalize_caller_row` the rest of the pipeline uses.

**Why the identifier check is the whole point.** A sibling of this workbook exists with the
`Patient_sample` and `Patient` columns stripped. Because that copy has no way to link a
specimen across assays, the earlier analysis matched specimens *by allele fingerprint* and
then measured HLA concordance on those pairs, which cannot estimate anything. Every
cross-modality number derived that way was withdrawn
(`decisions/20260929_fimm_legacy_withdrawal.json`). This importer therefore refuses to read a
sheet with no specimen identifier, rather than silently reproducing the defect.

Two mappings are load-bearing:

* `Method` is folded to the exact canonical caller spelling. Panel membership in
  `consensus.py` is an exact string match, so `arcasHLA` left as written would be dropped
  from every vote without a word.
* `BulkRNA` and `SCRNA` both normalise to the `rnaseq` modality, and `build_consensus` groups
  on `(cohort, subject, modality, gene)`. They are therefore given **distinct cohort labels**;
  without that, bulk and single-cell calls for one specimen would be pooled into a single
  vote as if they were one assay.
"""
from __future__ import annotations

import argparse
import collections
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import GENES  # noqa: E402
from champhla_confirmation.schema import normalize_caller_row  # noqa: E402

SHEET = "all_results_merged"
SPECIMEN_COLUMN = "Patient_sample"
DONOR_COLUMN = "Patient"

CALLER_NAMES = {"arcashla": "ArcasHLA", "optitype": "OptiType", "spechla": "SpecHLA",
                "hlahd": "HLA-HD", "hla-hd": "HLA-HD", "t1k": "T1K",
                "polysolver": "POLYSOLVER", "kourami": "Kourami", "seq2hla": "Seq2HLA"}

# Assay label -> (modality understood by the pipeline, cohort label that keeps the two RNA
# assays from being pooled into one vote).
ASSAYS = {
    "wes": ("wes", "FIMM-AML-WES"),
    "bulkrna": ("rnaseq", "FIMM-AML-BulkRNA"),
    "scrna": ("rnaseq", "FIMM-AML-SCRNA"),
}

# Specimens excluded by identity, not by content.
ARTEFACT_DONORS = {"align_pair"}
SEPARATE_COHORT_PREFIX = "VX_"   # VenEx, analysed from its own native caller outputs

# `no_match` is a caller saying it found nothing, which is a no-call rather than bad data.
NO_CALL_TOKENS = {"no_match", "nomatch"}
# A bare integer in an allele column is not an allele. In this workbook 89 WES rows carry one,
# always with the neighbouring cells blank and alleles displaced rightwards, which is a column
# shift upstream. They are left to fail normalisation rather than being cleaned away, so the
# defect stays visible in the call statuses instead of turning into a confident wrong call.
NUMERIC_CELL = re.compile(r"^\d+$")

CALLS_FIELDS = [
    "cohort", "subject", "donor", "superpopulation", "modality", "gene", "caller",
    "allele1_raw", "allele2_raw", "allele1", "allele2", "call_status", "no_call_reason",
    "allele1_suffix", "allele2_suffix", "caller_version", "database_version",
    "database_version_basis", "normalization_database_version", "input_reference_build",
    "container_digest", "source_path", "source_sha256", "replicates",
]


class BlockedEvidence(RuntimeError):
    """Raised when the workbook cannot support a non-circular analysis."""


def read_sheet(path: Path, sheet_name: str) -> list[dict[str, str]]:
    """Read one worksheet with the standard library only (no openpyxl dependency)."""
    archive = zipfile.ZipFile(path)
    workbook = archive.read("xl/workbook.xml").decode("utf-8", "replace")
    names = re.findall(r'<sheet[^>]*name="([^"]+)"', workbook)
    if sheet_name not in names:
        raise BlockedEvidence(f"workbook has no sheet {sheet_name!r}; found {names}")

    shared: list[str] = []
    if "xl/sharedStrings.xml" in archive.namelist():
        blocks = re.findall(r"<si>(.*?)</si>",
                            archive.read("xl/sharedStrings.xml").decode("utf-8", "replace"),
                            re.S)
        shared = ["".join(re.findall(r"<t[^>]*>(.*?)</t>", block, re.S)) for block in blocks]

    part = f"xl/worksheets/sheet{names.index(sheet_name) + 1}.xml"
    xml = archive.read(part).decode("utf-8", "replace")

    def parse(raw: str) -> dict[str, str]:
        cells: dict[str, str] = {}
        for match in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*)>(.*?)</c>', raw, re.S):
            column, attributes, body = match.group(1), match.group(2), match.group(3)
            value = re.search(r"<v>(.*?)</v>", body, re.S)
            if not value:
                inline = re.search(r"<t[^>]*>(.*?)</t>", body, re.S)
                if inline:
                    cells[column] = inline.group(1)
                continue
            text = value.group(1)
            if 't="s"' in attributes and text.isdigit() and int(text) < len(shared):
                text = shared[int(text)]
            cells[column] = text
        return cells

    raw_rows = re.findall(r"<row[^>]*>(.*?)</row>", xml, re.S)
    if not raw_rows:
        raise BlockedEvidence(f"sheet {sheet_name!r} is empty")
    header = parse(raw_rows[0])
    return [
        {header[col]: cells.get(col, "").strip()
         for col in header if header[col]}
        for cells in (parse(raw) for raw in raw_rows[1:])
    ]


def canonical_caller(value: str) -> str | None:
    return CALLER_NAMES.get(value.strip().lower().replace(" ", ""))


def import_workbook(path: Path, sheet: str = SHEET) -> tuple[list[dict], list[dict]]:
    rows = read_sheet(path, sheet)
    if not rows:
        raise BlockedEvidence("no data rows")
    present = set(rows[0])
    if SPECIMEN_COLUMN not in present:
        raise BlockedEvidence(
            f"no sample identifier column ({SPECIMEN_COLUMN!r}) in sheet {sheet!r}. "
            "Without it, specimens can only be paired by allele similarity, which is the "
            "circularity recorded in decisions/20260929_fimm_legacy_withdrawal.json. "
            f"Columns present: {sorted(present)}")

    counts: collections.Counter[str] = collections.Counter()
    calls: list[dict] = []
    for row in rows:
        counts["rows_read"] += 1
        specimen = row.get(SPECIMEN_COLUMN, "").strip()
        donor = row.get(DONOR_COLUMN, "").strip()
        if not specimen:
            counts["excluded_no_specimen_id"] += 1
            continue
        if donor in ARTEFACT_DONORS or specimen in ARTEFACT_DONORS:
            counts["excluded_artefact_identifier"] += 1
            continue
        if specimen.startswith(SEPARATE_COHORT_PREFIX) or donor.startswith(SEPARATE_COHORT_PREFIX):
            counts["excluded_separate_venex_cohort"] += 1
            continue

        caller = canonical_caller(row.get("Method", ""))
        if caller is None:
            counts["excluded_unknown_caller"] += 1
            continue
        assay = ASSAYS.get(row.get("Seq_type", "").strip().lower())
        if assay is None:
            counts["excluded_unknown_assay"] += 1
            continue
        modality, cohort = assay

        if not any(row.get(f"HLA_{gene}_{slot}", "") for gene in GENES for slot in (1, 2)):
            counts["rows_with_no_allele_at_any_locus"] += 1
            # Still emitted: a caller that ran and returned nothing is evidence of
            # non-callability, and dropping it would shrink build_consensus's denominator.
        counts["rows_imported"] += 1

        for gene in GENES:
            allele1 = row.get(f"HLA_{gene}_1", "").strip()
            allele2 = row.get(f"HLA_{gene}_2", "").strip()
            for value in (allele1, allele2):
                if NUMERIC_CELL.match(value):
                    counts["locus_cells_numeric_artefact"] += 1
            if allele1.lower() in NO_CALL_TOKENS:
                counts["locus_cells_no_match_token"] += 1
                allele1 = ""
            if allele2.lower() in NO_CALL_TOKENS:
                counts["locus_cells_no_match_token"] += 1
                allele2 = ""
            try:
                call = normalize_caller_row({
                    "cohort": cohort, "subject": specimen, "modality": modality,
                    "gene": gene, "caller": caller,
                    "allele1_raw": allele1, "allele2_raw": allele2,
                    "source_path": path.name,
                })
            except ValueError as error:
                counts["locus_rows_unparsable"] += 1
                call = normalize_caller_row({
                    "cohort": cohort, "subject": specimen, "modality": modality,
                    "gene": gene, "caller": caller, "allele1_raw": "", "allele2_raw": "",
                    "source_path": path.name,
                })
                call["no_call_reason"] = f"unparsable_allele: {error}"
            call["donor"] = donor
            counts[f"locus_rows_{call['call_status']}"] += 1
            calls.append(call)
            counts["locus_rows"] += 1

    calls = collapse_replicates(calls, counts)
    flow = [{"stage": stage, "count": count} for stage, count in sorted(counts.items())]
    return calls, flow


def collapse_replicates(calls: list[dict], counts: collections.Counter) -> list[dict]:
    """Reduce repeated rows for one specimen, caller and locus to a single call.

    The workbook carries more than one row for some (specimen, caller, assay) triples --
    technical repeats sharing a `Patient_sample` identifier. `build_consensus` refuses such
    input outright, and rightly: a caller cannot cast two votes at one locus.

    Where the repeats agree the call is kept once. Where they disagree the caller is recorded
    as **not calling** that locus, with `replicate_conflict` as the reason. Picking one of two
    contradictory genotypes would be inventing a result, and letting the caller vote twice
    would weight it above the rest of the panel. This is the same fail-closed rule
    `champhla_recovery.fimm.collapse_donor_calls` applies to longitudinal specimens.
    """
    grouped: dict[tuple[str, str, str, str], list[dict]] = collections.defaultdict(list)
    for row in calls:
        grouped[(row["cohort"], row["subject"], row["caller"], row["gene"])].append(row)

    collapsed: list[dict] = []
    for key in sorted(grouped):
        rows = grouped[key]
        if len(rows) == 1:
            rows[0]["replicates"] = 1
            collapsed.append(rows[0])
            continue
        counts["replicate_groups"] += 1
        callable_pairs = {
            (row["allele1"], row["allele2"]) for row in rows if row["call_status"] == "callable"
        }
        if len(callable_pairs) > 1:
            counts["replicate_conflicts"] += 1
            conflicted = dict(rows[0])
            conflicted.update({
                "allele1": "", "allele2": "", "allele1_raw": "", "allele2_raw": "",
                "call_status": "no_call", "no_call_reason": "replicate_conflict",
                "replicates": len(rows),
            })
            collapsed.append(conflicted)
            continue
        counts["replicate_agreements"] += 1
        preferred = next((row for row in rows if row["call_status"] == "callable"), rows[0])
        preferred["replicates"] = len(rows)
        collapsed.append(preferred)
    counts["locus_rows_after_replicate_collapse"] = len(collapsed)
    return collapsed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--sheet", default=SHEET)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cohort-flow", type=Path)
    args = parser.parse_args(argv)

    try:
        calls, flow = import_workbook(args.workbook, args.sheet)
    except BlockedEvidence as error:
        print(f"BLOCKED_EVIDENCE: {error}", file=sys.stderr)
        return 2

    write_tsv(args.output, calls, CALLS_FIELDS)
    if args.cohort_flow:
        write_tsv(args.cohort_flow, flow, ["stage", "count"])

    by_cohort = collections.Counter(row["cohort"] for row in calls)
    by_caller = collections.Counter(row["caller"] for row in calls)
    specimens = len({row["subject"] for row in calls})
    donors = len({row["donor"] for row in calls if row["donor"]})
    print(f"imported {len(calls)} locus rows, {specimens} specimens, {donors} donors")
    for cohort, count in sorted(by_cohort.items()):
        print(f"  {cohort:<22} {count:>6} locus rows")
    for caller, count in sorted(by_caller.items()):
        print(f"  {caller:<22} {count:>6} locus rows")
    for row in flow:
        if row["stage"].startswith("excluded") or row["stage"].startswith("rows_with"):
            print(f"  {row['stage']:<36} {row['count']}")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
