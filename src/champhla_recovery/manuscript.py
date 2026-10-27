from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree

from .io import read_tsv, sha256, write_json, write_tsv
from .registry import validate_registry


PLACEHOLDER_RE = re.compile(
    r"\[(?:AUTHOR|TODO|TBD|PLACEHOLDER)[^\]]*\]|\b(?:TODO|TBD)\b|author verification"
    r"|\bTO CONFIRM\b|\bto be confirmed\b",
    re.I,
)
INVALID_WGS_RE = re.compile(r"(?:0\.399|0\.494|\+30\.66|79/411|205/411)")
RESULT_REF_RE = re.compile(r"\[RESULT:([A-Za-z0-9_.:-]+)\]")
FIGURE_RE = re.compile(r"\b(?:Figure|Fig\.)\s*\d+", re.I)
ABSTRACT_RE = re.compile(r"^## Abstract[ \t]*\n(.*?)(?=^## )", re.M | re.S)
# Percentages, n/N counts and decimal effect sizes (concordance, phi, p values).
# Denominators such as "153 WES loci" are design facts, not performance.
NUMERIC_PERFORMANCE_RE = re.compile(r"\d\s*%|\b\d+\s*/\s*\d+\b|\b\d*\.\d+\b")

# Statuses the claim ledger is allowed to carry. An unrecognised status used to
# pass silently, so a typo -- or a new status such as "exploratory" -- escaped
# every check.
KNOWN_CLAIM_STATUSES = {"supported", "exploratory", "pending", "invalid", "remove"}

# Vocabulary that counts as labelling an exploratory claim where it is made.
# Deliberately small and general rather than tuned to the current wording: it
# recognises the forms this project uses to withhold a confirmed-superiority
# reading, so deleting the hedge fails the check instead of passing silently.
# The check that consumes this used to be absent -- the warning fired for every
# exploratory row without ever reading the manuscript, which meant it asserted a
# check it did not perform.
EXPLORATORY_MARKERS = (
    "exploratory",
    "development evidence",
    "ablation",
    "descriptive",
    "diagnostic",
    "not significant",
    "does not reach significance",
    "does not establish equivalence",
    "not equivalence",
    "does not distinguish",
    "statistically indistinguishable",
)

HEADING_RE = re.compile(r"^#{1,6} .*$", re.M)


def _normalise(text: str) -> str:
    """Lowercase with runs of whitespace collapsed.

    The manuscript is hard-wrapped, so a multi-word marker such as "not
    significantly" is routinely split across a line break. Matching without
    this produces false warnings.
    """
    return re.sub(r"\s+", " ", text).lower()


def _section_containing(text: str, needle: str) -> str | None:
    """The markdown section holding `needle`, or None if it is not present.

    A claim absent from this document is not made in it, so it is not this
    document's job to label it -- that is why the supplementary used to inherit
    warnings about claims that only the main text asserts.
    """
    index = text.find(needle)
    if index < 0:
        return None
    start, end = 0, len(text)
    for match in HEADING_RE.finditer(text):
        if match.start() <= index:
            start = match.start()
        else:
            end = match.start()
            break
    return text[start:end]

# Front and back matter a submission must carry. Each entry is a label and the
# pattern that evidences it. Checked only for the main text of the live route:
# a supplementary file legitimately has no author list, keywords or references
# of its own, so applying these to it produces false positives.
REQUIRED_ELEMENTS = (
    ("references", re.compile(r"^##+\s*References\b", re.M)),
    ("author list", re.compile(r"^##+\s*Authors?\b", re.M)),
    ("author contributions", re.compile(r"authors?'? contributions", re.I)),
    ("ethics statement", re.compile(r"\bethic(?:s|al)\b", re.I)),
    ("funding statement", re.compile(r"\bfunding\b", re.I)),
    ("competing interests", re.compile(r"competing interests|conflicts? of interest", re.I)),
    ("data availability", re.compile(
        r"data (?:and software )?availability|availability of data", re.I)),
    ("keywords", re.compile(r"^##+\s*Keywords\b", re.M)),
)

# What a supplement must carry instead: numbered sections the main text can cite.
SUPPLEMENTARY_ELEMENTS = (
    ("numbered supplementary sections", re.compile(r"^##+\s*S\d+\.", re.M)),
)

