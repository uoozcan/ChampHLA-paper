"""The declared protocol must match the executed one.

The frozen protocol declared TwoThirdsGuardedCC as the primary method and Holm
across three modalities long after the code had stopped doing either. The
divergence was real but only discoverable by reading evaluation.py. These tests
pin the amended protocol to the code, so the two cannot drift apart silently
again.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from champhla_confirmation.panels import (METHOD_PLURALITY, PANELS, REFERENCE_ALIASES)

ROOT = Path(__file__).resolve().parent.parent
FROZEN = ROOT / "configs" / "confirmation_protocol.json"
AMENDED = ROOT / "configs" / "confirmation_protocol_amended.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class ProtocolConsistencyTests(unittest.TestCase):
    def test_amended_protocol_declares_the_executed_primary_method(self):
        self.assertEqual(load(AMENDED)["primary_method"], METHOD_PLURALITY)

    def test_amended_protocol_declares_the_executed_reference_aliases(self):
        declared = set(load(AMENDED)["reference_aliases_excluded_from_comparator_family"])
        self.assertEqual(declared, set(REFERENCE_ALIASES))

    def test_amended_protocol_panels_match_the_code(self):
        declared = load(AMENDED)["panels"]
        self.assertEqual({k: tuple(v) for k, v in declared.items()}, dict(PANELS))

    def test_frozen_protocol_is_retained_unedited_and_marked_superseded(self):
        frozen = load(FROZEN)
        # The pre-registration must keep saying what it originally promised.
        self.assertEqual(frozen["status"], "frozen_before_external_truth")
        self.assertEqual(frozen["primary_method"], "TwoThirdsGuardedCC")
        # And the amendment must point at it rather than overwrite it.
        self.assertEqual(load(AMENDED)["supersedes"], "configs/confirmation_protocol.json")
        self.assertTrue(load(AMENDED)["superseded_record_retained"])

    def test_every_divergence_names_its_authorising_record(self):
        amended = load(AMENDED)
        for record in amended["amendment_records"]:
            self.assertTrue((ROOT / record).is_file(), f"missing amendment record: {record}")

    def test_manuscript_scope_excludes_wgs(self):
        amended = load(AMENDED)
        self.assertNotIn("wgs", amended["manuscript_modalities"])
        self.assertEqual(set(amended["reporting_denominator"]), {"wes", "rnaseq"})


if __name__ == "__main__":
    unittest.main()
