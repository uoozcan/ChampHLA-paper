#!/usr/bin/env python3
"""Compare plurality with each caller on loci where that caller has a stored row."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "artifacts" / "development_corrected" / "per_locus_results.tsv"
OUTPUT = (
    ROOT / "artifacts" / "development_characterisation"
    / "caller_mutually_available_comparison.tsv"
)
PLURALITY = "SimplePluralityLex"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    rows = read(INPUT)
    consensus = {
        (row["subject"], row["modality"], row["gene"]): row
        for row in rows if row["method"] == PLURALITY
    }
    callers = sorted({
        (row["modality"], row["method"])
        for row in rows if row["method"].startswith("Caller:")
    })
    output: list[dict[str, object]] = []
    for modality, method in callers:
        caller = {
            (row["subject"], row["modality"], row["gene"]): row
            for row in rows if row["modality"] == modality and row["method"] == method
        }
        loci = sorted(key for key in consensus if key[1] == modality)
        mutual = [key for key in loci if key in caller]
        absent = [key for key in loci if key not in caller]
        wins = sum(
            int(consensus[key]["correct"]) > int(caller[key]["correct"]) for key in mutual
        )
        losses = sum(
            int(consensus[key]["correct"]) < int(caller[key]["correct"]) for key in mutual
        )
        output.append({
            "modality": modality,
            "caller": method.removeprefix("Caller:"),
            "fixed_loci": len(loci),
            "stored_rows": len(mutual),
            "absent_rows": len(absent),
            "absent_subject_gene": ";".join(f"{key[0]}:HLA-{key[2]}" for key in absent),
            "consensus_correct_fixed": sum(int(consensus[key]["correct"]) for key in loci),
            "caller_correct_fixed": sum(
                int(caller[key]["correct"]) if key in caller else 0 for key in loci
            ),
            "mutually_available_loci": len(mutual),
            "consensus_correct_mutually_available": sum(
                int(consensus[key]["correct"]) for key in mutual
            ),
            "caller_correct_mutually_available": sum(
                int(caller[key]["correct"]) for key in mutual
            ),
            "consensus_wins_mutually_available": wins,
            "consensus_losses_mutually_available": losses,
            "ties_mutually_available": len(mutual) - wins - losses,
            "historical_task_state_for_absent_rows": (
                "unrecoverable_from_stored_artifacts" if absent else "not_applicable"
            ),
        })
    write(OUTPUT, output)
    print(f"generated {len(output)} caller mutually-available comparisons")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
