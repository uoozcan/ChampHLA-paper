from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from champhla_recovery.release import freeze_release, validate_release

ROOT = Path(__file__).resolve().parents[1]


class ValidateReleaseTests(unittest.TestCase):
    """A freeze manifest that nothing checks cannot support a provenance claim.

    The manuscript states that freeze manifests record a content hash for every
    released path. Until this validator existed, scripts/run_local_verification.sh
    never verified that, so the claim was unfalsifiable by the project's own gate.
    """

    def _tree(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / "a.txt").write_text("alpha\n", encoding="utf-8")
        (root / "sub").mkdir()
        (root / "sub" / "b.txt").write_text("beta\n", encoding="utf-8")
        return root

    def test_a_fresh_manifest_validates(self):
        with TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            manifest = root / "freeze.json"
            freeze_release(str(root), str(manifest))
            report = validate_release(str(root), str(manifest))
            self.assertTrue(report["valid"], report)
            self.assertEqual([], report["missing"])
            self.assertEqual([], report["mismatched"])
            self.assertEqual([], report["untracked"])

    def test_changed_content_is_a_mismatch(self):
        with TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            manifest = root / "freeze.json"
            freeze_release(str(root), str(manifest))
            (root / "a.txt").write_text("alpha changed\n", encoding="utf-8")
            report = validate_release(str(root), str(manifest))
            self.assertFalse(report["valid"])
            self.assertEqual(["a.txt"], report["mismatched"])

    def test_a_deleted_file_is_missing(self):
        with TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            manifest = root / "freeze.json"
            freeze_release(str(root), str(manifest))
            (root / "sub" / "b.txt").unlink()
            report = validate_release(str(root), str(manifest))
            self.assertFalse(report["valid"])
            self.assertEqual(["sub/b.txt"], report["missing"])

    def test_a_new_releasable_file_is_reported_as_unfrozen(self):
        """The check the mismatch count misses: a file that would ship but that the
        manifest does not attest at all."""
        with TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            manifest = root / "freeze.json"
            freeze_release(str(root), str(manifest))
            (root / "c.txt").write_text("gamma\n", encoding="utf-8")
            report = validate_release(str(root), str(manifest))
            self.assertFalse(report["valid"])
            self.assertEqual(["c.txt"], report["untracked"])

    def test_the_manifest_itself_is_not_reported_against_itself(self):
        with TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            manifest = root / "freeze.json"
            freeze_release(str(root), str(manifest))
            report = validate_release(str(root), str(manifest))
            self.assertNotIn("freeze.json", report["untracked"])
            self.assertNotIn("freeze.json", [e for e in report["mismatched"]])

    def test_manifest_is_stable_and_clean_when_it_is_the_only_changed_path(self):
        with TemporaryDirectory() as tmp:
            root = self._tree(tmp)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "content"], cwd=root, check=True)
            manifest = root / "freeze.json"
            first = freeze_release(str(root), str(manifest))
            first_bytes = manifest.read_bytes()
            second = freeze_release(str(root), str(manifest))
            self.assertEqual(first_bytes, manifest.read_bytes())
            self.assertFalse(first["git_dirty"])
            self.assertFalse(second["git_dirty"])
            self.assertEqual(first["content_tree_sha256"], second["content_tree_sha256"])

    def test_the_committed_manifest_is_checked_and_its_state_is_reported(self):
        """Not an assertion that it passes -- it does not, and that is the finding.
        This asserts the validator actually walks the real manifest."""
        report = validate_release(str(ROOT), str(ROOT / "artifacts" / "release_freeze.json"))
        recorded = json.loads((ROOT / "artifacts" / "release_freeze.json").read_text(encoding="utf-8"))
        self.assertEqual(recorded["file_count"], report["recorded_file_count"])
        self.assertGreater(report["recorded_file_count"], 100)


if __name__ == "__main__":
    unittest.main()
