from __future__ import annotations

import re
from pathlib import Path

from .io import read_json, sha256, write_json


_DIGEST_RE = re.compile(r"^(?:sha256:)?[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
AMENDMENT_SCHEMA = "champhla-preregistration-amendment-1"
PINNED_RELEASE_COMMIT = "66d949da90861da6cf60cf1d4bee2f094f2518bd"
# The extension analysis code frozen by the amendment's analysis_code_sha256. Reporting
# code (registry, tables, figures, manuscript) may change after the pin; this may not.
EXTENSION_ANALYSIS_PATHS = (
    "src/champhla_confirmation",
    "scripts/run_extension.py",
    "configs/caller_resources_v2.json",
    "cohorts/frozen_initial_rosters.tsv",
)


def extension_analysis_code_sha256(root: Path) -> str:
    """One digest over every frozen extension-analysis file, in path order."""
    import hashlib

    files = []
    for relative in EXTENSION_ANALYSIS_PATHS:
        path = root / relative
        if path.is_dir():
            files.extend(item for item in path.rglob("*")
                         if item.is_file() and "__pycache__" not in item.parts)
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(f"frozen extension path missing: {relative}")
    digest = hashlib.sha256()
    for path in sorted(files, key=lambda item: item.relative_to(root).as_posix()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0")
        digest.update(sha256(path).encode("ascii") + b"\n")
    return digest.hexdigest()


def _publication_blocker(root: Path, record: dict, amendment_sha256: str) -> str | None:
    """The deposit holds the signed amendment, so its publication cannot be recorded inside
    the amendment: a separate record names the DOI and the signed amendment's SHA-256."""
    zenodo = record.get("zenodo", {})
    doi = str(zenodo.get("reserved_doi", ""))
    if not doi.startswith("10."):
        return "pre-registration records no public release DOI"
    publication_path = root / str(zenodo.get("publication_record", ""))
    if not zenodo.get("publication_record") or not publication_path.is_file():
        return "Zenodo pre-registration deposit is not published"
    publication = read_json(publication_path)
    if publication.get("published") is not True or publication.get("doi") != doi:
        return "Zenodo pre-registration deposit is not published"
    if publication.get("amendment_sha256") != amendment_sha256:
        return "published deposit does not hold this signed amendment"
    return None


def _amendment_blockers(root: Path, record: dict, amendment_sha256: str = "") -> list[str]:
    """The v3.5.0 amendment (decisions/20261013_extension_v350_preregistration_amendment.json):
    signed, release pinned to 3.5.0, analysis code pinned and unchanged, the amended record
    unrewritten, and the Zenodo deposit holding the signed record published."""
    blockers = []
    gates = record.get("gates", {})
    if not str(record.get("status", "")).startswith("SIGNED") \
            or not record.get("authorization", {}).get("signed") or not gates.get("author_signed"):
        blockers.append("pre-registration is not signed")
    pin = record.get("release_pin", {})
    if pin.get("commit") != PINNED_RELEASE_COMMIT:
        blockers.append("amendment does not pin workflow release 3.5.0")
    if not _COMMIT_RE.fullmatch(str(pin.get("analysis_commit") or "")) \
            or not gates.get("analysis_commit_pinned"):
        blockers.append("analysis commit is not pinned")
    expected_code = pin.get("analysis_code_sha256")
    if not expected_code:
        blockers.append("analysis code digest is not pinned")
    elif extension_analysis_code_sha256(root) != expected_code:
        blockers.append("extension analysis code changed after the pin")
    amended = record.get("amends_without_rewriting", {})
    amended_path = root / str(amended.get("record", ""))
    if not amended_path.is_file() or sha256(amended_path) != amended.get("sha256"):
        blockers.append("amended pre-registration was rewritten or is missing")
    publication = _publication_blocker(root, record, amendment_sha256)
    if publication:
        blockers.append(publication)
    return blockers


def extension_staging_blockers(project_root: str, amendment_path: str) -> list[str]:
    """Staging or submitting extension inputs needs the signed amendment (its
    signature_rule); the Zenodo publication is required only before the truth join."""
    root = Path(project_root)
    path = Path(amendment_path)
    path = path if path.is_absolute() else root / path
    if not path.is_file():
        return [f"amendment not found: {amendment_path}"]
    record = read_json(path)
    if record.get("schema_version") != AMENDMENT_SCHEMA:
        return ["not a pre-registration amendment"]
    blockers = [item for item in _amendment_blockers(root, record, sha256(path))
                if item not in {"Zenodo pre-registration deposit is not published",
                                "published deposit does not hold this signed amendment"}]
    if not record.get("gates", {}).get("extension_stage_or_submit_permitted"):
        blockers.append("amendment does not permit extension staging")
    return blockers


def _preregistration_blockers(root: Path, preregistration_path: str | None) -> list[str]:
    """The truth join additionally needs a signed confirmatory pre-registration that
    records the public release DOI required by the locked protocol's blocking gates."""
    if not preregistration_path:
        return ["no confirmatory pre-registration supplied"]
    path = Path(preregistration_path)
    path = path if path.is_absolute() else root / path
    if not path.is_file():
        return [f"pre-registration not found: {preregistration_path}"]
    record = read_json(path)
    if record.get("schema_version") == AMENDMENT_SCHEMA:
        return _amendment_blockers(root, record, sha256(path))
    blockers = []
    if record.get("status") != "SIGNED" or not record.get("authorization", {}).get("signed"):
        blockers.append("pre-registration is not signed")
    if not str(record.get("release", {}).get("doi", "")).startswith("10."):
        blockers.append("pre-registration records no public release DOI")
    return blockers


def audit_extension_readiness(project_root: str, protocol_audit_path: str,
                              caller_resources_path: str, output_path: str,
                              preregistration_path: str | None = None) -> dict:
    root = Path(project_root)
    protocol_audit = read_json(protocol_audit_path)
    resources = read_json(caller_resources_path)
    failures = []
    if not protocol_audit.get("valid") or not protocol_audit.get("truth_join_permitted"):
        failures.append("locked protocol audit is not valid")
    ipd = resources.get("common_normalization_reference", {})
    for field in ("allele_list", "sha256_manifest"):
        path = root / ipd.get(field, "")
        if not ipd.get(field) or not path.is_file():
            failures.append(f"missing common normalization {field}")
    callers = resources.get("callers", {})
    required_callers = []
    excluded_callers = {}
    caller_failures = {}
    for caller, item in sorted(callers.items()):
        # decisions/20261009_extension_voting_panels_only.json: a caller removed from the
        # extension by a recorded decision is not required, and is reported as excluded.
        if item.get("extension_required") is False:
            decision = item.get("excluded_by", "")
            if decision and (root / decision).is_file():
                excluded_callers[caller] = decision
            else:
                caller_failures[caller] = ["excluded without a recorded decision"]
            continue
        required_callers.append(caller)
        if item.get("allele_list_sha256") and (root / item.get("allele_list", "")).is_file() \
                and sha256(root / item["allele_list"]) != item["allele_list_sha256"]:
            caller_failures.setdefault(caller, []).append("native allele_list checksum mismatch")
        problems = []
        if item.get("status") != "ready":
            problems.append(f"status={item.get('status', 'missing')}")
        if not item.get("database_release"):
            problems.append("database_release missing")
        allele_list = root / item.get("allele_list", "")
        if not item.get("allele_list") or not allele_list.is_file():
            problems.append("native allele_list missing")
        if not _DIGEST_RE.fullmatch(item.get("container_digest", "")):
            problems.append("immutable container digest missing")
        if problems:
            caller_failures.setdefault(caller, []).extend(problems)
    if caller_failures:
        failures.append("one or more caller resources are not ready")
    truth_join_blockers = _preregistration_blockers(root, preregistration_path)
    result = {
        "schema_version": "panelhla-extension-readiness-1",
        "ready": not failures,
        "failures": failures,
        "caller_failures": caller_failures,
        "required_callers": required_callers,
        "excluded_callers": excluded_callers,
        "protocol_audit_sha256": sha256(protocol_audit_path),
        "caller_resources_sha256": sha256(caller_resources_path),
        "extension_execution_permitted": not failures,
        "truth_join_blockers": truth_join_blockers,
        "truth_join_permitted": bool(not failures and not truth_join_blockers
                                     and protocol_audit.get("truth_join_permitted")),
    }
    write_json(output_path, result)
    return result
