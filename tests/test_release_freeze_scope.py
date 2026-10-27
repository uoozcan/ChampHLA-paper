"""The release freeze must describe what ships, not what happens to be on disk.

It previously walked the filesystem against a hand-maintained exclusion list and
swept in artifacts/consensus_eval_wes_rna/joined_wes_rna.tsv, a gitignored
truth-bearing table that is deliberately never distributed. Validating that manifest
from a clone would report the file missing and the release corrupt.
"""
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from champhla_recovery.release import freeze_release

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "artifacts" / "release_freeze.json"


def git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class ReleaseFreezeScopeTests(unittest.TestCase):
    def test_ignored_files_are_not_frozen(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            git("init", "-q", cwd=root)
            git("config", "user.email", "t@example.com", cwd=root)
            git("config", "user.name", "t", cwd=root)
            (root / ".gitignore").write_text("secret*.tsv\n", encoding="utf-8")
            (root / "kept.txt").write_text("ships\n", encoding="utf-8")
            (root / "secret_truth.tsv").write_text("truth_allele1\nA*01:01\n", encoding="utf-8")
            git("add", ".gitignore", "kept.txt", cwd=root)
            git("commit", "-qm", "init", cwd=root)

            payload = freeze_release(str(root), str(root / "freeze.json"))
            paths = {f["path"] for f in payload["files"]}
            self.assertIn("kept.txt", paths)
            self.assertNotIn("secret_truth.tsv", paths,
                             "an ignored file must never enter the release manifest")

    def test_falls_back_to_a_walk_outside_a_repository(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plain.txt").write_text("x\n", encoding="utf-8")
            payload = freeze_release(str(root), str(root / "freeze.json"))
            self.assertIn("plain.txt", {f["path"] for f in payload["files"]})

    def test_recorded_paths_are_posix(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pkg").mkdir()
            (root / "pkg" / "mod.py").write_text("X = 1\n", encoding="utf-8")
            payload = freeze_release(str(root), str(root / "freeze.json"))
            paths = {f["path"] for f in payload["files"]}
            self.assertIn("pkg/mod.py", paths)
            for path in paths:
                self.assertNotIn("\\", path)

    def test_superseded_and_historical_material_is_not_frozen(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            git("init", "-q", cwd=root)
            git("config", "user.email", "t@example.com", cwd=root)
            git("config", "user.name", "t", cwd=root)
            (root / "manuscripts" / "source_original").mkdir(parents=True)
            (root / "manuscripts" / "historical").mkdir(parents=True)
            (root / "manuscripts" / "benchmark").mkdir(parents=True)
            (root / "manuscripts" / "source_original" / "source.docx").write_bytes(b"old")
            (root / "manuscripts" / "historical" / "draft.md").write_text(
                "old\n", encoding="utf-8"
            )
            (root / "manuscripts" / "benchmark" / "manuscript.md").write_text(
                "active\n", encoding="utf-8"
            )
            git("add", ".", cwd=root)
            git("commit", "-qm", "init", cwd=root)

            payload = freeze_release(str(root), str(root / "freeze.json"))
            paths = {f["path"] for f in payload["files"]}
            self.assertIn("manuscripts/benchmark/manuscript.md", paths)
            self.assertFalse(any("source_original" in path for path in paths))
            self.assertFalse(any("historical" in path for path in paths))

    @unittest.skipUnless(MANIFEST.is_file(), "release freeze not generated")
    def test_the_committed_manifest_carries_no_truth_joined_table(self):
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        offenders = [f["path"] for f in payload["files"] if "joined" in f["path"]]
        self.assertEqual(offenders, [],
                         "the release manifest must not reference a truth-joined table")


if __name__ == "__main__":
    unittest.main()
