"""Caller-native homozygosity (decisions/20261008_singleton_native_homozygosity.json)."""
from __future__ import annotations

import unittest

from champhla_confirmation.io import declares_native_homozygosity
from champhla_confirmation.parsers import parse_caller_pair
from champhla_confirmation.schema import normalize_caller_row


def caller_row(caller: str, raw1: str, raw2: str, gene: str = "A") -> dict[str, str]:
    return {"subject": "HG00096", "caller": caller, "modality": "rnaseq", "gene": gene,
            "allele1_raw": raw1, "allele2_raw": raw2}


class NativeDeclarationTests(unittest.TestCase):
    def test_hlahd_hyphen_and_arcashla_singleton_declare_homozygosity(self):
        self.assertTrue(declares_native_homozygosity("HLA-HD", "HLA-A*02:01:01", "-"))
        self.assertTrue(declares_native_homozygosity("ArcasHLA", "A*02:01:01", "-"))

    def test_hlahd_not_typed_is_a_failure_not_a_homozygote(self):
        self.assertFalse(declares_native_homozygosity("HLA-HD", "HLA-A*02:01:01", "Not typed"))

    def test_t1k_placeholder_is_ambiguous_and_never_declares(self):
        self.assertFalse(declares_native_homozygosity("T1K", "HLA-A*02:01:01", "-"))
        self.assertFalse(declares_native_homozygosity("T1K", "HLA-A*02:01:01", "."))

    def test_two_alleles_or_none_is_not_a_singleton_declaration(self):
        self.assertFalse(declares_native_homozygosity("HLA-HD", "A*02:01", "A*03:01"))
        self.assertFalse(declares_native_homozygosity("HLA-HD", "-", "-"))


class NormalizeCallerRowTests(unittest.TestCase):
    def test_native_policy_completes_declared_homozygote_with_provenance(self):
        row = normalize_caller_row(caller_row("HLA-HD", "HLA-A*02:01:01", "-"),
                                   singleton_policy="native_declaration")
        self.assertEqual(("callable", "A*02:01", "A*02:01"),
                         (row["call_status"], row["allele1"], row["allele2"]))
        self.assertEqual("caller_native_declaration", row["homozygosity_basis"])

    def test_abstain_policy_keeps_every_singleton_partial(self):
        row = normalize_caller_row(caller_row("HLA-HD", "HLA-A*02:01:01", "-"))
        self.assertEqual("partial", row["call_status"])
        self.assertEqual("", row["homozygosity_basis"])

    def test_native_policy_still_abstains_for_t1k(self):
        row = normalize_caller_row(caller_row("T1K", "HLA-A*02:01:01", "-"),
                                   singleton_policy="native_declaration")
        self.assertEqual("partial", row["call_status"])

    def test_two_reported_alleles_are_labelled_as_such(self):
        row = normalize_caller_row(caller_row("OptiType", "A*01:01", "A*02:01"),
                                   singleton_policy="native_declaration")
        self.assertEqual("two_alleles", row["homozygosity_basis"])

    def test_unknown_policy_fails(self):
        with self.assertRaises(ValueError):
            normalize_caller_row(caller_row("HLA-HD", "A*02:01", "-"), singleton_policy="complete")


class NativeSummaryParserTests(unittest.TestCase):
    HLAHD = "HLA-A\tHLA-A*03:01:01\t-\t412\t412\nHLA-B\tHLA-B*07:02:01\tHLA-B*08:01:01\t9\t9\n"
    ARCAS = "# arcasHLA results for S1\nGene\tAllele1\tAllele2\nHLA-C\tC*07:02:01\t-\n"

    def test_parser_matches_normalizer_under_each_policy(self):
        self.assertIsNone(parse_caller_pair("HLA-HD", self.HLAHD, "A"))
        self.assertEqual(("A*03:01", "A*03:01"),
                         parse_caller_pair("HLA-HD", self.HLAHD, "A", "native_declaration"))
        self.assertEqual(("C*07:02", "C*07:02"),
                         parse_caller_pair("ArcasHLA", self.ARCAS, "C", "native_declaration"))

    def test_heterozygous_lines_are_unchanged_by_the_policy(self):
        self.assertEqual(parse_caller_pair("HLA-HD", self.HLAHD, "B"),
                         parse_caller_pair("HLA-HD", self.HLAHD, "B", "native_declaration"))

    def test_t1k_summary_line_still_abstains(self):
        text = "HLA-A\tHLA-A*03:01:01\t-\n"
        self.assertIsNone(parse_caller_pair("T1K", text, "A", "native_declaration"))


if __name__ == "__main__":
    unittest.main()
