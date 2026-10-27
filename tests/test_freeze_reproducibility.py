"""Freeze manifests are checksummed provenance, so they must mean the same thing
on every machine. These tests pin the two properties that were broken:

- record paths are POSIX, so a manifest built on Windows validates on Linux;
- content identity excludes build time and absolute root, so re-freezing an
  unchanged tree does not invent a new hash.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from champhla_confirmation.freeze import freeze_bundle, validate_freeze


def _project(root: Path) -> tuple[Path, Path]:
    (root / "src" / "champhla_confirmation").mkdir(parents=True)
    (root / "src" / "champhla_confirmation" / "code.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "configs").mkdir()
    (root / "configs" / "protocol.json").write_text("{}\n", encoding="utf-8")
    (root / "pyproject.toml").write_text("[project]\nname = \"fixture\"\nversion = \"0\"\n", encoding="utf-8")
    predictions = root / "pred.tsv"
    predictions.write_text("a\n1\n", encoding="utf-8")
    protocol = root / "protocol.json"
    protocol.write_text("{}\n", encoding="utf-8")
    return predictions, protocol


class FreezeReproducibilityTests(unittest.TestCase):
    def test_record_paths_are_posix_on_every_platform(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, protocol = _project(root)
            payload = freeze_bundle(root, {"predictions": predictions, "protocol": protocol},
                                    root / "freeze.json")
            paths = {row["path"] for row in payload["project_files"]}
            self.assertIn("src/champhla_confirmation/code.py", paths)
            self.assertIn("configs/protocol.json", paths)
            for path in paths:
                self.assertNotIn("\\", path, f"backslash in frozen path: {path}")

    def test_posix_manifest_validates_and_detects_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, protocol = _project(root)
            manifest = root / "freeze.json"
            freeze_bundle(root, {"predictions": predictions, "protocol": protocol}, manifest)
            self.assertTrue(validate_freeze(manifest)["valid"])
            (root / "src" / "champhla_confirmation" / "code.py").write_text("VALUE = 2\n",
                                                                           encoding="utf-8")
            result = validate_freeze(manifest)
            self.assertFalse(result["valid"])
            self.assertIn("project:src/champhla_confirmation/code.py:checksum_mismatch",
                          result["failures"])

    def test_manifest_relocates_from_a_foreign_windows_project_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, protocol = _project(root)
            runtime = root / "runtime"
            runtime.mkdir()
            manifest = runtime / "freeze.json"
            freeze_bundle(root, {"predictions": predictions, "protocol": protocol}, manifest)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["project_root"] = r"Z:\\retired\\checkout"
            manifest.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            result = validate_freeze(manifest)
            self.assertTrue(result["valid"], result)
            self.assertEqual(str(root), result["resolved_project_root"])

    def test_input_only_validation_keeps_hash_gate_but_allows_later_analysis_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, protocol = _project(root)
            manifest = root / "freeze.json"
            freeze_bundle(root, {"predictions": predictions, "protocol": protocol}, manifest)
            code = root / "src" / "champhla_confirmation" / "code.py"
            code.write_text("VALUE = 2\n", encoding="utf-8")
            self.assertFalse(validate_freeze(manifest)["valid"])
            inputs_only = validate_freeze(manifest, verify_project_files=False)
            self.assertTrue(inputs_only["valid"], inputs_only)
            self.assertFalse(inputs_only["project_files_verified"])
            predictions.write_text("a\n2\n", encoding="utf-8")
            self.assertFalse(
                validate_freeze(manifest, verify_project_files=False)["valid"],
                "input-only mode must still reject prediction drift",
            )

    def test_content_hash_is_stable_across_rebuilds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, protocol = _project(root)
            first = freeze_bundle(root, {"predictions": predictions, "protocol": protocol},
                                  root / "a.json")
            second = freeze_bundle(root, {"predictions": predictions, "protocol": protocol},
                                   root / "b.json")
            self.assertEqual(first["content_sha256"], second["content_sha256"])

    def test_content_hash_changes_when_a_covered_file_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, protocol = _project(root)
            before = freeze_bundle(root, {"predictions": predictions, "protocol": protocol},
                                   root / "a.json")
            (root / "src" / "champhla_confirmation" / "code.py").write_text("VALUE = 2\n",
                                                                           encoding="utf-8")
            after = freeze_bundle(root, {"predictions": predictions, "protocol": protocol},
                                  root / "b.json")
            self.assertNotEqual(before["content_sha256"], after["content_sha256"])

    def test_tampering_with_a_manifest_record_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            predictions, protocol = _project(root)
            manifest = root / "freeze.json"
            freeze_bundle(root, {"predictions": predictions, "protocol": protocol}, manifest)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["project_files"][0]["bytes"] += 1
            manifest.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                                encoding="utf-8")
            self.assertIn("manifest:content_sha256_mismatch", validate_freeze(manifest)["failures"])


if __name__ == "__main__":
    unittest.main()