AUTHOR_GATE_SCHEMA = "panelhla-fimm-submission-gate-2"


def _load_author_gate(path: str) -> tuple[dict | None, list[str], list[str]]:
    """Return a validated author gate, pending items, and structural failures."""
    gate_path = Path(path)
    if not gate_path.is_file():
        return None, [], [f"author gate is missing: {gate_path}"]
    try:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [], [f"author gate cannot be read: {gate_path}: {exc}"]
    if not isinstance(gate, dict):
        return None, [], ["author gate must be a JSON object"]

    failures = []
    if gate.get("schema_version") != AUTHOR_GATE_SCHEMA:
        failures.append(
            "author gate has unknown schema_version: "
            f"{gate.get('schema_version')!r}"
        )
    submission_allowed = gate.get("submission_allowed")
    if not isinstance(submission_allowed, bool):
        failures.append("author gate submission_allowed must be boolean")
    blocking_items = gate.get("blocking_items")
    if not isinstance(blocking_items, list) or not all(
            isinstance(item, str) and item.strip() for item in blocking_items):
        failures.append("author gate blocking_items must be a list of non-empty strings")
        blocking_items = []
    else:
        blocking_items = [item.strip() for item in blocking_items]
    if submission_allowed is True and blocking_items:
        failures.append("author gate permits submission while blocking_items remain")
    if submission_allowed is False and not blocking_items:
        failures.append("author gate blocks submission but lists no blocking_items")
    pending = [f"FIMM: {item}" for item in blocking_items] if submission_allowed is False else []
    return gate, pending, failures


def extract_docx_text(path: str) -> str:
    with zipfile.ZipFile(path) as archive:
        root = ElementTree.fromstring(archive.read("word/document.xml"))
    paragraphs = []
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    for paragraph in root.iter(namespace + "p"):
        text = "".join(node.text or "" for node in paragraph.iter(namespace + "t"))
        if text.strip():
            paragraphs.append(text)
    return "\n".join(paragraphs) + "\n"


def write_docx_text(source: str, output: str) -> None:
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(extract_docx_text(source), encoding="utf-8")


