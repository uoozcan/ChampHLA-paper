"""Two runs of the head-to-head script must produce byte-identical output.

This project has been bitten by non-determinism before: set() iteration over
k-mers once made two runs of identical code differ on 8,517 rows and change one
call. The statistical artifacts feed every number in the manuscript, so their
reproducibility is checked rather than assumed.

A small bootstrap keeps the test fast; determinism does not depend on the
iteration count, only on the seeding and iteration order.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "consensus_head_to_head.py"
JOINED = ROOT / "artifacts" / "consensus_eval_wes_rna" / "joined_wes_rna.tsv"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@unittest.skipUnless(JOINED.is_file(), "joined table not present")
class HeadToHeadDeterminismTests(unittest.TestCase):
    def test_two_runs_are_byte_identical(self):
        with TemporaryDirectory() as directory:
            outputs = []
            for name in ("a", "b"):
                out = Path(directory) / name
                subprocess.run(
                    [sys.executable, str(SCRIPT), str(JOINED), str(out), "300"],
                    check=True, capture_output=True,
                )
                outputs.append(out / "consensus_head_to_head.tsv")
            self.assertEqual(digest(outputs[0]), digest(outputs[1]),
                             "head-to-head output is not reproducible")

    def test_the_reference_never_appears_as_its_own_comparator(self):
        with TemporaryDirectory() as directory:
            out = Path(directory) / "run"
            subprocess.run(
                [sys.executable, str(SCRIPT), str(JOINED), str(out), "100"],
                check=True, capture_output=True,
            )
            text = (out / "consensus_head_to_head.tsv").read_text(encoding="utf-8")
            comparators = {line.split("\t")[1] for line in text.splitlines()[1:]}
            self.assertNotIn("MajorityVote", comparators)
            self.assertNotIn("SimplePluralityLex", comparators)


if __name__ == "__main__":
    unittest.main()
