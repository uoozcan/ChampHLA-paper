"""Guard the Scientific Reports rewrite against claim and evidence drift.

Usage: python reports/tools/check_scirep_rewrite.py <worktree-root>
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / "src"))

from champhla_recovery.manuscript import audit_claims  # noqa: E402


MAIN = Path("manuscripts/benchmark/manuscript.md")
SUPPLEMENT = Path("manuscripts/benchmark/supplementary.md")
TAG = re.compile(r"\[RESULT:([A-Za-z0-9_.:-]+)\]")
GENERATED = re.compile(
    r"<!-- BEGIN GENERATED.*?<!-- END GENERATED[^>]*-->", re.DOTALL
)
GENERATED_NAMED = re.compile(
    r"<!-- BEGIN GENERATED (?P<name>.*?) -->(?P<body>.*?)"
    r"<!-- END GENERATED (?P=name) -->",
    re.DOTALL,
)
ALLOWED_NEW_GENERATED = {
    "RERUN TASK STATE TABLE",
    "RERUN CELL COMPARISON TABLE",
}
BANNED = (
    "notably",
    "importantly",
    "moreover",
    "furthermore",
    "delve",
    "pivotal",
    "it is worth noting",
    "in summary",
    "in conclusion",
    "paves the way",
    "seamless",
)


def _head(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(ROOT), "show", f"HEAD:{path.as_posix()}"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    ).stdout


def _without_references_or_generated(text: str) -> str:
    text = GENERATED.sub("", text)
    if "## References" not in text:
        return text
    before, rest = text.split("## References", 1)
    _, separator, after = rest.partition("\n## Acknowledgements")
    return before + (separator + after if separator else "")


def _generated_blocks(text: str) -> list[str]:
    return GENERATED.findall(text)


def _generated_by_name(text: str) -> dict[str, str]:
    found = list(GENERATED_NAMED.finditer(text))
    result = {match.group("name"): match.group(0) for match in found}
    if len(result) != len(found):
        raise ValueError("duplicate generated block name")
    return result


canonical_main = _head(MAIN)
canonical_supplement = _head(SUPPLEMENT)
new_main = (ROOT / MAIN).read_text(encoding="utf-8")
new_supplement = (ROOT / SUPPLEMENT).read_text(encoding="utf-8")

failures: list[str] = []
old_tags = set(TAG.findall(canonical_main + canonical_supplement))
new_tags = set(TAG.findall(new_main + new_supplement))
if old_tags != new_tags:
    failures.append(
        "result-tag set changed: "
        + json.dumps(
            {"missing": sorted(old_tags - new_tags), "extra": sorted(new_tags - old_tags)}
        )
    )

if _generated_blocks(canonical_main) != _generated_blocks(new_main):
    failures.append("main-manuscript generated blocks changed")
old_supplement_blocks = _generated_by_name(canonical_supplement)
new_supplement_blocks = _generated_by_name(new_supplement)
for name, block in old_supplement_blocks.items():
    if new_supplement_blocks.get(name) != block:
        failures.append(f"supplement generated block changed: {name}")
unexpected = set(new_supplement_blocks) - set(old_supplement_blocks) - ALLOWED_NEW_GENERATED
if unexpected:
    failures.append(f"unexpected new supplement generated blocks: {sorted(unexpected)}")

with tempfile.TemporaryDirectory(prefix="champhla_scirep_audit_") as tmp:
    for label, relative in (("main", MAIN), ("supplement", SUPPLEMENT)):
        result = audit_claims(
            str(ROOT / relative),
            str(ROOT / "result_registry.tsv"),
            str(ROOT / "manuscripts/claim_audit.tsv"),
            str(Path(tmp) / f"{label}.json"),
            str(ROOT),
            author_gate=str(ROOT / "configs/fimm_submission_gate.json"),
        )
        scientific_failures = [
            failure
            for failure in result["blocking_failures"]
            if "AUTHOR INPUT REQUIRED" not in failure
            and "TO CONFIRM" not in failure
            and "FIMM:" not in failure
        ]
        if scientific_failures:
            failures.append(f"{label} claim audit: {scientific_failures}")
        if result["warnings"]:
            failures.append(f"{label} claim warnings: {result['warnings']}")

lowered = _without_references_or_generated(new_main).lower()
for phrase in BANNED:
    if phrase in lowered:
        failures.append(f"banned phrase remains: {phrase}")

if "## Background" in new_main or "## Declarations" in new_main:
    failures.append("BMC-only heading remains")

print(f"result tags: {len(new_tags)} preserved")
print(f"generated blocks: {len(_generated_blocks(new_main))} main, "
      f"{len(_generated_blocks(new_supplement))} supplement")
if failures:
    for failure in failures:
        print(f"FAIL: {failure}")
    raise SystemExit(1)
print("Scientific Reports rewrite guard: PASS")
