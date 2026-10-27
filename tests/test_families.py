"""The algorithm-family diversity gate.

The gate exists because callers within a family share an alignment strategy and
reference representation, so their agreement is correlated rather than independent.
Every override it reverted in the measurement was backed by two callers from one
family, and three of those four overrides were wrong.

The pipeline's own implementation of this gate has no test coverage, so these pin the
behaviour the measurement depends on.
"""
from __future__ import annotations

import unittest

from champhla_confirmation.families import (DEFAULT_MIN_SUPPORTING_FAMILIES, family_of,
                                            passes_family_gate, supporting_families)


class FamilyMapTests(unittest.TestCase):
    def test_the_three_families(self):
        self.assertEqual(family_of("OptiType"), "alignment")
        self.assertEqual(family_of("POLYSOLVER"), "alignment")
        self.assertEqual(family_of("SpecHLA"), "assembly_graph")
        self.assertEqual(family_of("T1K"), "alignment_em")
        self.assertEqual(family_of("ArcasHLA"), "kmer")

    def test_caller_naming_is_tolerated(self):
        """HLA-HD appears as both HLA-HD and hlahd across the pipeline."""
        self.assertEqual(family_of("HLA-HD"), "alignment")
        self.assertEqual(family_of("hlahd"), "alignment")
        self.assertEqual(family_of("  optitype  "), "alignment")

    def test_an_unknown_caller_gets_its_own_family(self):
        """Fail open. Merging an unknown caller would make the gate weaker than it looks."""
        self.assertNotEqual(family_of("NewCaller"), family_of("OptiType"))
        self.assertNotEqual(family_of("NewCaller"), family_of("OtherNewCaller"))


class FamilyGateTests(unittest.TestCase):
    def test_two_callers_from_one_family_do_not_pass(self):
        """The case the gate exists for, and the only case it fired on."""
        self.assertFalse(passes_family_gate(["HLA-HD", "POLYSOLVER"]))   # both alignment
        self.assertFalse(passes_family_gate(["HLA-HD", "OptiType"]))     # both alignment
        self.assertTrue(passes_family_gate(["SpecHLA", "T1K"]))          # distinct mechanisms

    def test_two_callers_from_different_families_pass(self):
        self.assertTrue(passes_family_gate(["OptiType", "T1K"]))
        self.assertTrue(passes_family_gate(["ArcasHLA", "T1K"]))
        self.assertTrue(passes_family_gate(["POLYSOLVER", "SpecHLA"]))

    def test_three_callers_from_one_family_still_do_not_pass(self):
        """A count of callers would pass this; that is the point of counting families."""
        callers = ["OptiType", "HLA-HD", "POLYSOLVER"]
        self.assertEqual(len(callers), 3)
        self.assertFalse(passes_family_gate(callers))

    def test_a_comma_separated_field_is_accepted(self):
        """supporting_callers arrives as a joined string in the prediction rows."""
        self.assertEqual(supporting_families("HLA-HD,POLYSOLVER"), {"alignment"})
        self.assertTrue(passes_family_gate("ArcasHLA,T1K"))
        self.assertFalse(passes_family_gate("HLA-HD,OptiType"))

    def test_empty_support_never_passes(self):
        for empty in ("", "   ", [], ",,"):
            self.assertFalse(passes_family_gate(empty))

    def test_the_threshold_is_two_and_is_configurable(self):
        self.assertEqual(DEFAULT_MIN_SUPPORTING_FAMILIES, 2)
        self.assertTrue(passes_family_gate(["HLA-HD", "POLYSOLVER"], minimum=1))
        self.assertFalse(passes_family_gate(["OptiType", "T1K"], minimum=3))

    def test_historical_supporter_groups_are_reclassified_by_method(self):
        """T1K is not an assembly-graph method and must add a distinct family."""
        observed = [
            ("HLA-HD,POLYSOLVER", {"alignment"}),
            ("SpecHLA,T1K", {"assembly_graph", "alignment_em"}),
            ("HLA-HD,OptiType", {"alignment"}),
        ]
        for supporters, expected_families in observed:
            families = supporting_families(supporters)
            self.assertEqual(families, expected_families, supporters)
            self.assertEqual(passes_family_gate(supporters), len(expected_families) >= 2,
                             supporters)


if __name__ == "__main__":
    unittest.main()
