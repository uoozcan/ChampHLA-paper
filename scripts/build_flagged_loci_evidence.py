"""POST HOC: join published typing at the ten flagged vote-error loci to the adjudication.

decisions/20261105_posthoc_round2_amendment.json. The curated input records what each
published source reports at these loci and nothing else. The 2014 type, the vote and the
P-group flag come from the signed adjudication artifact, so they are not retyped. The
sources were checked only at flagged loci, so this cannot show that other loci are correct.

Writes ``artifacts/development_characterisation/flagged_loci_evidence_posthoc.tsv``.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from champhla_confirmation.io import write_tsv  # noqa: E402

CURATED = ROOT / "resources" / "reference_adjudication" / "flagged_loci_published_typing.tsv"
CHARACTERISED = ROOT / "artifacts" / "development_characterisation"
ADJUDICATION = CHARACTERISED / "reference_adjudication.tsv"
OUTPUT = CHARACTERISED / "flagged_loci_evidence_posthoc.tsv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def build(curated: list[dict[str, str]],
          adjudication: list[dict[str, str]]) -> list[dict[str, str]]:
    wes = {(row["subject"], row["gene"]): row for row in adjudication
           if row["modality"] == "wes"}
    rnaseq = {(row["subject"], row["gene"]) for row in adjudication
              if row["modality"] == "rnaseq"}
    evidence = {(row["subject"], row["gene"]): row for row in curated}
    if set(evidence) != set(wes) or not rnaseq <= set(wes):
        raise SystemExit("curated published typing does not match the WES vote-error loci")
    results = []
    for locus in sorted(wes):
        row, source = wes[locus], evidence[locus]
        results.append({
            "subject": row["subject"], "gene": row["gene"],
            "superpopulation": row["superpopulation"],
            "reference_2014": row["reference"], "vote": row["consensus"],
            "vote_error_assays": "WES and RNA-seq" if locus in rnaseq else "WES",
            "p_group_equal": row["p_group_equivalent_to_reference"],
            "erlich_2011": source["erlich_2011"],
            "trusight_buchkovich_2017": source["trusight_buchkovich_2017"],
            "assembly": source["assembly"],
            "abi_rached_confirmation": source["abi_rached_confirmation"],
            "analysis_status": "post_hoc_after_results",
        })
    return results


def main() -> int:
    results = build(read_rows(CURATED), read_rows(ADJUDICATION))
    write_tsv(OUTPUT, results)
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(results)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
