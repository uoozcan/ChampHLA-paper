"""Every number printed in the manuscript must still be in the artifact.

The claim audit validates [RESULT:] identifiers but never compares a number to
its source, so a table could drift from the artifact it was generated from and
nothing would notice. These tests read both and compare.

They skip when the artifacts are absent, so a fresh clone can run the suite
before the analysis has been regenerated.
"""
from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARTIFACT = ROOT / "artifacts" / "head_to_head" / "consensus_head_to_head.tsv"
MANUSCRIPT = ROOT / "manuscripts" / "benchmark" / "manuscript.md"
SUPPLEMENTARY = ROOT / "manuscripts" / "benchmark" / "supplementary.md"

BANNED_WGS = re.compile(r"0\.399|0\.494|\+30\.66|79/411|205/411")
RESULT_TAG = re.compile(r"\[RESULT:[^\]]+\]")

# The prose uses each tool's own spelling; the artifact key is an identifier and
# is deliberately not renamed, so the two are mapped rather than unified.
DISPLAY_TO_KEY = {"arcasHLA": "ArcasHLA", "seq2HLA": "Seq2HLA"}


def artifact_key(printed: str) -> str:
    name = printed.replace("Caller: ", "Caller:")
    if name.startswith("Caller:"):
        return "Caller:" + DISPLAY_TO_KEY.get(name[7:], name[7:])
    return DISPLAY_TO_KEY.get(name, name)

# Main-text Holm values, as printed. Each must round-trip to the artifact.
QUOTED_P = [
    ("wes", "Caller:HLA-HD", 4.3e-12),
    ("wes", "Caller:SpecHLA", 8.7e-13),
    ("wes", "Caller:T1K", 1.9e-7),
    ("wes", "Caller:POLYSOLVER", 0.17),
    ("wes", "SimpleTwoThirdsConsensus", 3.7e-8),
    ("rnaseq", "Caller:T1K", 1.4e-5),
    ("rnaseq", "Caller:ArcasHLA", 0.091),  # printed as arcasHLA
    ("rnaseq", "Caller:OptiType", 0.22),
    ("rnaseq", "Caller:HLA-HD", 0.75),
    ("rnaseq", "BestSingleTool_nestedCV", 0.02),
    ("rnaseq", "SimpleTwoThirdsConsensus", 0.035),
]


def artifact_rows() -> dict[tuple[str, str], dict[str, str]]:
    with ARTIFACT.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    return {(r["modality"], r["comparator"]): r for r in rows}


def table_rows(text: str, section: str) -> list[list[str]]:
    block = text.split(f"### {section}.")[1].split("###")[0]
    out = []
    for line in block.splitlines():
        if not line.startswith("| ") or line.startswith("|---") or " Correct " in line:
            continue
        out.append([cell.strip() for cell in line.strip("|").split("|")])
    return out


