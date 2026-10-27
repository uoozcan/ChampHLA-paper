"""The published numbers stay primary and the correction stays visible.

A rule was pre-registered, run once, produced a lower number, and was not adopted.
That sequence is indistinguishable from selecting on the score unless the record
carries its reasoning and both number sets stay in the paper. These tests pin the
parts that can be checked mechanically, so a later edit cannot quietly drop either
the corrected values or the disclosure.
"""
from __future__ import annotations

import csv
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULT_RECORD = ROOT / "decisions" / "20260918_harmonisation_correction_result.json"
PRE_REGISTRATION = ROOT / "decisions" / "20260918_harmonisation_correction.json"
RESULTS = (ROOT / "artifacts" / "harmonisation_correction"
           / "harmonisation_correction_results.tsv")
EVIDENCE = (ROOT / "artifacts" / "harmonisation_correction"
            / "placeholder_homozygosity_evidence.tsv")
MANUSCRIPT = ROOT / "manuscripts" / "benchmark" / "manuscript.md"
SUPPLEMENTARY = ROOT / "manuscripts" / "benchmark" / "supplementary.md"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


@unittest.skipUnless(RESULTS.is_file(), "correction artifacts not generated")
class CorrectionReportedAsRobustnessTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(RESULT_RECORD.read_text(encoding="utf-8"))
        self.results = rows(RESULTS)
        self.manuscript = MANUSCRIPT.read_text(encoding="utf-8")
        self.supplementary = SUPPLEMENTARY.read_text(encoding="utf-8")

    def consensus(self, modality: str, variant: str) -> str:
        row = next(r for r in self.results
                   if r["modality"] == modality and r["scope"] == "consensus"
                   and r["variant"] == variant)
        return f"{row['correct']}/{row['loci']}"

    def test_uncorrected_variant_reproduces_the_published_values(self):
        """Without this the deltas would mean nothing."""
        self.assertEqual(self.consensus("wes", "current"), "365/390")
        self.assertEqual(self.consensus("rnaseq", "current"), "306/321")

    def test_published_values_remain_the_headline(self):
        for value in ("365 of 390", "306 of 321"):
            self.assertIn(value, self.manuscript, f"{value} must remain in the main text")

    def test_corrected_values_are_reported_not_buried(self):
        for value in (self.consensus("wes", "abstain"), self.consensus("rnaseq", "abstain")):
            self.assertIn(value, self.supplementary,
                          f"corrected value {value} must appear in the supplement")

    def test_the_record_discloses_the_deviation_and_the_counter_reading(self):
        adoption = self.record["adoption_decision"]
        self.assertIn("deviation_from_pre_registration", adoption)
        self.assertIn("why_this_is_not_selection_on_the_score", adoption)
        alternative = adoption["the_alternative_reading_and_what_would_support_it"]
        self.assertTrue(alternative["reading"].strip())
        self.assertTrue(alternative["what_would_support_it"].strip())
        self.assertGreaterEqual(len(alternative["what_a_reader_can_check"]), 3)

    def test_both_number_sets_are_retained_in_the_record(self):
        retained = self.record["adoption_decision"]["both_number_sets_retained"]
        self.assertEqual(retained["published_primary"]["wes"], "365 / 390")
        self.assertEqual(retained["corrected_abstain"]["wes"], "364 / 390")
        self.assertEqual(retained["corrected_abstain"]["rnaseq"], "303 / 321")

    def test_the_pre_registration_was_signed_before_the_result_exists(self):
        pre = json.loads(PRE_REGISTRATION.read_text(encoding="utf-8"))
        self.assertEqual(pre["status"], "SIGNED")
        self.assertTrue(pre["author_signoff"]["signed_by"])
        self.assertTrue(pre["written_before_the_run"])

    @unittest.skipUnless(EVIDENCE.is_file(), "evidence artifact not generated")
    def test_the_justification_rests_on_a_measurement_that_exists(self):
        """The enrichment is the argument; it must be in an artifact, not only prose."""
        evidence = {r["modality"]: r for r in rows(EVIDENCE)}
        for modality in ("wes", "rnaseq"):
            affected = float(evidence[modality]["affected_homozygous_rate"])
            baseline = float(evidence[modality]["baseline_homozygous_rate"])
            self.assertGreater(affected, 0.9, f"{modality}: affected loci overwhelmingly homozygous")
            self.assertLess(baseline, 0.2, f"{modality}: baseline homozygosity is low")
            self.assertGreater(affected / baseline, 5, f"{modality}: enrichment")

    def test_the_manuscript_states_the_assay_dependence(self):
        self.assertIn("depend", self.manuscript.lower())
        self.assertIn("92.1%", self.supplementary)
        self.assertIn("97.0%", self.supplementary)


if __name__ == "__main__":
    unittest.main()
