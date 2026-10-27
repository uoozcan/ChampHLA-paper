#!/usr/bin/env python3
"""Build the truth-free input manifest for the frozen confirmatory extension.

The frozen roster (cohorts/frozen_initial_rosters.tsv, pinned by the signed
pre-registration amendment) supplies the WES and RNA-seq subject/modality pairs;
public input metadata is joined from the official 1000 Genomes assay manifest.
No allele, caller output or reference typing enters the manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_development_rerun_manifest import (  # noqa: E402
    DEFAULT_ASSAYS, DEFAULT_BATCH_SIZE, build_rows, read_tsv, write_outputs,
)

FROZEN_ROSTER = ROOT / "cohorts/frozen_initial_rosters.tsv"
FROZEN_ROSTER_SHA256 = "c54a2edaf7225f2bee886ab6e55569878e00fd0040a6e1598da7016a4d399c34"
EXPECTED_COUNTS = {"wes": 89, "rnaseq": 99}
DEFAULT_TSV = ROOT / "cohorts/extension_v350_manifest.tsv"
DEFAULT_JSON = ROOT / "cohorts/extension_v350_manifest.json"
ROSTER_ORIGIN = ("subject/modality identifiers from the frozen extension roster; "
                 "public input metadata joined from the official assay manifest")


def roster_rows(path: Path) -> list[dict[str, str]]:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != FROZEN_ROSTER_SHA256:
        raise SystemExit(f"frozen roster hash differs from the pre-registration pin: {digest}")
    return [row for row in read_tsv(path) if row["modality"] in EXPECTED_COUNTS]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", type=Path, default=FROZEN_ROSTER)
    parser.add_argument("--assay-manifest", type=Path, default=DEFAULT_ASSAYS)
    parser.add_argument("--output-tsv", type=Path, default=DEFAULT_TSV)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    args = parser.parse_args(argv)
    rows = build_rows(roster_rows(args.roster), read_tsv(args.assay_manifest),
                      batch_size=args.batch_size, expected_counts=EXPECTED_COUNTS)
    for row in rows:
        row["batch_id"] = "ext-" + row["batch_id"]
        row["roster_origin"] = ROSTER_ORIGIN
    write_outputs(rows, output_tsv=args.output_tsv, output_json=args.output_json,
                  caller_path=args.roster, assay_path=args.assay_manifest,
                  batch_size=args.batch_size,
                  purpose="truth-free public-input manifest for the frozen v3.5.0 "
                          "confirmatory extension",
                  selection_rule_status="frozen extension roster pinned by "
                                        "decisions/20261013_extension_v350_preregistration_"
                                        "amendment.json")
    print(dict(sorted(Counter(row["modality"] for row in rows).items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