@unittest.skipUnless(ARTIFACT.is_file(), "head-to-head artifact not generated")
class ManuscriptReconciliationTests(unittest.TestCase):
    def setUp(self):
        self.by = artifact_rows()
        self.manuscript = MANUSCRIPT.read_text(encoding="utf-8")
        self.supplementary = SUPPLEMENTARY.read_text(encoding="utf-8")

    def test_supplementary_s1_matches_the_artifact(self):
        for modality, section in (("wes", "S1a"), ("rnaseq", "S1b")):
            for cells in table_rows(self.supplementary, section):
                name = artifact_key(cells[0])
                row = self.by.get((modality, name))
                self.assertIsNotNone(row, f"{section}: {name} absent from the artifact")
                self.assertEqual(cells[1], row["comparator_correct"], f"{section} {name} correct")
                self.assertEqual(cells[3], row["wins"], f"{section} {name} wins")
                self.assertEqual(cells[4], row["losses"], f"{section} {name} losses")
                expected = "yes" if row["holm_significant"] == "1" else "no"
                self.assertEqual(cells[7], expected, f"{section} {name} significance")

    def test_quoted_p_values_round_trip(self):
        for modality, comparator, quoted in QUOTED_P:
            actual = float(self.by[(modality, comparator)]["holm_adjusted_p"])
            self.assertAlmostEqual(
                actual / quoted, 1.0, delta=0.05,
                msg=f"{modality}/{comparator}: prose {quoted} vs artifact {actual:.3g}")

    def test_per_caller_totals_agree_between_s1_and_s5(self):
        for modality, section in (("wes", "S5a"), ("rnaseq", "S5b")):
            for cells in table_rows(self.supplementary, section):
                row = self.by.get((modality, artifact_key(f"Caller:{cells[0]}")))
                if row is None:
                    continue
                total = cells[5].replace("**", "").split("/")[0]
                self.assertEqual(total, row["comparator_correct"],
                                 f"{section} {cells[0]}: S5 total disagrees with S1")

    def test_main_text_table_one_matches_the_artifact(self):
        """Table 1 was missed by the first cross-check and kept a stale p value."""
        block = self.manuscript.split("**Table 1.")[1].split("No caller exceeds")[0]
        seen = 0
        for line in block.splitlines():
            if (not line.startswith("| ") or line.startswith("|---")
                    or "| Comparator |" in line):
                continue
            # Cells may carry [RESULT:ID] provenance tags; strip them before parsing.
            cells = [RESULT_TAG.sub("", c).strip() for c in line.strip("|").split("|")]
            method = artifact_key(cells[0])
            if method == "PanelHLA-Consensus":
                continue
            for modality, cell in (("wes", cells[1]), ("rnaseq", cells[2])):
                # An em dash marks a caller outside that assay's intended-use panel.
                if cell in {"—", "-", ""}:
                    self.assertIsNone(self.by.get((modality, method)),
                                      f"Table 1 {modality}/{method}: dashed but the "
                                      "artifact has a result for it")
                    continue
                row = self.by.get((modality, method))
                self.assertIsNotNone(row, f"Table 1: {method} absent from the artifact")
                correct = cell.split("(")[0].strip()
                self.assertEqual(correct, row["comparator_correct"],
                                 f"Table 1 {modality}/{method}: correct count")
                if "p = " in cell:
                    quoted = float(cell.split("p = ")[1].rstrip(") "))
                    actual = float(row["holm_adjusted_p"])
                    if quoted == 1.0:
                        self.assertAlmostEqual(actual, 1.0, places=6)
                    else:
                        self.assertAlmostEqual(
                            actual / quoted, 1.0, delta=0.05,
                            msg=f"Table 1 {modality}/{method}: p {quoted} vs {actual:.3g}")
                seen += 1
        self.assertGreaterEqual(seen, 8, "Table 1 rows were not parsed")

    def test_no_banned_wgs_performance_number_in_either_manuscript(self):
        for name, text in (("manuscript", self.manuscript),
                           ("supplementary", self.supplementary)):
            self.assertIsNone(BANNED_WGS.search(text),
                              f"{name} contains an invalid-WGS performance number")

    def test_artifact_scope_is_wes_and_rna_only(self):
        self.assertFalse(any(m == "wgs" for m, _ in self.by),
                         "WGS rows leaked into the head-to-head artifact")

    def test_reference_is_not_its_own_comparator(self):
        names = {c for _, c in self.by}
        self.assertNotIn("MajorityVote", names)
        self.assertNotIn("SimplePluralityLex", names)


if __name__ == "__main__":
    unittest.main()


class CitedPathsResolveTests(unittest.TestCase):
    """Every repo path a manuscript cites must ship with the submission.

    The supplement cited evidence in sibling trees that are not part of the
    bundle, so a referee could not resolve it -- and the whole WGS
    harmonisation-defect narrative rested on one of those files.
    """

    # Paths inside third-party caller distributions, named to identify a file
    # within a caller's own bundle rather than a file in this repository.
    EXTERNAL_TO_CALLERS = {
        "dat/IMGTHLA/version_report.txt",
        "db/VERSION.txt",
        "dictionary/allele.list",
    }

    # Paths this repository deliberately does not track. The truth-joined table
    # carries truth_allele columns and no such file is version-controlled here;
    # it is regenerated by join_truth_once. Citing it is correct, but it cannot
    # be required to exist in a clone.
    NOT_SHIPPED_BY_POLICY = {
        "artifacts/consensus_eval_wes_rna/joined_wes_rna.tsv",
    }

    PATH_RE = re.compile(r"`([a-zA-Z_][a-zA-Z0-9_./-]*/[a-zA-Z0-9_./-]+)`")

    def test_every_cited_repository_path_exists(self):
        missing = []
        for document in (MANUSCRIPT, SUPPLEMENTARY):
            text = document.read_text(encoding="utf-8")
            for cited in sorted(set(self.PATH_RE.findall(text))):
                if cited in self.EXTERNAL_TO_CALLERS or cited in self.NOT_SHIPPED_BY_POLICY:
                    continue
                if not (ROOT / cited).exists():
                    missing.append(f"{document.name}: {cited}")
        self.assertEqual(missing, [], f"cited paths absent from the bundle: {missing}")

    def test_no_manuscript_cites_a_sibling_tree(self):
        offenders = []
        for document in (MANUSCRIPT, SUPPLEMENTARY):
            text = document.read_text(encoding="utf-8")
            for cited in sorted(set(self.PATH_RE.findall(text))):
                if cited.startswith(("champhla_egcc_pilot/", "champhla_cc_confirmation/",
                                     "champhla_baseline_ladder/", "champhla_refformer/")):
                    offenders.append(f"{document.name}: {cited}")
        self.assertEqual(offenders, [],
                         "cite provenance/external_evidence/ instead of a sibling tree")


