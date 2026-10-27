from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .hla_reference import HLAReference
from .io import canonical_pair, read_json, read_tsv, sha256, write_json, write_tsv
from .panels import PANELS


def evaluate_representability(truth_path: str, caller_resource_manifest: str,
                              output_path: str, summary_path: str) -> dict:
    """Measure whether each exact truth genotype exists in each caller search space."""
    truth = read_tsv(truth_path)
    manifest = read_json(caller_resource_manifest)
    callers = manifest.get("callers", {})
    if not callers:
        raise ValueError("caller resource manifest contains no callers")
    manifest_path = Path(caller_resource_manifest).resolve()
    project_root = next(
        (
            ancestor for ancestor in manifest_path.parents
            if (ancestor / "pyproject.toml").is_file() and (ancestor / "src").is_dir()
        ),
        None,
    )
    if project_root is None:
        raise ValueError("cannot resolve project root for caller-native resources")
    catalogs = {}
    catalog_metadata = {}
    for caller, item in callers.items():
        if not item.get("allele_list") or not item.get("database_release"):
            raise ValueError(f"caller {caller} lacks allele_list or database_release")
        allele_list = Path(item["allele_list"])
        if not allele_list.is_absolute():
            allele_list = project_root.joinpath(*item["allele_list"].split("/"))
        if not allele_list.is_file():
            raise ValueError(f"caller {caller} allele list is missing: {allele_list}")
        if item.get("sha256") and sha256(allele_list) != item["sha256"]:
            raise ValueError(f"caller {caller} allele list checksum mismatch")
        catalogs[caller] = HLAReference.from_files(
            item["database_release"], allele_list,
            deleted_alleles=item.get("deleted_alleles"),
            p_groups=item.get("p_groups"), g_groups=item.get("g_groups"),
        )
        catalog_metadata[caller] = {
            "database_release": item["database_release"],
            "allele_list_sha256": sha256(allele_list),
            "catalog_alleles": item.get("alleles", len(catalogs[caller].alleles)),
        }
    rows = []
    counts = defaultdict(
        lambda: {
            "loci": 0, "representable_loci": 0,
            "truth_allele_copies": 0, "representable_allele_copies": 0,
        }
    )
    for item in truth:
        pair = canonical_pair(item["truth_allele1"], item["truth_allele2"], item["gene"])
        applicable_callers = set(PANELS.get(item["modality"], ()))
        for caller, catalog in sorted(catalogs.items()):
            if caller not in applicable_callers:
                continue
            allele_flags = [allele in catalog.two_field_alleles for allele in pair]
            representable = all(allele_flags)
            rows.append({
                "cohort": item.get("cohort", ""), "subject": item["subject"],
                "modality": item["modality"], "gene": item["gene"], "caller": caller,
                "truth_allele1": pair[0], "truth_allele2": pair[1],
                "allele1_representable": int(allele_flags[0]),
                "allele2_representable": int(allele_flags[1]),
                "truth_representable": int(representable),
                "caller_database_release": catalog.release,
            })
            key = (item["modality"], caller)
            counts[key]["loci"] += 1
            counts[key]["representable_loci"] += int(representable)
            counts[key]["truth_allele_copies"] += len(pair)
            counts[key]["representable_allele_copies"] += sum(allele_flags)
    write_tsv(output_path, rows)
    summary_rows = []
    for (modality, caller), values in sorted(counts.items()):
        metadata = catalog_metadata[caller]
        summary_rows.append({
            "modality": modality,
            "caller": caller,
            "caller_database_release": metadata["database_release"],
            "catalog_alleles": metadata["catalog_alleles"],
            **values,
            "representability": values["representable_loci"] / values["loci"],
            "allele_copy_representability": (
                values["representable_allele_copies"] / values["truth_allele_copies"]
            ),
            "allele_list_sha256": metadata["allele_list_sha256"],
        })
    summary_tsv = Path(output_path).with_name("caller_truth_representability_summary.tsv")
    write_tsv(summary_tsv, summary_rows)
    summary = {
        "schema_version": "caller-truth-representability-2",
        "scope": (
            "Bounded membership check against verified current-deployment native "
            "allele lists for intended-use assay panels; not a reconstruction of "
            "the historical caller run or proof that a present allele was callable"
        ),
        "truth_sha256": sha256(truth_path),
        "caller_resource_manifest_sha256": sha256(caller_resource_manifest),
        "rows_sha256": sha256(output_path),
        # Sibling of this JSON; a bare name keeps the artifact checkout-independent.
        "summary_tsv": summary_tsv.name,
        "summary_tsv_sha256": sha256(summary_tsv),
        "summary": summary_rows,
    }
    write_json(summary_path, summary)
    return summary
