"""Write a deterministic manifest of the declared analysis environment."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import shutil
import subprocess
from pathlib import Path


PACKAGES = ("numpy", "scipy", "matplotlib", "pytest", "ruff", "python-docx")
COMMANDS = {
    "nextflow": ["nextflow", "-version"],
    "apptainer": ["apptainer", "--version"],
    "samtools": ["samtools", "--version"],
}


def command_version(command: list[str]) -> str:
    if not shutil.which(command[0]):
        return "unavailable"
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    text = (result.stdout + "\n" + result.stderr).strip()
    return " ".join(text.split())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    packages = {}
    for name in PACKAGES:
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "unavailable"
    payload = {
        "schema_version": "panelhla-exact-environment-1",
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "packages": packages,
        "commands": {name: command_version(command) for name, command in COMMANDS.items()},
    }
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
