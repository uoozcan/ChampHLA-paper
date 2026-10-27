"""Check that every panel member actually produced calls, and fail if not.

Run this where a pilot writes its caller outputs. It replaces an existence-and-
checksum check that let SpecHLA pass while emitting a header and no calls, turning
a five-caller WES panel into four with CALLERS_COMPLETE still written.

    python scripts/validate_caller_outputs.py <results_dir> --modality wes \
        [--sample HG00096] [--output validation.tsv] [--require-complete]

<results_dir> is the directory holding one subdirectory per caller, each containing
that caller's native summary, as the pipeline lays it out under
results/<sample>/<caller>/<sample>_<caller>.txt.

Exit status is 0 when every panel member produced calls, 2 otherwise. With
--require-complete the command also refuses to leave a CALLERS_COMPLETE marker in
place next to a panel that is not complete.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.caller_validation import validate_panel  # noqa: E402
from champhla_confirmation.io import write_tsv  # noqa: E402
from champhla_confirmation.panels import PANELS  # noqa: E402

# Directory name under results/<sample>/ -> canonical caller name used by the panels.
DIRECTORY_TO_CALLER = {
    "hlahd": "HLA-HD",
    "optitype": "OptiType",
    "polysolver": "POLYSOLVER",
    "spechla": "SpecHLA",
    "t1k": "T1K",
    "arcashla": "ArcasHLA",
    "kourami": "Kourami",
    "seq2hla": "Seq2HLA",
}


def discover(results_dir: Path, sample: str | None) -> dict[str, Path]:
    """Map caller name to its native summary file."""
    outputs: dict[str, Path] = {}
    for child in sorted(results_dir.iterdir()):
        if not child.is_dir():
            continue
        caller = DIRECTORY_TO_CALLER.get(child.name.lower())
        if caller is None:
            continue
        candidates = sorted(child.glob(f"*_{child.name.lower()}.txt"))
        if sample:
            preferred = [p for p in candidates if p.name.startswith(f"{sample}_")]
            candidates = preferred or candidates
        if candidates:
            outputs[caller] = candidates[0]
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("results_dir", type=Path)
    parser.add_argument("--modality", required=True, choices=sorted(PANELS))
    parser.add_argument("--sample")
    parser.add_argument("--output", type=Path,
                        help="write the per-caller validation table here")
    parser.add_argument("--require-complete", action="store_true",
                        help="remove any CALLERS_COMPLETE marker when the panel is incomplete")
    args = parser.parse_args(argv)

    if not args.results_dir.is_dir():
        print(f"no such directory: {args.results_dir}", file=sys.stderr)
        return 2

    outputs = discover(args.results_dir, args.sample)
    result = validate_panel(outputs, args.modality)

    print(f"modality {args.modality}: {result['callers_with_calls']} of "
          f"{result['panel_size']} panel members produced calls")
    for row in result["rows"]:
        marker = " " if row["in_panel"] else "."
        detail = f"  {row['detail']}" if row["detail"] else ""
        print(f" {marker} {row['caller']:<12}{row['status']:<11}"
              f"{row['call_rows']:>4} call rows{detail}")

    if args.output:
        write_tsv(args.output, [
            {"caller": r["caller"], "in_panel": r["in_panel"], "status": r["status"],
             "call_rows": r["call_rows"], "genes_called": r["genes_called"],
             "detail": r["detail"]}
            for r in result["rows"]
        ])
        print(f"wrote {args.output}")

    if result["panel_complete"]:
        return 0

    print(f"PANEL INCOMPLETE: {', '.join(result['failures'])}", file=sys.stderr)
    if args.require_complete:
        marker = args.results_dir.parent / "CALLERS_COMPLETE"
        if marker.exists():
            marker.unlink()
            print(f"removed misleading marker {marker}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
