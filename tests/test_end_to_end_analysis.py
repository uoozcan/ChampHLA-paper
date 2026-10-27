"""A stub end-to-end pass over the analysis chain.

Caller execution needs Nextflow, Singularity and the caller containers, so it can
only be exercised on the cluster. Everything downstream of the callers is pure
Python and can be exercised here: harmonised caller rows -> consensus -> freeze ->
truth join -> evaluation -> registry -> claim audit.

The point is that the chain holds together on realistic shapes, and that the
gates fire on the conditions they exist to catch. Numbers here are fixtures, not
results.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from champhla_confirmation.consensus import build_consensus
from champhla_confirmation.evaluation import evaluate, join_truth
from champhla_confirmation.freeze import freeze_bundle
from champhla_confirmation.io import write_tsv
from champhla_confirmation.panels import METHOD_BASELINE, METHOD_GUARDED_CC, METHOD_PLURALITY
from champhla_recovery.manuscript import audit_claims

GENES = ("A", "B", "C")
WES_PANEL = ("HLA-HD", "OptiType", "POLYSOLVER", "SpecHLA", "T1K")
RNA_PANEL = ("ArcasHLA", "HLA-HD", "OptiType", "T1K")


def truth_pair(gene: str, index: int) -> tuple[str, str]:
    return (f"{gene}*01:{index % 9 + 1:02d}", f"{gene}*02:{index % 7 + 1:02d}")


def wrong_pair(gene: str, index: int) -> tuple[str, str]:
    return (f"{gene}*01:{index % 9 + 1:02d}", f"{gene}*11:{index % 5 + 1:02d}")


def caller_row(subject, modality, gene, caller, pair):
    return {"cohort": "FIXTURE", "subject": subject, "modality": modality, "gene": gene,
            "caller": caller,
            "allele1": pair[0] if pair else "", "allele2": pair[1] if pair else "",
            "call_status": "callable" if pair else "missing",
            "caller_version": "1", "source_path": "", "source_sha256": ""}


def method_row(row, method):
    return {"cohort": row["cohort"], "subject": row["subject"], "modality": row["modality"],
            "gene": row["gene"], "method": method,
            "allele1": row.get("allele1", ""), "allele2": row.get("allele2", ""),
            "call_status": row.get("call_status", "callable"),
            "decision_reason": row.get("decision_reason", ""),
            "superpopulation": "EUR"}


def build_fixture(n_subjects: int = 9):
    """One dissenting caller per locus, so the plurality is correct but not unanimous."""
    caller_rows, truth_rows = [], []
    for index in range(n_subjects):
        subject = f"S{index:03d}"
        for modality, panel in (("wes", WES_PANEL), ("rnaseq", RNA_PANEL)):
            for gene in GENES:
                right = truth_pair(gene, index)
                wrong = wrong_pair(gene, index)
                for position, caller in enumerate(panel):
                    # The last caller dissents; on every third locus it abstains
                    # instead, which exercises the missing-call path.
                    if position == len(panel) - 1:
                        pair = None if index % 3 == 0 else wrong
                    else:
                        pair = right
                    caller_rows.append(caller_row(subject, modality, gene, caller, pair))
                truth_rows.append({
                    "cohort": "FIXTURE", "subject": subject, "modality": modality,
                    "gene": gene, "truth_allele1": right[0], "truth_allele2": right[1],
                    "truth_status": "resolved", "truth_source": "fixture",
                    "source_sha256": "0" * 64,
                })
    return caller_rows, truth_rows


class EndToEndAnalysisTests(unittest.TestCase):
    def test_chain_runs_and_consensus_beats_the_dissenting_caller(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src").mkdir()
            (root / "src" / "stub.py").write_text("X = 1\n", encoding="utf-8")

            caller_rows, truth_rows = build_fixture()
            consensus = build_consensus(caller_rows)
            self.assertTrue(consensus, "consensus produced no rows")

            # build_consensus already emits the plurality and two-thirds rows with
            # their own method field. The evaluator also requires a guarded-CC row
            # per locus, which here simply mirrors the plurality call.
            predictions = list(consensus)
            for row in consensus:
                if row["method"] == METHOD_PLURALITY:
                    predictions.append({**row, "method": METHOD_GUARDED_CC})
            for row in caller_rows:
                predictions.append(method_row(row, f"Caller:{row['caller']}"))
            self.assertIn(METHOD_BASELINE, {r["method"] for r in predictions})

            predictions_path = root / "predictions.tsv"
            truth_path = root / "truth.tsv"
            write_tsv(predictions_path, predictions)
            write_tsv(truth_path, truth_rows)

            # Freeze before truth is joined -- the firewall the provenance model rests on.
            manifest = root / "freeze.json"
            freeze_bundle(root, {"predictions": predictions_path}, manifest)

            joined = root / "joined.tsv"
            join_manifest = root / "join.json"
            payload = join_truth(str(predictions_path), str(truth_path), str(manifest),
                                 str(joined), str(join_manifest))
            self.assertEqual(payload["loci"], len(truth_rows))

            out_dir = root / "evaluation"
            result = evaluate(str(joined), str(out_dir), bootstrap=200,
                              allow_partial=True, mode="discovery")

            self.assertEqual(sorted(result["modalities_evaluated"]), ["rnaseq", "wes"])
            self.assertFalse(result["all_modalities_present"])
            # Discovery mode can never retain a headline: external prerequisites fail.
            self.assertFalse(result["headline_retained"])
            self.assertEqual(result["status"], "discovery_only")

            # The dissenting caller must be beaten by the vote it dissents from.
            secondary = {(r["modality"], r["comparator"]): r
                         for r in _rows(out_dir / "secondary_method_results.tsv")}
            for modality, panel in (("wes", WES_PANEL), ("rnaseq", RNA_PANEL)):
                row = secondary[(modality, f"Caller:{panel[-1]}")]
                self.assertGreater(float(row["delta_points"]), 0,
                                   f"{modality}: vote should beat the dissenting caller")

            # Within a modality no comparator may appear twice, and the reference
            # must never appear as its own comparator -- the defect that inflated
            # every Holm family when the plurality rule was emitted under two names.
            for modality in ("wes", "rnaseq"):
                names = [c for m, c in secondary if m == modality]
                self.assertEqual(len(names), len(set(names)),
                                 f"{modality}: duplicate comparator in the Holm family")
                self.assertNotIn(METHOD_PLURALITY, names)

    def test_audit_rejects_a_manuscript_citing_an_unregistered_result(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "artifact.tsv"
            artifact.write_text("x\n1\n", encoding="utf-8")
            registry = root / "registry.tsv"
            registry.write_text(
                "result_id\tcohort\tmodality\tmethod\tanalysis_status\tvalidity\tsubjects\t"
                "loci\tcorrect\taccuracy\tartifact_path\tartifact_sha256\tabstract_allowed\t"
                "claim_boundary\n", encoding="utf-8")
            claims = root / "claims.tsv"
            claims.write_text(
                "claim_id\tdraft\tsection\tclaim\tstatus\tevidence_result_id\taction\n"
                "C1\tbenchmark\tResults\tok\tsupported\t\tretain\n", encoding="utf-8")
            manuscript = root / "benchmark" / "manuscript.md"
            manuscript.parent.mkdir()
            manuscript.write_text("We report [RESULT:NOT_REGISTERED].\n", encoding="utf-8")

            result = audit_claims(str(manuscript), str(registry), str(claims),
                                  str(root / "audit.json"), str(root))
            self.assertTrue(any("unknown result reference" in f for f in result["failures"]))
            self.assertFalse(result["submission_ready"])


def _rows(path: Path) -> list[dict[str, str]]:
    import csv
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


if __name__ == "__main__":
    unittest.main()
