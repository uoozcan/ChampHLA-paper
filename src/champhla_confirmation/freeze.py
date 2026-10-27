from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .io import read_json, sha256, sha256_text, write_json


CODE_DIRS = {"src", "scripts", "configs", "models", "templates"}
CODE_FILES = {"pyproject.toml", "README.md", "IMPLEMENTATION_STATUS.md", "ORIGINALS_MANIFEST.json"}

# Fields that record when and where a manifest was built rather than what it
# covers. Excluding them from content_sha256 makes the content identity of a
# freeze reproducible: the same tree frozen twice, or frozen on a different
# platform, yields the same value.
NON_CONTENT_FIELDS = {"created_at_utc", "content_sha256", "project_root"}


def _content_hash(payload: dict) -> str:
    material = {key: value for key, value in payload.items() if key not in NON_CONTENT_FIELDS}
    return sha256_text(json.dumps(material, indent=2, sort_keys=True))


def _tree_hashes(root: Path) -> list[dict]:
    paths = [root / name for name in CODE_FILES if (root / name).is_file()]
    for directory in CODE_DIRS:
        base = root / directory
        if base.is_dir():
            paths.extend(path for path in base.rglob("*") if path.is_file()
                         and "__pycache__" not in path.parts)
    records = []
    for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        records.append({"path": relative.as_posix(), "bytes": path.stat().st_size,
                        "sha256": sha256(path)})
    return records


def freeze_bundle(project_root: str | Path, named_inputs: dict[str, str | Path],
                  output_manifest: str | Path) -> dict:
    root = Path(project_root).resolve()
    if not root.is_dir():
        raise ValueError(f"project root does not exist: {root}")
    inputs = {}
    for name, raw_path in sorted(named_inputs.items()):
        path = Path(raw_path).resolve()
        if not path.is_file():
            raise ValueError(f"freeze input {name} is not a file: {path}")
        # Inside the project, record the path relative to the root so the manifest
        # validates on any checkout; outside it, the absolute path is all there is.
        try:
            recorded = path.relative_to(root).as_posix()
        except ValueError:
            recorded = path.as_posix()
        inputs[name] = {"path": recorded, "bytes": path.stat().st_size, "sha256": sha256(path)}
    payload = {
        "schema_version": "confirmation-freeze-1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "truth_joined": False,
        "policy": "immutable predictions and policy before external truth",
        "project_hash_scope": {"directories": sorted(CODE_DIRS), "files": sorted(CODE_FILES)},
        "project_root": str(root),
        "project_files": _tree_hashes(root),
        "inputs": inputs,
    }
    payload["content_sha256"] = _content_hash(payload)
    write_json(output_manifest, payload)
    return payload


def validate_freeze(manifest_path: str | Path, *,
                    verify_project_files: bool = True) -> dict:
    manifest = read_json(manifest_path)
    failures = []
    recorded_content = manifest.get("content_sha256")
    if recorded_content is not None and recorded_content != _content_hash(manifest):
        failures.append("manifest:content_sha256_mismatch")
    manifest_file = Path(manifest_path).resolve()
    root = Path(manifest.get("project_root", ""))
    if not root.is_dir():
        # Historical manifests may carry an absolute root from another operating
        # system (for example a Windows drive path opened from WSL/Linux). Relative
        # frozen inputs remain portable: find the nearest project ancestor of the
        # manifest, then verify their recorded hashes there.
        relocated = next(
            (
                ancestor for ancestor in manifest_file.parents
                if (ancestor / "pyproject.toml").is_file()
                and (ancestor / "src").is_dir()
            ),
            None,
        )
        if relocated is not None:
            root = relocated
    for name, record in manifest.get("inputs", {}).items():
        path = Path(record["path"])
        if not path.is_absolute():
            path = root.joinpath(*record["path"].split("/"))
        if not path.is_file():
            failures.append(f"{name}:missing")
        elif sha256(path) != record["sha256"]:
            failures.append(f"{name}:checksum_mismatch")
    checked_project_files = 0
    if verify_project_files:
        for record in manifest.get("project_files", []):
            checked_project_files += 1
            path = root.joinpath(*record["path"].split("/"))
            if not path.is_file():
                failures.append(f"project:{record['path']}:missing")
            elif sha256(path) != record["sha256"]:
                failures.append(f"project:{record['path']}:checksum_mismatch")
    return {
        "valid": not failures,
        "failures": failures,
        "checked_inputs": len(manifest.get("inputs", {})),
        "checked_project_files": checked_project_files,
        "project_files_verified": verify_project_files,
        "resolved_project_root": str(root),
    }