def audit_claims(manuscript: str, registry_path: str, claims_path: str, output: str,
                 root: str | None = None, author_gate: str | None = None) -> dict:
    path = Path(manuscript)
    text = extract_docx_text(str(path)) if path.suffix.lower() == ".docx" else path.read_text(encoding="utf-8")
    rows = read_tsv(registry_path)
    registry = {row["result_id"]: row for row in rows}
    claims = read_tsv(claims_path)
    failures = validate_registry(registry_path, root)
    warnings = []

    placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
    pending_author_input = []
    author_input_failures = set()
    if placeholders:
        # A placeholder is a real submission blocker, but it is outstanding
        # author input rather than a defect in the analysis or the code. It is
        # reported separately so a continuous-integration gate can stay
        # meaningful about code health while the manuscript is still being
        # filled in. submission_ready remains False either way.
        pending_author_input = placeholders
        failure = f"manuscript contains {len(placeholders)} placeholder marker(s)"
        failures.append(failure)
        author_input_failures.add(failure)
    author_gate_status = None
    author_gate_path = None
    if author_gate is not None:
        gate, gate_pending, gate_failures = _load_author_gate(author_gate)
        failures.extend(gate_failures)
        pending_author_input.extend(gate_pending)
        if gate is not None:
            author_gate_status = gate.get("status")
            gate_file = Path(author_gate).resolve()
            if root:
                try:
                    author_gate_path = gate_file.relative_to(Path(root).resolve()).as_posix()
                except ValueError:
                    author_gate_path = gate_file.as_posix()
            else:
                author_gate_path = gate_file.as_posix()
        if gate_pending and not gate_failures:
            failure = f"author gate has {len(gate_pending)} unresolved item(s)"
            failures.append(failure)
            author_input_failures.add(failure)
    if INVALID_WGS_RE.search(text):
        failures.append("manuscript contains a historical invalid-WGS performance number")
    abstract_match = ABSTRACT_RE.search(text)
    if abstract_match:
        abstract = abstract_match.group(1)
        for result_id in RESULT_REF_RE.findall(abstract):
            if result_id in registry and registry[result_id].get("abstract_allowed") != "1":
                failures.append(f"abstract cites a result not allowed in the abstract: {result_id}")
        # decisions/publication_route.json governs whether the Abstract may report
        # numeric performance at all; registry rows alone cannot authorise it.
        route_path = (Path(root) if root else path.parent) / "decisions" / "publication_route.json"
        if route_path.is_file():
            route = json.loads(route_path.read_text(encoding="utf-8"))
            if route.get("abstract_numeric_performance_allowed") is False:
                hits = sorted(set(NUMERIC_PERFORMANCE_RE.findall(abstract)))
                if hits:
                    failures.append(
                        "abstract reports numeric performance although "
                        f"abstract_numeric_performance_allowed is false: {hits}")
    for result_id in RESULT_REF_RE.findall(text):
        if result_id not in registry:
            failures.append(f"unknown result reference: {result_id}")
        elif registry[result_id]["validity"] != "valid":
            failures.append(f"manuscript cites invalid result: {result_id}")
    external_valid = any(
        row["analysis_status"] == "external_confirmation" and row["validity"] == "valid"
        for row in rows
    )
    external_claim = re.compile(
        r"\b(?:externally validated|independent external validation (?:confirmed|demonstrated))\b",
        re.I,
    )
    positive_external_claim = False
    for match in external_claim.finditer(text):
        sentence_start = max(text.rfind(".", 0, match.start()), text.rfind("\n\n", 0, match.start()))
        sentence_end = text.find(".", match.end())
        sentence = text[sentence_start + 1: sentence_end if sentence_end >= 0 else len(text)]
        # A limitation such as "not externally validated" must not be mistaken
        # for the positive validation claim this gate is designed to stop.
        if not re.search(r"\b(?:not|no|without|lack(?:s|ed|ing)?)\b", sentence, re.I):
            positive_external_claim = True
            break
    if positive_external_claim and not external_valid:
        failures.append("external-validation language is unsupported by the result registry")

    route = "method" if "method_conditional" in str(path) else "benchmark" if "benchmark" in str(path) else "source_original"
    is_supplementary = "supplement" in path.name.lower()
    active_claims = [claim for claim in claims if claim.get("draft") in {route, "shared"}]
    claim_fields = set(claims[0]) if claims else set()
    required_claim_fields = {"claim_id", "draft", "section", "claim", "status", "evidence_result_id", "action"}
    if not claims:
        failures.append("claim audit is empty")
    elif required_claim_fields - claim_fields:
        failures.append(f"claim audit missing fields: {sorted(required_claim_fields - claim_fields)}")
    else:
        for claim in active_claims:
            result_id = claim["evidence_result_id"]
            if result_id and result_id not in registry:
                failures.append(f"claim {claim['claim_id']} references unknown result {result_id}")
            if claim["status"] not in KNOWN_CLAIM_STATUSES:
                failures.append(
                    f"claim {claim['claim_id']} has unrecognised status {claim['status']!r}")
            if claim["status"] in {"invalid", "remove"} and claim["draft"] in {"benchmark", "method"}:
                failures.append(f"active draft contains rejected claim record {claim['claim_id']}")
            if claim["status"] == "pending":
                warnings.append(f"pending claim: {claim['claim_id']}")
            # An evidence source is a non-registry citation -- an external
            # diagnosis, or the verification gate itself for a claim about the
            # software rather than about a measured result. Optional column, so
            # a claim ledger written before it existed still validates.
            evidence_source = (claim.get("evidence_source") or "").strip()
            if evidence_source:
                source_path = (Path(root) if root else path.parent) / evidence_source
                if not source_path.exists():
                    failures.append(
                        f"claim {claim['claim_id']} cites a missing evidence source: {evidence_source}")
            if claim["status"] == "exploratory":
                section = _section_containing(text, f"[RESULT:{result_id}]") if result_id else None
                if not result_id:
                    warnings.append(
                        f"exploratory claim cites no registry result, so its labelling "
                        f"cannot be verified: {claim['claim_id']}")
                elif section is not None and not any(
                        marker in _normalise(section) for marker in EXPLORATORY_MARKERS):
                    warnings.append(
                        f"exploratory claim is not labelled as exploratory where it is "
                        f"made: {claim['claim_id']}")
            if claim["status"] == "supported" and not result_id and not evidence_source:
                warnings.append(
                    f"claim {claim['claim_id']} is supported but cites neither a registry "
                    f"result nor an evidence source")

    missing_elements = []
    if route == "benchmark":
        required = SUPPLEMENTARY_ELEMENTS if is_supplementary else REQUIRED_ELEMENTS
        for label, pattern in required:
            if not pattern.search(text):
                missing_elements.append(label)
        if not is_supplementary and not FIGURE_RE.search(text):
            missing_elements.append("numbered figure reference")
        for label in missing_elements:
            warnings.append(f"missing submission element: {label}")

    resolved_path = path.resolve()
    if root:
        try:
            recorded_path = resolved_path.relative_to(Path(root).resolve()).as_posix()
        except ValueError:
            recorded_path = resolved_path.as_posix()
    else:
        recorded_path = resolved_path.as_posix()

    result = {
        "schema_version": "manuscript-claim-audit-1",
        "manuscript": recorded_path,
        "manuscript_sha256": sha256(path),
        "word_count": len(text.split()),
        "draft_route": route,
        "document_kind": "supplementary" if is_supplementary else "main_text",
        "result_references": sorted(set(RESULT_REF_RE.findall(text))),
        "missing_submission_elements": missing_elements,
        "author_gate": author_gate_path,
        "author_gate_status": author_gate_status,
        "pending_author_input": sorted(set(pending_author_input)),
        "blocking_failures": sorted(set(failures) - author_input_failures),
        "failures": sorted(set(failures)),
        "warnings": sorted(set(warnings)),
        "submission_ready": not failures and not warnings,
    }
    write_json(output, result)
    return result


