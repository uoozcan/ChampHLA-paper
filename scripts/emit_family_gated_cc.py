"""Emit FamilyGatedCC rows so it can be judged in the comparator family.

TwoThirdsGuardedCC and MVFlooredCC are Champion-Challenger variants and both sit in
the comparator family. FamilyGatedCC is another, so reporting it outside the Holm
correction while its siblings sit inside would be inconsistent, and would invite the
obvious question of why this one was exempt.

Entering it enlarges each modality's family by one, which raises every adjusted p
value slightly. That is the honest cost of adding a comparator and is preferable to
quoting it uncorrected.

The rows are derived from the existing ChampionChallenger rows: where an override was
backed by callers spanning fewer than the required number of families, the champion
call is restored; otherwise the CC call stands.

    python scripts/emit_family_gated_cc.py <joined.tsv> <output.tsv>
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.families import (DEFAULT_MIN_SUPPORTING_FAMILIES,  # noqa: E402
                                            supporting_families)
from champhla_confirmation.io import write_tsv  # noqa: E402

CC = "ChampionChallenger"
GATED = "FamilyGatedCC"
OVERRIDE = "challenger_override"


def cell(row: dict[str, str], key: str) -> str:
    return (row.get(key) or "").strip()


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    source, target = Path(argv[1]), Path(argv[2])

    with source.open(newline="", encoding="utf-8", errors="replace") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    if any(r["method"] == GATED for r in rows):
        raise SystemExit(f"{GATED} rows are already present in {source}")

    emitted = reverted = 0
    new_rows = []
    for row in rows:
        if row["method"] != CC:
            continue
        gated = dict(row)
        gated["method"] = GATED
        if cell(row, "decision_reason") == OVERRIDE:
            families = supporting_families(cell(row, "supporting_callers"))
            if len(families) < DEFAULT_MIN_SUPPORTING_FAMILIES:
                champion = cell(row, "champion_pair")
                if "+" in champion:
                    a, b = champion.split("+", 1)
                    gated["allele1"], gated["allele2"] = a, b
                    gated["call_status"] = "callable"
                else:
                    gated["allele1"] = gated["allele2"] = ""
                    gated["call_status"] = "missing"
                gated["decision_reason"] = "family_gate_rejected_override"
                reverted += 1
        emitted += 1
        new_rows.append(gated)

    if not new_rows:
        raise SystemExit(f"no {CC} rows found in {source}")

    write_tsv(target, rows + new_rows)
    print(f"wrote {target}")
    print(f"  {emitted} {GATED} rows, {reverted} overrides reverted by the gate")
    print(f"  total rows {len(rows)} -> {len(rows) + len(new_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
