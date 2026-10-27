from __future__ import annotations

import json
import unittest
from pathlib import Path

from champhla_confirmation.panels import (GENES, METHOD_BASELINE, METHOD_GUARDED_CC,
                                         METHOD_PLURALITY, METHOD_PLURALITY_ALIAS,
                                         METHOD_RAW_CC, MODALITIES, PANELS,
                                         REFERENCE_ALIASES)

ROOT = Path(__file__).resolve().parents[1]
FROZEN_PROTOCOL = ROOT / "configs" / "confirmation_protocol.json"


class ReferenceAliasTests(unittest.TestCase):
    """The primary method must never appear in its own comparator family.

    Recorded in decisions/20260917_protocol_amendment.json: leaving the legacy
    alias in place compared consensus against itself at delta 0 and p = 1.0, so
    every Holm family was one comparator too large and every adjusted p value in
    the paper was inflated. These assertions guard that regression directly
    rather than through an artifact that may not be present.
    """

    def test_both_names_of_the_primary_rule_are_excluded(self):
        self.assertIn(METHOD_PLURALITY, REFERENCE_ALIASES)
        self.assertIn(METHOD_PLURALITY_ALIAS, REFERENCE_ALIASES)

    def test_the_exclusion_removes_the_primary_method_and_its_alias(self):
        """The set expression used at evaluation.py:193 and
        scripts/consensus_head_to_head.py:37."""
        emitted = {METHOD_PLURALITY, METHOD_PLURALITY_ALIAS, METHOD_BASELINE,
                   METHOD_RAW_CC, METHOD_GUARDED_CC, "Caller:OptiType"}
        family = sorted(emitted - REFERENCE_ALIASES)
        self.assertNotIn(METHOD_PLURALITY, family)
        self.assertNotIn(METHOD_PLURALITY_ALIAS, family)
        self.assertEqual({METHOD_RAW_CC, "Caller:OptiType", METHOD_BASELINE,
                          METHOD_GUARDED_CC}, set(family))

    def test_the_exclusion_does_not_remove_a_genuine_comparator(self):
        self.assertEqual({METHOD_GUARDED_CC}, {METHOD_GUARDED_CC} - REFERENCE_ALIASES)

    def test_the_alias_is_not_the_primary_name(self):
        """If these ever collapse to one string the exclusion still works, but the
        alias has silently stopped being emitted and the comparison it guards has
        changed shape."""
        self.assertNotEqual(METHOD_PLURALITY, METHOD_PLURALITY_ALIAS)
        self.assertEqual(2, len(REFERENCE_ALIASES))


class PanelTests(unittest.TestCase):
    def test_genes_are_the_three_class_one_loci(self):
        self.assertEqual(("A", "B", "C"), GENES)

    def test_every_modality_has_a_panel(self):
        self.assertEqual(set(MODALITIES), set(PANELS))

    def test_panel_members_are_unique_and_sorted(self):
        for modality, panel in PANELS.items():
            self.assertEqual(len(set(panel)), len(panel), modality)
            self.assertEqual(tuple(sorted(panel)), panel, modality)

    def test_panel_sizes_match_the_reported_vote_widths(self):
        """The manuscript reports five callers voting on WES and four on RNA-seq."""
        self.assertEqual(5, len(PANELS["wes"]))
        self.assertEqual(4, len(PANELS["rnaseq"]))
        self.assertEqual(5, len(PANELS["wgs"]))

    def test_the_panels_still_match_the_frozen_pre_registration(self):
        """configs/confirmation_protocol.json declares the panels as frozen on
        2026-08-31. A panel is an input: if code and pre-registration drift apart,
        the reported vote is not the one that was declared."""
        frozen = json.loads(FROZEN_PROTOCOL.read_text(encoding="utf-8"))["panels"]
        self.assertEqual({modality: sorted(callers) for modality, callers in frozen.items()},
                         {modality: sorted(callers) for modality, callers in PANELS.items()})


if __name__ == "__main__":
    unittest.main()
