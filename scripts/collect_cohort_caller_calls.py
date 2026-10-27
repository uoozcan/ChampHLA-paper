"""Turn a cohort's native caller outputs into a normalized calls table.

This is the generalised sibling of `champhla_confirmation.wgs_pilot.collect_full_cram_wgs_pilot`,
which does the same job but is hardcoded to the WGS pilot's modality, cohort, panel and
`CALLERS_COMPLETE` / `caller_output_validation.tsv` preconditions that only that pilot writes.

    python scripts/collect_cohort_caller_calls.py <caller_root> \
        --cohort VenEx-WES --modality wes \
        --output data/venex/normalized_caller_calls.tsv \
        --validation-output data/venex/caller_validation.tsv

`<caller_root>` holds one directory per sample, each holding one directory per caller, laid
out as the pipeline writes it:

    <caller_root>/<sample>/<caller>/<sample>_<caller>.txt

**A caller is never silently dropped.** `build_consensus` divides by `callable_tools`, the
number of panel callers that actually produced a call, so a caller that vanishes because its
file was missing or unparsable would shrink the denominator and quietly make the consensus
look better supported than it is. Every panel member therefore gets a row for every locus,
carrying `call_status` and an explicit `no_call_reason` when it did not call.

That matters here concretely: in the VenEx cohort every POLYSOLVER summary contains
`# WARNING: POLYSOLVER produced no output` and no data rows, so POLYSOLVER is present as a
file and absent as evidence. This is the same defect class that
`champhla_confirmation.caller_validation` was written for after SpecHLA emitted a header and
no calls, turning a five-caller panel into four with the completion marker still in place.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.caller_validation import validate_caller  # noqa: E402
from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import GENES, PANELS  # noqa: E402
from champhla_confirmation.parsers import parse_caller_pair  # noqa: E402
from champhla_confirmation.schema import normalize_caller_row  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_caller_outputs import DIRECTORY_TO_CALLER  # noqa: E402

CALLER_TO_DIRECTORY = {caller: directory for directory, caller in DIRECTORY_TO_CALLER.items()}

CALLS_FIELDS = [
    "cohort", "subject", "superpopulation", "modality", "gene", "caller",
    "allele1_raw", "allele2_raw", "allele1", "allele2", "call_status", "no_call_reason",
    "allele1_suffix", "allele2_suffix", "caller_version", "database_version",
    "database_version_basis", "normalization_database_version", "input_reference_build",
    "container_digest", "source_path", "source_sha256", "caller_version_provenance",
    "container_provenance",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def find_summary(sample_dir: Path, sample: str, directory: str) -> Path | None:
    """Locate a caller's native summary, preferring the exact <sample>_<caller>.txt name.

    The recursive fallback exists because some callers nest their summary (OptiType writes
    `<sample>/<sample>_result.tsv` beside it, HLA-HD writes a per-locus `result/` tree).
    Intermediate per-locus files are deliberately not eligible: on one VenEx sample HLA-HD
    alone emits 60 of them, and picking one yields a partial genotype that looks like a call.
    """
    caller_dir = sample_dir / directory
    if not caller_dir.is_dir():
        return None
    exact = caller_dir / f"{sample}_{directory}.txt"
    if exact.is_file():
        return exact
    candidates = sorted(caller_dir.glob(f"*_{directory}.txt"))
    preferred = [path for path in candidates if path.name.startswith(f"{sample}_")]
    chosen = preferred or candidates
    return chosen[0] if chosen else None


def collect_sample(sample_dir: Path, cohort: str, modality: str,
                   panel: tuple[str, ...]) -> tuple[list[dict], list[dict]]:
    sample = sample_dir.name
    calls: list[dict] = []
    validation: list[dict] = []
    for caller in panel:
        directory = CALLER_TO_DIRECTORY.get(caller)
        summary = find_summary(sample_dir, sample, directory) if directory else None
        if summary is None:
            for gene in GENES:
                calls.append(_row(cohort, sample, modality, gene, caller, None, None,
                                  "", "", "no_caller_output"))
            validation.append({"subject": sample, "caller": caller, "status": "missing",
                               "genes_called": 0, "detail": "no summary file",
                               "source_path": "", "source_sha256": ""})
            continue

        text = summary.read_text(encoding="utf-8", errors="replace")
        digest = sha256(summary)
        called = 0
        for gene in GENES:
            pair = parse_caller_pair(caller, text, gene)
            if pair:
                called += 1
                calls.append(_row(cohort, sample, modality, gene, caller, pair[0], pair[1],
                                  str(summary), digest, ""))
            else:
                calls.append(_row(cohort, sample, modality, gene, caller, None, None,
                                  str(summary), digest, "no_pair_in_caller_output"))
        detail = validate_caller(summary)
        validation.append({
            "subject": sample, "caller": caller, "status": str(detail.get("status", "")),
            "genes_called": called,
            "detail": str(detail.get("detail", "")),
            "source_path": str(summary), "source_sha256": digest,
        })
    return calls, validation


def _row(cohort: str, sample: str, modality: str, gene: str, caller: str,
         allele1: str | None, allele2: str | None, source_path: str,
         source_sha256: str, reason: str) -> dict:
    # parse_caller_pair already returns a canonical two-field pair, so the raw and normalized
    # alleles coincide here exactly as they do in wgs_pilot.collect_full_cram_wgs_pilot. The
    # caller's own higher-field designation is not preserved through this path.
    row = normalize_caller_row({
        "cohort": cohort, "subject": sample, "modality": modality, "gene": gene,
        "caller": caller, "allele1_raw": allele1 or "", "allele2_raw": allele2 or "",
        "source_path": source_path, "source_sha256": source_sha256,
    })
    if reason:
        row["no_call_reason"] = reason
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("caller_root", type=Path)
    parser.add_argument("--cohort", required=True)
    parser.add_argument("--modality", required=True, choices=sorted(PANELS))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--validation-output", type=Path)
    parser.add_argument("--sample", action="append", default=[],
                        help="restrict to these samples; repeat for several")
    args = parser.parse_args(argv)

    if not args.caller_root.is_dir():
        print(f"no such directory: {args.caller_root}", file=sys.stderr)
        return 2

    panel = PANELS[args.modality]
    wanted = set(args.sample)
    sample_dirs = [
        child for child in sorted(args.caller_root.iterdir())
        if child.is_dir() and (not wanted or child.name in wanted)
        and any((child / directory).is_dir() for directory in DIRECTORY_TO_CALLER)
    ]
    if not sample_dirs:
        print(f"no sample directories under {args.caller_root}", file=sys.stderr)
        return 2

    calls: list[dict] = []
    validation: list[dict] = []
    for sample_dir in sample_dirs:
        sample_calls, sample_validation = collect_sample(
            sample_dir, args.cohort, args.modality, panel)
        calls.extend(sample_calls)
        validation.extend(sample_validation)

    write_tsv(args.output, calls, CALLS_FIELDS)
    if args.validation_output:
        write_tsv(args.validation_output, validation,
                  ["subject", "caller", "status", "genes_called", "detail",
                   "source_path", "source_sha256"])

    expected = len(sample_dirs) * len(panel) * len(GENES)
    callable_rows = sum(1 for row in calls if row["call_status"] == "callable")
    by_caller = {
        caller: sum(1 for row in calls
                    if row["caller"] == caller and row["call_status"] == "callable")
        for caller in panel
    }
    print(f"cohort {args.cohort} modality {args.modality}: "
          f"{len(sample_dirs)} samples x {len(panel)} panel callers x {len(GENES)} genes")
    print(f"  rows written {len(calls)} (expected {expected}), callable {callable_rows}")
    for caller in panel:
        share = by_caller[caller] / (len(sample_dirs) * len(GENES))
        flag = "  <-- contributes nothing" if by_caller[caller] == 0 else ""
        print(f"    {caller:<12} callable {by_caller[caller]:>5}  ({share:.1%}){flag}")
    print(f"wrote {args.output}")

    if len(calls) != expected:
        print(f"ROW COUNT MISMATCH: {len(calls)} != {expected}; a caller was dropped "
              f"instead of being recorded as a no-call", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
