from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .io import read_json, sha256, sha256_text, write_json


EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "runs",
    "runtime_data",
    "truth_sealed",
    # Retained in the working repository as provenance, but never shipped in
    # the active paper release or submission bundle.
    "source_original",
    "historical",
    "quarantined_figures",
    "consensus_eval",
    "consensus_eval_wes_rna",
    "family_gate",
    "harmonisation_correction",
    "harmonisation_defect",
    "head_to_head",
    "integration_limits",
    "plurality_characterisation",
    "source_results",
    "verification",
    "wgs_pilot_review",
}



def _tracked_paths(project: Path) -> list[Path] | None:
    """Paths git tracks, or None when this is not a repository.

    Freezing what git tracks is what makes the manifest describe the release. A
    filesystem walk also sees ignored files -- including the truth-joined tables,
    which are deliberately never distributed.
    """
    try:
        result = subprocess.run(
            ["git", "-C", str(project), "ls-files", "-z", "--cached", "--others",
             "--exclude-standard"],
            check=True, capture_output=True, text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return sorted((Path(entry) for entry in result.stdout.split("\0") if entry),
                  key=lambda item: item.as_posix())


def _walked_paths(project: Path) -> list[Path]:
    """Fallback for a tree that is not a git repository."""
    out = []
    for path in project.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(project)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        out.append(relative)
    return sorted(out, key=lambda item: item.as_posix())


def _release_paths(project: Path) -> list[Path]:
    tracked = _tracked_paths(project)
    paths = tracked if tracked is not None else _walked_paths(project)
    # git ls-files respects .gitignore but not the scientific quarantine.
    # Apply the same content boundary to repository and non-repository trees.
    return [
        relative
        for relative in paths
        if not any(part in EXCLUDED_PARTS for part in relative.parts)
    ]


def freeze_release(root: str, output: str) -> dict:
    project = Path(root).resolve()
    target = Path(output).resolve()
    files = []
    for relative in _release_paths(project):
        path = project / relative
        if not path.is_file() or path.resolve() == target:
            continue
        files.append({"path": relative.as_posix(), "bytes": path.stat().st_size,
                      "sha256": sha256(path)})
    try:
        relative_target = target.relative_to(project).as_posix()
        status = subprocess.run(
            ["git", "-C", str(project), "status", "--porcelain", "--untracked-files=all"],
            check=True, capture_output=True, text=True,
        ).stdout.splitlines()
        # The manifest cannot include its own content or commit identity without
        # creating a self-reference. Its dirty-state assertion therefore covers
        # every repository path except the manifest itself; the stable content
        # digest below identifies the complete releasable tree.
        dirty_paths = []
        for line in status:
            candidate = line[3:].strip().strip('"')
            if " -> " in candidate:
                candidate = candidate.split(" -> ", 1)[1].strip().strip('"')
            if candidate != relative_target:
                dirty_paths.append(candidate)
        dirty = bool(dirty_paths)
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        dirty = True
    content_tree_sha256 = sha256_text(json.dumps(files, sort_keys=True, separators=(",", ":")))
    result = {
        "schema_version": "panelhla-release-freeze-2",
        "git_dirty": dirty,
        "git_commit_policy": (
            "Commit identity is recorded by the external verification record; embedding the "
            "commit that contains this manifest would be self-referential."
        ),
        "content_tree_sha256": content_tree_sha256,
        "files": files, "file_count": len(files),
        "truth_data_included": False,
    }
    write_json(target, result)
    return result


def validate_release(root: str, manifest: str) -> dict:
    """Check a release freeze manifest against the working tree.

    champhla_confirmation.freeze.validate_freeze cannot be used for this: it reads
    ``inputs`` and ``project_files``, which the release manifest does not have (it
    records ``files``), so it would walk zero entries and report the manifest valid.

    Reports three kinds of divergence, all of which falsify the provenance claim
    that the manifest attests a specific tree:
      ``missing``   - a recorded file is gone
      ``mismatch``  - a recorded file's content changed
      ``untracked`` - a file that would now be released is absent from the manifest
    """
    project = Path(root).resolve()
    recorded = read_json(manifest)
    entries = recorded.get("files", [])
    by_path = {entry["path"]: entry for entry in entries}

    missing, mismatched = [], []
    for entry in entries:
        path = project.joinpath(*entry["path"].split("/"))
        if not path.is_file():
            missing.append(entry["path"])
        elif sha256(path) != entry["sha256"]:
            mismatched.append(entry["path"])

    target = Path(manifest).resolve()
    current = {relative.as_posix() for relative in _release_paths(project)
               if (project / relative).is_file() and (project / relative).resolve() != target}
    untracked = sorted(current - set(by_path))

    computed_tree_hash = sha256_text(json.dumps(entries, sort_keys=True, separators=(",", ":")))
    metadata_mismatch = computed_tree_hash != recorded.get("content_tree_sha256")
    return {
        "valid": not (missing or mismatched or untracked or metadata_mismatch),
        "manifest": str(Path(manifest)),
        "recorded_file_count": len(entries),
        "recorded_git_commit": recorded.get("git_commit"),
        "recorded_git_dirty": recorded.get("git_dirty"),
        "recorded_content_tree_sha256": recorded.get("content_tree_sha256"),
        "computed_content_tree_sha256": computed_tree_hash,
        "metadata_mismatch": metadata_mismatch,
        "missing": sorted(missing),
        "mismatched": sorted(mismatched),
        "untracked": untracked,
    }
