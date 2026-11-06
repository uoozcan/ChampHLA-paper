"""POST HOC: exact-endpoint agreement with the 2014 type at P-group level, for every method.

decisions/20261105_posthoc_round2_amendment.json. The 2014 typing read exons 2 and 3, so
P-group level is what that assay could measure. A call agrees when it equals the 2014
type or when its alleles pair with it through official IPD-IMGT/HLA 3.65.0 P groups under
the lenient two-field mapping used by the signed adjudication. A missing call does not
agree. This does not replace the primary endpoint.

Writes ``artifacts/development_characterisation/exact_locus_p_group_agreement_posthoc.tsv``.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from adjudicate_reference_discordance import group_compatible  # noqa: E402
from champhla_confirmation.hla_reference import HLAReference  # noqa: E402
from champhla_confirmation.io import write_tsv  # noqa: E402

PER_LOCUS = ROOT / "artifacts" / "development_corrected" / "per_locus_results.tsv"
IPD = ROOT / "resources" / "ipd_imgt_hla" / "3.65.0"
OUTPUT = (ROOT / "artifacts" / "development_characterisation" /
          "exact_locus_p_group_agreement_posthoc.tsv")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def score(per_locus: list[dict[str, str]], reference) -> list[dict[str, object]]:
    tallies: dict[tuple[str, str], list[int]] = {}
    for row in per_locus:
        tally = tallies.setdefault((row["modality"], row["method"]), [0, 0, 0])
        tally[0] += 1
        if row["call_status"] != "callable":
            continue
        call = tuple(sorted((row["allele1"], row["allele2"])))
        truth = tuple(sorted((row["truth_allele1"], row["truth_allele2"])))
        tally[1] += call == truth
        tally[2] += call == truth or group_compatible(reference, call, truth, "P")
    return [{
        "modality": modality, "method": method, "loci": tally[0],
        "exact_correct": tally[1], "p_group_agreement": tally[2],
        "analysis_status": "post_hoc_after_results",
    } for (modality, method), tally in sorted(tallies.items())]


def main() -> int:
    reference = HLAReference.from_files(
        "3.65.0", IPD / "Allelelist.txt",
        p_groups=IPD / "wmda" / "hla_nom_p.txt", g_groups=IPD / "wmda" / "hla_nom_g.txt",
    )
    results = score(read_rows(PER_LOCUS), reference)
    write_tsv(OUTPUT, results)
    print(f"wrote {OUTPUT.relative_to(ROOT)} ({len(results)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