DEFECT_COUNTS = ROOT / "artifacts" / "harmonisation_defect" / "harmonisation_defect_counts.tsv"


@unittest.skipUnless(DEFECT_COUNTS.is_file(), "defect counts artifact not generated")
class HarmonisationDefectReconciliationTests(unittest.TestCase):
    """S4 and Figure 3 must agree with the counts artifact.

    S4 previously quoted figures measured on benchmark_wes_all_samples (7,235 rows,
    138 subjects) while the paper reports on benchmark_wes_truthbacked (2,655 rows,
    130 subjects), so the section described a cohort the results were not computed
    on. These tests pin both to the generated artifact.
    """

    def setUp(self):
        with DEFECT_COUNTS.open(newline="", encoding="utf-8") as handle:
            self.rows = list(csv.DictReader(handle, delimiter="\t"))
        self.supplementary = SUPPLEMENTARY.read_text(encoding="utf-8")
        self.manuscript = MANUSCRIPT.read_text(encoding="utf-8")

    def panel_rate(self, modality: str) -> tuple[int, int]:
        panel = [r for r in self.rows if r["modality"] == modality and r["in_panel"] == "1"]
        return (sum(int(r["false_homozygous"]) for r in panel),
                sum(int(r["rows"]) for r in panel))

    def test_artifact_carries_no_reference_typing(self):
        for row in self.rows:
            leaked = [k for k in row if k.lower().startswith("truth")]
            self.assertEqual(leaked, [], f"truth columns leaked into the artifact: {leaked}")

    def test_s4_tables_match_the_artifact(self):
        for modality, section in (("wes", "S4a"), ("rnaseq", "S4b")):
            # Key the printed rows by identifier, since the table prints each
            # tool's own spelling while the artifact carries the identifier.
            printed = {artifact_key(c[0]): c for c in table_rows(self.supplementary, section)}
            for row in (r for r in self.rows if r["modality"] == modality):
                cells = printed.get(row["caller"])
                self.assertIsNotNone(cells, f"{section}: {row['caller']} missing from the table")
                self.assertEqual(cells[2], row["rows"], f"{section} {row['caller']} rows")
                self.assertEqual(cells[3], row["placeholder_second_allele"],
                                 f"{section} {row['caller']} placeholders")
                self.assertEqual(cells[4], row["manufactured_homozygous"],
                                 f"{section} {row['caller']} manufactured")
                self.assertEqual(cells[6].replace("*", ""), row["false_homozygous"],
                                 f"{section} {row['caller']} false homozygous")

    def test_panel_rates_quoted_in_prose_match_the_artifact(self):
        for modality, quoted in (("wes", "4.1%"), ("rnaseq", "7.4%")):
            false_hom, total = self.panel_rate(modality)
            self.assertEqual(f"{100 * false_hom / total:.1f}%", quoted,
                             f"{modality}: artifact rate disagrees with the prose")
            self.assertIn(quoted, self.manuscript,
                          f"{modality}: rate {quoted} absent from the main text")

    def test_the_conversion_is_not_claimed_to_be_total(self):
        """SpecHLA emits 75 placeholders on RNA-seq and manufactured none.

        The main text once claimed the conversion was total for every caller in
        every assay, which this artifact disproves.
        """
        spechla = next(r for r in self.rows
                       if r["modality"] == "rnaseq" and r["caller"] == "SpecHLA")
        self.assertGreater(int(spechla["placeholder_second_allele"]), 0)
        self.assertEqual(int(spechla["manufactured_homozygous"]), 0)
        self.assertNotIn("conversion\nwas total", self.manuscript)
        self.assertNotIn("The conversion was total", self.manuscript)
