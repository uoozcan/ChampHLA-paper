"""Consensus-versus-comparator head-to-head at the reporting denominator.

Anchors every paired test on the frozen always-call plurality rule
(``SimplePluralityLex``, published as ChampHLA-Consensus) instead of on
TwoThirdsGuardedCC.  Reuses the confirmation package's own correctness,
sign-flip, bootstrap and Holm helpers so the numbers come from the same code
path as ``primary_modality_results.tsv``.

Usage:
    python scripts/consensus_head_to_head.py <joined.tsv> <output_dir> [bootstrap]
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from champhla_confirmation.evaluation import _evaluate_rows, prediction_key
from champhla_confirmation.io import read_tsv, write_tsv
from champhla_confirmation.panels import METHOD_PLURALITY, MODALITIES, REFERENCE_ALIASES
from champhla_confirmation.statistics import (
    cluster_bootstrap_ci,
    exact_cluster_signflip,
    holm_adjust,
    subject_deltas,
)

REFERENCE = METHOD_PLURALITY


def main(joined_path: str, output_dir: str, bootstrap: int = 100000, seed: int = 20260908) -> None:
    evaluated = _evaluate_rows(read_tsv(joined_path))
    by_locus_method = {prediction_key(row): row for row in evaluated}
    loci = sorted({key[:4] for key in by_locus_method})
    methods = sorted({row["method"] for row in evaluated} - REFERENCE_ALIASES)

    rows = []
    for index, modality in enumerate(MODALITIES):
        modality_loci = [locus for locus in loci if locus[2] == modality]
        if not modality_loci:
            continue
        for method_index, method in enumerate(methods):
            covered = [locus for locus in modality_loci
                       if (*locus, method) in by_locus_method]
            if not covered:
                continue
            # Fixed denominator: a comparator absent at a locus scores 0 there.
            paired = []
            for locus in modality_loci:
                reference = by_locus_method.get((*locus, REFERENCE))
                if reference is None:
                    raise ValueError(f"reference method missing at {locus}")
                candidate = by_locus_method.get((*locus, method))
                paired.append({
                    "subject": locus[1],
                    "comparator_correct": int(candidate["is_correct"]) if candidate else 0,
                    "consensus_correct": int(reference["is_correct"]),
                })
            deltas = subject_deltas(paired, "comparator_correct", "consensus_correct")
            ci_lo, ci_hi = cluster_bootstrap_ci(
                paired, "comparator_correct", "consensus_correct",
                # W2.7: seed per (modality, comparator). Seeding per modality alone
                # made every comparator in a modality resample on an identical
                # sequence, so their intervals were perfectly correlated.
                iterations=bootstrap, seed=seed + index * 1000 + method_index)
            consensus_correct = sum(row["consensus_correct"] for row in paired)
            comparator_correct = sum(row["comparator_correct"] for row in paired)
            rows.append({
                "modality": modality,
                "comparator": method,
                "comparator_coverage": len(covered),
                "loci": len(modality_loci),
                "consensus_correct": consensus_correct,
                "comparator_correct": comparator_correct,
                "net": consensus_correct - comparator_correct,
                "delta_points": 100 * (consensus_correct - comparator_correct) / len(modality_loci),
                "wins": sum(row["consensus_correct"] > row["comparator_correct"] for row in paired),
                "losses": sum(row["consensus_correct"] < row["comparator_correct"] for row in paired),
                "ci_lo_points": 100 * ci_lo,
                "ci_hi_points": 100 * ci_hi,
                "p_value": exact_cluster_signflip(deltas.values()),
            })

    # Holm correction is applied within each modality's comparator family.
    corrected = []
    for modality in MODALITIES:
        family = [row for row in rows if row["modality"] == modality]
        if family:
            corrected.extend(holm_adjust(family))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_tsv(out / "consensus_head_to_head.tsv", corrected)
    print(f"wrote {out / 'consensus_head_to_head.tsv'} ({len(corrected)} rows)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2],
         bootstrap=int(sys.argv[3]) if len(sys.argv) > 3 else 100000)
