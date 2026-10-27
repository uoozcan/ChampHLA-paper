"""A caller that emits a header and no calls must fail validation.

The fixtures are real output from the 2026-09-16 pilot run, copied unmodified.
SpecHLA wrote a header-only file for both subjects and was recorded as valid
because the check hashed the file rather than reading it. That turned a
five-caller WES panel into four while still writing CALLERS_COMPLETE.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from champhla_confirmation.caller_validation import (count_calls, validate_caller,
                                                     validate_panel)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "caller_outputs"
WES_OUTPUTS = {
    "HLA-HD": FIXTURES / "HG00096_hlahd.txt",
    "OptiType": FIXTURES / "HG00096_optitype.txt",
    "POLYSOLVER": FIXTURES / "HG00096_polysolver.txt",
    "SpecHLA": FIXTURES / "HG00096_spechla.txt",
    "T1K": FIXTURES / "HG00096_t1k.txt",
}


class CallerValidationTests(unittest.TestCase):
    def test_callers_that_produced_calls_pass(self):
        for caller in ("HLA-HD", "OptiType", "T1K", "POLYSOLVER"):
            record = validate_caller(WES_OUTPUTS[caller])
            self.assertEqual(record["status"], "ok", f"{caller}: {record['detail']}")
            self.assertGreaterEqual(record["call_rows"], 3, caller)

    def test_header_only_output_is_rejected(self):
        """The defect this module exists to catch."""
        path = WES_OUTPUTS["SpecHLA"]
        self.assertGreater(path.stat().st_size, 0,
                           "the file is non-empty, which is why a size check missed it")
        record = validate_caller(path)
        self.assertEqual(record["status"], "empty")
        self.assertEqual(record["call_rows"], 0)

    def test_panel_is_incomplete_when_a_member_emits_nothing(self):
        result = validate_panel(WES_OUTPUTS, "wes")
        self.assertFalse(result["panel_complete"])
        self.assertEqual(result["callers_with_calls"], 4)
        self.assertEqual(result["panel_size"], 5)
        self.assertEqual(result["failures"], ["SpecHLA:empty"])

    def test_a_missing_panel_member_is_a_failure_not_an_omission(self):
        partial = {k: v for k, v in WES_OUTPUTS.items() if k != "SpecHLA"}
        result = validate_panel(partial, "wes")
        self.assertFalse(result["panel_complete"])
        self.assertEqual(result["failures"], ["SpecHLA:missing"])

    def test_a_complete_panel_passes(self):
        good = {k: v for k, v in WES_OUTPUTS.items() if k in {"HLA-HD", "OptiType", "T1K"}}
        result = validate_panel(good, "rnaseq")  # RNA panel has no SpecHLA/POLYSOLVER
        self.assertEqual(sorted(result["failures"]), ["ArcasHLA:missing"])
        good["ArcasHLA"] = FIXTURES / "HG00096_optitype.txt"  # any file carrying calls
        self.assertTrue(validate_panel(good, "rnaseq")["panel_complete"])

    def test_non_panel_callers_cannot_fail_the_panel(self):
        outputs = dict(WES_OUTPUTS)
        outputs.pop("SpecHLA")
        outputs["Kourami"] = FIXTURES / "HG00096_spechla.txt"  # empty, but not in the WES panel
        result = validate_panel(outputs, "wes")
        self.assertNotIn("Kourami:empty", result["failures"])

    def test_a_caller_missing_one_gene_is_incomplete(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "partial.txt"
            path.write_text("Gene\tAllele1\tAllele2\nHLA-A\tA*01:01\tA*02:01\n",
                            encoding="utf-8")
            record = validate_caller(path)
            self.assertEqual(record["status"], "incomplete")
            self.assertIn("B", record["detail"])

    def test_comment_lines_never_count_as_calls(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "comments.txt"
            path.write_text("# A*01:01 example in a comment\n# nothing real here\n",
                            encoding="utf-8")
            self.assertEqual(count_calls(path)[0], 0)


if __name__ == "__main__":
    unittest.main()
