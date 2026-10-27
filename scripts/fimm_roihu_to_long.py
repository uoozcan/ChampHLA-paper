#!/usr/bin/env python3
"""Convert the FIMM secure wide call tables into the long inputs run_fimm_analysis expects.

The FIMM results on Roihu are stored one specimen per row with one column per
``<modality>_<caller>_<locus>`` combination and the two alleles packed into a single
``allele1|allele2`` cell. ``champhla_recovery.fimm`` consumes long rows instead, so this
script transposes them and builds the specimen-to-donor crosswalk alongside.

Two things it does NOT do, deliberately:

* It does not guess donor structure from identifier strings. The FIMM specimen
  identifiers span more than a dozen formats and a prefix heuristic silently merged 106
  unrelated specimens into one donor during development. For the pseudonymised cohort
  tiers every specimen is therefore exported as its own donor and the tier is declared
  specimen-level. Only the flow tier gets true donor grouping, because
  ``hla_a2_flow_per_donor.tsv`` records the member specimens explicitly in
  ``call_samples``.
* It does not emit real identifiers. Export identifiers are minted in the ``FIMM-``
  namespace and the mapping stays inside the secure environment.

Run inside /scratch on Roihu. Outputs land in --out-dir together with a manifest whose
checksums are already frozen.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

LOCI = ("A", "B", "C")
MODALITY_ALIASES = {"scrna": "scrna", "bulkrna": "bulk_rna", "wes": "wes"}
MISSING_TOKENS = {"", "-", "na", "n/a", ".", "none", "missing"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, delimiter="\t", fieldnames=fields,
            extrasaction="ignore", lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_column(column: str) -> tuple[str, str, str] | None:
    """``bulkrna_OptiType_A`` -> (``bulk_rna``, ``optitype``, ``A``)."""
    parts = column.split("_")
    if len(parts) < 3 or parts[-1] not in LOCI:
        return None
    modality = MODALITY_ALIASES.get(parts[0].lower())
    if modality is None:
        return None
    # Caller names are folded to lower case on purpose: the source table writes the same
    # tool as "arcashla" on scRNA and "arcasHLA" on bulk RNA and WES. Left unfolded, the
    # shared-caller detection would report the panels as disjoint when they are identical.
    return modality, "_".join(parts[1:-1]).lower(), parts[-1]


def split_pair(value: str) -> tuple[str, str]:
    text = (value or "").strip()
    if not text:
        return "", ""
    parts = text.split("|")
    first = parts[0].strip()
    second = parts[1].strip() if len(parts) > 1 else ""
    if first.lower() in MISSING_TOKENS:
        first = ""
    if second.lower() in MISSING_TOKENS:
        second = ""
    return first, second


def build_calls(wide_rows: list[dict[str, str]], keep: set[str] | None) -> list[dict[str, str]]:
    columns = [
        (column, parsed)
        for column in (wide_rows[0] if wide_rows else {})
        if column != "sample_id" and (parsed := parse_column(column))
    ]
    calls: list[dict[str, str]] = []
    for row in wide_rows:
        specimen = row["sample_id"].strip()
        if keep is not None and specimen not in keep:
            continue
        for column, (modality, caller, locus) in columns:
            allele1, allele2 = split_pair(row.get(column, ""))
            if not allele1 and not allele2:
                continue
            calls.append({
                "specimen_id": specimen, "modality": modality, "locus": locus,
                "caller": caller, "allele1": allele1, "allele2": allele2,
            })
    return calls


def identity_crosswalk(specimens: list[str], tier: str) -> list[dict[str, str]]:
    """One specimen, one donor. Used where donor structure is not establishable."""
    rows = []
    for index, specimen in enumerate(sorted(set(specimens)), start=1):
        export_id = f"FIMM-{tier}-{index:05d}"
        rows.append({
            "specimen_id": specimen, "donor_id": specimen, "export_id": export_id,
            "export_sample_id": f"{export_id}-S1", "collection_order": "1",
        })
    return rows


def flow_crosswalk(
    flow_rows: list[dict[str, str]], known_specimens: set[str], tier: str
) -> tuple[list[dict[str, str]], list[str]]:
    """Donor grouping taken from the flow table's own recorded member specimens."""
    rows: list[dict[str, str]] = []
    notes: list[str] = []
    for index, record in enumerate(sorted(flow_rows, key=lambda r: r["donor"]), start=1):
        donor = record["donor"].strip()
        export_id = f"FIMM-{tier}-{index:05d}"
        members = [
            member.strip() for member in (record.get("call_samples") or "").split(",")
            if member.strip()
        ]
        linked = [member for member in members if member in known_specimens]
        if not linked:
            notes.append(f"flow donor {index:05d}: no member specimen present in the call table")
            continue
        for order, specimen in enumerate(sorted(linked), start=1):
            rows.append({
                "specimen_id": specimen, "donor_id": donor, "export_id": export_id,
                "export_sample_id": f"{export_id}-S{order}", "collection_order": str(order),
            })
    return rows, notes


