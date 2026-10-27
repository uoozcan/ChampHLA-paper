"""Derive each voting caller's native allele list for the confirmatory extension.

Inputs are the release-bearing components extracted from the deployed caller images
(resources/caller_native/components/). They are verified against the hashes recorded at
extraction, then written as IPD-style `AlleleID,Allele` lists that
champhla_confirmation.hla_reference.HLAReference reads. The database releases are the
content-derived ones in provenance/external_evidence/db_release_resolution.json.

    python scripts/build_caller_native_allele_lists.py
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NATIVE = ROOT / "resources" / "caller_native"
COMPONENTS = NATIVE / "components"

# arcasHLA was not part of the 2026-09-10 extraction. Its list was read on 2026-10-09
# from dat/IMGTHLA/Allelelist.txt inside the image whose digest caller_resources_v2.json
# records (sha256:60c42737...); the file declares IPD-IMGT/HLA 3.40.0.
EXTRA_PINS = {"arcashla__Allelelist.txt":
              "5150f3b3436328f769d38fbdb5d7a751cbff233089d9417202e6b4a9407a9cb7"}

CALLERS = {
    "HLA-HD": ("3.15.0", ["hlahd__dictionary_allele.list"]),
    "OptiType": ("3.13.1", ["optitype__hla_reference_dna.headers",
                            "optitype__hla_reference_rna.headers"]),
    "POLYSOLVER": ("3.11.0", ["polysolver__a_complete.headers",
                              "polysolver__b_complete.headers",
                              "polysolver__c_complete.headers"]),
    "SpecHLA": ("3.38.0", ["spechla__Allelelist.txt"]),
    "T1K": ("3.63.0", ["t1k__dna_seq.headers"]),
    "ArcasHLA": ("3.40.0", ["arcashla__Allelelist.txt"]),
}
POLYSOLVER_RE = re.compile(r"^hla_([a-z0-9]+)_(\d+(?:_\d+)*)([a-z]?)$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pinned_hashes() -> dict[str, str]:
    pins = dict(EXTRA_PINS)
    for name in ("SHA256SUMS", "HEADERS_SHA256SUMS"):
        for line in (COMPONENTS / name).read_text(encoding="utf-8").splitlines():
            digest, _, file = line.strip().partition("  ")
            if digest and file:
                pins[Path(file).name] = digest
    return pins


def parse(name: str, text: str) -> list[tuple[str, str]]:
    """(AlleleID, Allele) pairs; AlleleID is empty where the source has none."""
    pairs = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if name.endswith("Allelelist.txt"):
            if line.startswith("AlleleID"):
                continue
            allele_id, _, allele = line.partition(",")
            pairs.append((allele_id, allele))
        elif name.startswith("hlahd__"):
            allele_id, _, allele = line.partition("\t")
            pairs.append((allele_id, allele.replace("HLA-", "")))
        elif name.startswith("polysolver__"):
            match = POLYSOLVER_RE.match(line.lstrip(">"))
            if match:
                gene, fields, suffix = match.groups()
                pairs.append(("", f"{gene.upper()}*{fields.replace('_', ':')}{suffix.upper()}"))
        elif name.startswith(("optitype__", "t1k__")):
            tokens = line.lstrip(">").split()
            allele = next((t for t in tokens if "*" in t), "")
            allele_id = tokens[0] if tokens and tokens[0].startswith("HLA") and "*" not in tokens[0] else ""
            if allele:
                pairs.append((allele_id, allele.replace("HLA-", "")))
    return pairs


def main() -> int:
    pins = pinned_hashes()
    manifest = {"schema_version": "champhla-caller-native-allele-lists-1", "callers": {}}
    for caller, (release, components) in CALLERS.items():
        rows: dict[str, str] = {}
        sources = []
        for name in components:
            path = COMPONENTS / name
            digest = sha256(path)
            if pins.get(name) != digest:
                raise SystemExit(f"{name}: SHA-256 {digest} does not match the pinned {pins.get(name)}")
            for allele_id, allele in parse(name, path.read_text(encoding="utf-8")):
                rows.setdefault(allele, allele_id)
            sources.append({"component": name, "sha256": digest})
        if not rows:
            raise SystemExit(f"{caller}: no alleles parsed")
        out = NATIVE / f"{caller.replace('*', '').replace('-', '').lower()}_Allelelist.csv"
        lines = [f"# caller: {caller}", f"# database_release: IPD-IMGT/HLA {release}",
                 *(f"# source: {s['component']} sha256={s['sha256']}" for s in sources),
                 "AlleleID,Allele",
                 *(f"{rows[allele]},{allele}" for allele in sorted(rows))]
        out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        manifest["callers"][caller] = {"database_release": release,
                                       "allele_list": out.relative_to(ROOT).as_posix(),
                                       "alleles": len(rows), "sha256": sha256(out),
                                       "sources": sources}
        print(f"{caller}: {len(rows)} alleles -> {out.name}")
    (NATIVE / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                          encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