def write_source_issue_register(source_docx: str, output_tsv: str, output_json: str) -> dict:
    text = extract_docx_text(source_docx)
    issues = []
    def add(category: str, severity: str, evidence: str, action: str) -> None:
        issues.append({
            "issue_id": f"MS-{len(issues)+1:03d}", "category": category,
            "severity": severity, "evidence": evidence, "required_action": action,
        })
    if len(text.split()) > 7000:
        add("structure", "high", f"Draft contains {len(text.split())} words.",
            "Replace with journal-length main text and move tutorials/exploratory work out of the main narrative.")
    if PLACEHOLDER_RE.search(text):
        add("placeholder", "high", "Author-confirmation or verification markers remain.",
            "Resolve every marker before submission.")
    if INVALID_WGS_RE.search(text):
        add("invalid_result", "critical", "Abstract/body contains performance from the invalid historical WGS slice.",
            "Remove from performance claims; retain only as a QC lesson.")
    if "MV-floor" in text:
        add("obsolete_headline", "critical", "MV-floor is presented as the reported operating method.",
            "Use the benchmark route by default; keep MV-floor as a comparator/ablation.")
    if "implemented but unbenchmarked long-read" in text or "longreads_hifi" in text:
        add("scope", "medium", "Unvalidated long-read support occupies the main narrative.",
            "Move long-read implementation to software documentation or limitations.")
    if "FIMM" in text and "survival" in text.lower():
        add("exploratory_scope", "high", "FIMM, LOH/HED, and survival analyses are embedded in the draft.",
            "Remove from the main manuscripts and retain only in a clearly exploratory archive.")
    add("claim_consistency", "critical", "Multiple source reports recommend incompatible headlines.",
        "Generate all result prose and tables from the authoritative result registry.")
    add("validation", "critical", "Qualifying three-modality confirmation is incomplete.",
        "Keep method manuscript conditional until frozen unseen-subject and HPRC gates pass.")
    add("comparison", "high", "The selected abstaining baseline can exaggerate fixed-denominator gain if callability is hidden.",
        "Report callability/called-only accuracy and always-call comparators beside it.")
    write_tsv(output_tsv, issues, ["issue_id", "category", "severity", "evidence", "required_action"])
    result = {
        "schema_version": "source-manuscript-issue-register-1",
        "source_sha256": sha256(source_docx), "word_count": len(text.split()),
        "issues": len(issues), "critical": sum(row["severity"] == "critical" for row in issues),
    }
    write_json(output_json, result)
    return result