def build_flow(
    matched: list[dict[str, str]], unmatched: list[dict[str, str]]
) -> list[dict[str, str]]:
    rows = [
        {"donor_id": record["donor"].strip(), "flow_positive": record["flow_a2"].strip()}
        for record in matched
    ]
    seen = {row["donor_id"] for row in rows}
    for record in unmatched:
        donor = record["donor"].strip()
        if donor in seen:
            continue
        seen.add(donor)
        rows.append({"donor_id": donor, "flow_positive": record["flow_a2"].strip()})
    return rows


def build_imbalance(
    rows: list[dict[str, str]], keep: set[str] | None
) -> list[dict[str, str]]:
    output = []
    for row in rows:
        specimen = row["sample_id"].strip()
        if keep is not None and specimen not in keep:
            continue
        if (row.get("modality") or "").strip().lower() not in {"wes", ""}:
            continue
        output.append({
            "specimen_id": specimen,
            "locus": (row.get("gene") or "").strip().upper().replace("HLA-", ""),
            "major_fraction": (row.get("major_allele_fraction") or "").strip(),
            "informative_heterozygous_sites": (row.get("het_variant_count") or "").strip(),
        })
    return output


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tier", required=True, choices=["A", "B", "C"])
    parser.add_argument("--calls-wide", required=True)
    parser.add_argument("--imbalance", required=True)
    parser.add_argument("--flow-per-donor", required=True)
    parser.add_argument("--flow-unmatched", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args(argv)

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    wide = read_tsv(Path(args.calls_wide))
    matched = read_tsv(Path(args.flow_per_donor))
    unmatched = read_tsv(Path(args.flow_unmatched))
    notes: list[str] = []

    specimens = [row["sample_id"].strip() for row in wide]
    if args.tier == "C":
        crosswalk, notes = flow_crosswalk(matched, set(specimens), args.tier)
    else:
        crosswalk = identity_crosswalk(specimens, args.tier)
        notes.append(
            "specimen-level tier: donor structure is not establishable from the "
            "pseudonymised identifiers, so each specimen is its own donor"
        )
    keep = {row["specimen_id"] for row in crosswalk}

    calls = build_calls(wide, keep)
    flow = build_flow(matched, unmatched)
    imbalance = build_imbalance(read_tsv(Path(args.imbalance)), keep)

    write_tsv(
        out / "standardized_hla_calls.tsv", calls,
        ["specimen_id", "modality", "locus", "caller", "allele1", "allele2"],
    )
    write_tsv(
        out / "specimen_donor_crosswalk.tsv", crosswalk,
        ["specimen_id", "donor_id", "export_id", "export_sample_id", "collection_order"],
    )
    write_tsv(out / "bb72_flow.tsv", flow, ["donor_id", "flow_positive"])
    write_tsv(
        out / "spechla_wes_frequency.tsv", imbalance,
        ["specimen_id", "locus", "major_fraction", "informative_heterozygous_sites"],
    )

    tier_label = {
        "A": "A_specimen_level_full_cohort",
        "B": "B_matched_complete_case",
        "C": "C_flow_linked_subset",
    }[args.tier]
    manifest = {
        "schema_version": "panelhla-fimm-analysis-manifest-1",
        "cohort_id": "FIMM_AML_MDS",
        "tier": tier_label,
        "analysis_role": "exploratory",
        "accuracy_eligible": False,
        "external_validation_eligible": False,
        "ipd_imgt_hla_release": "3.65.0",
        "primary_method": "SimplePluralityLex",
        "inputs": {
            name: {"path": f"{name_file}.tsv", "sha256": sha256(out / f"{name_file}.tsv")}
            for name, name_file in (
                ("calls", "standardized_hla_calls"),
                ("crosswalk", "specimen_donor_crosswalk"),
                ("flow", "bb72_flow"),
                ("imbalance", "spechla_wes_frequency"),
            )
        },
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    panels: dict[str, set[str]] = {}
    for row in calls:
        panels.setdefault(row["modality"], set()).add(row["caller"])
    print(f"tier={tier_label}")
    print(f"  specimens_in_source={len(specimens)} specimens_kept={len(keep)}")
    print(f"  donors={len({row['export_id'] for row in crosswalk})}")
    print(f"  call_rows={len(calls)} imbalance_rows={len(imbalance)} flow_rows={len(flow)}")
    for modality in sorted(panels):
        print(f"  panel[{modality}]={','.join(sorted(panels[modality]))}")
    for note in notes:
        print(f"  NOTE: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
