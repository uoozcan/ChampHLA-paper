from __future__ import annotations

import unittest

from champhla_confirmation.io import canonical_allele, normalize_diploid_call
from champhla_confirmation.parsers import parse_caller_pair


class CallerParserTests(unittest.TestCase):
    def test_optitype_matrix(self):
        text = "A1\tA2\tB1\tB2\tC1\tC2\nA*01:01\tA*02:01\tB*07:02\tB*08:01\tC*07:01\tC*07:02\n"
        self.assertEqual(("A*01:01", "A*02:01"), parse_caller_pair("OptiType", text, "A"))

    def test_line_wrappers_for_all_wgs_callers(self):
        for caller in ("HLA-HD", "Kourami", "SpecHLA", "T1K"):
            with self.subTest(caller=caller):
                text = "HLA-A\tA*03:01:01\tA*24:02:01\n"
                self.assertEqual(("A*03:01", "A*24:02"), parse_caller_pair(caller, text, "A"))

    def test_homozygous_duplicate(self):
        self.assertEqual(("C*07:02", "C*07:02"),
                         parse_caller_pair("HLA-HD", "C\tC*07:02\tC*07:02\n", "C"))

    def test_explicit_singleton_homozygote_is_accepted(self):
        self.assertEqual(("C*07:02", "C*07:02"),
                         parse_caller_pair("HLA-HD", "C homozygous C*07:02\n", "C"))

    def test_unqualified_singleton_abstains(self):
        self.assertIsNone(parse_caller_pair("HLA-HD", "C\tC*07:02\t-\n", "C"))

    def test_ambiguous_many_pairs_fails(self):
        text = "A*01:01 A*02:01 A*03:01"
        self.assertIsNone(parse_caller_pair("T1K", text, "A"))

    def test_pseudogene_suffix_is_not_misparsed_as_class_i(self):
        text = ("A\tHLA-A*03:01:01\t-\n"
                "DMA\tHLA-DMA*01:01:01\tHLA-DMA*01:02:01\n"
                "DOB\tHLA-DOB*01:01:01\tHLA-DOB*01:01:03\n")
        self.assertIsNone(parse_caller_pair("HLA-HD", text, "A"))
        self.assertIsNone(parse_caller_pair("HLA-HD", text, "B"))

    def test_expression_suffix_is_retained_as_metadata_but_not_in_two_field_endpoint(self):
        result = normalize_diploid_call("A*02:01:01:02N", "A*24:02:01", "A")
        self.assertEqual("complete", result["call_status"])
        self.assertEqual(("A*02:01", "A*24:02"), result["pair"])
        self.assertEqual("N", result["allele1_suffix"])
        self.assertEqual("A*02:01", canonical_allele("A*02:01N", "A"))

    def test_partial_placeholder_has_explicit_state(self):
        result = normalize_diploid_call("B*07:02", "NA", "B")
        self.assertEqual("partial", result["call_status"])
        self.assertEqual("undetermined_second_allele", result["no_call_reason"])
        self.assertIsNone(result["pair"])

    def test_ambiguous_and_wrong_gene_calls_fail_closed(self):
        ambiguous = normalize_diploid_call("A*01:01/A*01:02", "A*02:01", "A")
        wrong_gene = normalize_diploid_call("B*07:02", "A*02:01", "A")
        self.assertEqual("ambiguous", ambiguous["call_status"])
        self.assertEqual("invalid", wrong_gene["call_status"])


if __name__ == "__main__":
    unittest.main()
