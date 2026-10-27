"""The manuscript and the LICENSE must say the same thing.

The abstract described the software as "released as a research-only ... framework"
while the repository shipped MIT, which grants unrestricted commercial use. A
referee checking the availability statement against the licence would have found
them contradicting. The restriction is real but lives in the callers ChampHLA
invokes, not in ChampHLA.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = ROOT / "manuscripts" / "benchmark" / "manuscript.md"
NOTICES = ROOT / "THIRD_PARTY_NOTICES.md"

# A licence whose name appears in the repository LICENSE file, if there is one.
LICENSE_FILES = ("LICENSE", "LICENSE.md", "LICENSE.txt")


def repository_licence() -> str | None:
    for name in LICENSE_FILES:
        path = ROOT / name
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")
    return None


class LicenceConsistencyTests(unittest.TestCase):
    def setUp(self):
        self.manuscript = MANUSCRIPT.read_text(encoding="utf-8")
        # Line wrapping must not change meaning, so match on normalised whitespace.
        self.flat = re.sub(r"\s+", " ", self.manuscript).lower()

    def test_manuscript_does_not_call_the_software_research_only(self):
        """It ships a permissive licence; 'research-only' would misdescribe it."""
        offenders = [line.strip() for line in self.manuscript.splitlines()
                     if re.search(r"research-only\s+(auditable|framework|software)", line, re.I)]
        self.assertEqual(offenders, [],
                         "the manuscript describes the software as research-only while "
                         "shipping a permissive licence")

    def test_manuscript_names_the_licence_it_ships(self):
        self.assertIn("MIT", self.manuscript,
                      "the availability statement must name the licence")

    def test_manuscript_discloses_that_callers_carry_their_own_terms(self):
        lowered = self.flat
        self.assertTrue(
            "own terms" in lowered or "own licence" in lowered or "own license" in lowered,
            "the availability statement must say the callers carry their own terms")
        self.assertIn("commercial", lowered,
                      "the commercial-use restriction on some callers must be disclosed")

    def test_third_party_notices_exist_and_separate_verified_from_unverified(self):
        self.assertTrue(NOTICES.is_file(), "THIRD_PARTY_NOTICES.md is required")
        text = NOTICES.read_text(encoding="utf-8")
        self.assertIn("Verified from the deployed installation", text)
        self.assertNotIn("TO CONFIRM", text,
                         "every caller's terms are now verified; an unverified one must be "
                         "marked, not guessed")
        for caller in ("OptiType", "Kourami", "arcasHLA", "SpecHLA", "HLA-HD", "POLYSOLVER",
                       "T1K", "seq2HLA"):
            self.assertIn(caller, text, f"{caller} must appear in the notices")

    def test_callers_without_an_in_image_licence_cite_their_upstream_source(self):
        """Callers whose licence is not in their image are asserted only with the
        upstream source and date that confirmed them (2026-10-09)."""
        text = NOTICES.read_text(encoding="utf-8")
        section = text.split("## Callers whose licence is not shipped in the image")[1]
        section = section.split("\n## ")[0]
        self.assertIn("confirmed upstream", text)
        for caller, source in (("HLA-HD", "https://w3.genome.med.kyoto-u.ac.jp/HLA-HD/"),
                               ("T1K", "https://github.com/mourisl/T1K"),
                               ("seq2HLA", "https://github.com/TRON-Bioinformatics/seq2HLA")):
            row = next(line for line in section.splitlines() if line.startswith(f"| {caller}"))
            self.assertIn(source, row, f"{caller} must cite its upstream source")
        self.assertIn("2026-10-09", section)

    def test_polysolver_states_both_the_code_and_the_image_terms(self):
        """Verified 2026-09-18 from polysolver.sif:/home/polysolver/license/.

        Its source is BSD-style, so calling POLYSOLVER non-commercial software is
        wrong. Its distributed image is academic and non-profit only because it
        bundles Novoalign, and the image is what this pipeline runs. Quoting either
        half alone misdescribes it, so both must be present.
        """
        text = NOTICES.read_text(encoding="utf-8")
        self.assertIn("BSD-style", text,
                      "POLYSOLVER's own code is BSD-style and that must be stated")
        flat = re.sub(r"\s+", " ", text).lower()
        self.assertIn("academic/non-profit users only", flat,
                      "the image restriction is the term that applies here")
        self.assertIn("novoalign", flat,
                      "the reason for the image restriction must be named")

    def test_the_most_restrictive_term_is_identified(self):
        """A pipeline is bound by its most restrictive component, so say which."""
        flat = re.sub(r"\s+", " ", NOTICES.read_text(encoding="utf-8")).lower()
        self.assertIn("most restrictive", flat)

    @unittest.skipUnless(repository_licence(), "no LICENSE file in this repository")
    def test_the_repository_licence_matches_what_the_manuscript_claims(self):
        licence = repository_licence()
        if "MIT" in self.manuscript:
            self.assertIn("MIT", licence,
                          "the manuscript claims MIT but the LICENSE says otherwise")


if __name__ == "__main__":
    unittest.main()
