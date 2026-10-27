#!/usr/bin/env python3
"""Verify the corrected development benchmark headline results.

This check intentionally reads only the regenerated, source-audited result table.
The pre-remediation 390/321-locus verification is retained in repository history;
it is not a valid publication gate because those labels collapsed ambiguous truth.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "artifacts/development_corrected/method_performance.tsv"
OUTPUT = ROOT / "artifacts/verification/development_reproduction.json"
EXPECTED = {
    "wes": {"subjects": 64, "loci": 158, "genotypes_correct": 147},
    "rnaseq": {"subjects": 53, "loci": 125, "genotypes_correct": 114},
}


def main() -> int:
    with SOURCE.open(newline="", encoding="utf-8") as handle:
        primary = {
            row["modality"]: row
            for row in csv.DictReader(handle, delimiter="\t")
            if row["method"] == "SimplePluralityLex" and row["analysis_scope"] == "primary"
        }

    failures: list[str] = []
    observed: dict[str, dict[str, int]] = {}
    for modality, expected in EXPECTED.items():
        if modality not in primary:
            failures.append(f"missing primary result for {modality}")
            continue
        observed[modality] = {}
        for field, value in expected.items():
            actual = int(float(primary[modality][field]))
            observed[modality][field] = actual
            if actual != value:
                failures.append(f"{modality}.{field}: expected {value}, observed {actual}")

    result = {
        "schema_version": "development-reproduction-2",
        "source": str(SOURCE.relative_to(ROOT)),
        "primary_method": "SimplePluralityLex",
        "truth_policy": "unique_public_two_field_truth_only",
        "passed": not failures,
        "observed": observed,
        "failures": failures,
        "historical_wgs_status": "excluded_invalid_input_no_quantitative_result",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if result["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
