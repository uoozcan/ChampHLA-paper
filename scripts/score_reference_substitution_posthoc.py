"""POST HOC: rescore every method with corrected values substituted at flagged loci.

decisions/20261105_reference_presentation_amendment.json. At each exact-endpoint locus
where the second typing carries an asterisk, the flagged value replaces the 2014 type;
every other locus keeps the 2014 type. Denominators stay fixed, and a missing call
scores incorrect. The flagged values derive from the same exome data, so this table
is not independent and never replaces the primary endpoint.

Reads only development artifacts, so no public-table row outside the development set
is opened here:

* ``artifacts/development_corrected/per_locus_results.tsv``
* ``artifacts/development_characterisation/reference_adjudication_flagged_loci_posthoc.tsv``

Writes ``artifacts/development_characterisation/reference_substitution_posthoc.tsv``.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402

PER_LOCUS = ROOT / "artifacts" / "development_corrected" / "per_locus_results.tsv"
CHARACTERISED = ROOT / "artifacts" / "development_characterisation"
FLAGGED = CHARACTERISED / "reference_adjudication_flagged_loci_posthoc.tsv"
OUTPUT = CHARACTERISED / "reference_substitution_posthoc.tsv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def _pair(first: str, second: str) -> tuple[str, ...] | None:
    return tuple(sorted((first, second))) if first and second else None


def score(per_locus: list[dict[str, str]],
          flagged: list[dict[str, str]]) -> list[dict[str, object]]:
    corrected = {
        (row["modality"], row["subject"], row["gene"]):
            tuple(sorted(row["flagged_second_typing"].split("+")))
        for row in flagged
    }
    truth, calls = {}, {}
    for row in per_locus:
        locus = (row["modality"], row["subject"], row["gene"])
        truth[locus] = _pair(row["truth_allele1"], row["truth_allele2"])
        if row["call_status"] == "callable":
            calls[(row["method"], locus)] = _pair(row["allele1"], row["allele2"])
    missing = sorted(set(corrected) - set(truth))
    if missing:
        raise SystemExit(f"flagged loci outside the exact endpoint: {len(missing)}")
    results = []
    for modality in sorted({locus[0] for locus in truth}):
        loci = sorted(locus for locus in truth if locus[0] == modality)
        methods = sorted({row["method"] for row in per_locus if row["modality"] == modality})
        for method in methods:
            results.append({
                "modality": modality, "method": method, "loci": len(loci),
                "flagged_loci": sum(locus in corrected for locus in loci),
                "exact_correct": sum(calls.get((method, locus)) == truth[locus]
                                     for locus in loci),
                "substituted_correct": sum(
                    calls.get((method, locus)) == corrected.get(locus, truth[locus])
                    for locus in loci),
                "analysis_status": "post_hoc_after_results",
            })
    return results


def main() -> int:
    results = score(read_rows(PER_LOCUS), read_rows(FLAGGED))
    write_tsv(OUTPUT, results)
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(results)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
