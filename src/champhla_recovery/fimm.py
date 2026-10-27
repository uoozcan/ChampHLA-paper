"""Exploratory FIMM AML/MDS cohort analysis.

This module computes the de-identified, checksum-gated exploratory endpoints for the
FIMM AML/MDS application: cross-modality caller agreement, the BB7.2 (HLA-A2) flow
cytometry comparison, and the WES allele-imbalance screen.

Three properties are deliberate and load-bearing:

* **No accuracy endpoint exists here.** FIMM carries no independent laboratory HLA
  typing, so every concordance number is caller-versus-caller agreement, never
  correctness. Nothing in this module may be described as accuracy or as external
  validation of the ChampHLA consensus rule.
* **Same-caller comparisons are reported separately.** A caller present in two
  modalities compares partly against itself across assays, which inflates agreement.
  Every cross-modality endpoint is therefore computed twice, under
  ``full_panel`` and under ``disjoint_callers``.
* **It fails closed.** Unfrozen or drifted input checksums, or an unverifiable donor
  crosswalk, emit ``BLOCKED_EVIDENCE`` and no numeric output at all.

HLA evolutionary divergence and survival analysis are deliberately out of scope; see
``decisions/20260929_fimm_exploratory_application.json``.
"""

from __future__ import annotations

import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Sequence

from .io import read_tsv, sha256, write_json, write_tsv

MANIFEST_SCHEMA = "panelhla-fimm-analysis-manifest-1"
COHORT_ID = "FIMM_AML_MDS"
IPD_RELEASE = "3.65.0"

LOCI = ("A", "B", "C")
MODALITIES = ("scrna", "bulk_rna", "wes")
MODALITY_PAIRS = (("scrna", "bulk_rna"), ("scrna", "wes"), ("bulk_rna", "wes"))
COMPLETE_STATES = {"complete", "tie"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")

REQUIRED_INPUTS = {"calls", "crosswalk", "flow", "imbalance"}


def normalize_modality(value: str) -> str:
    key = value.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "scrnaseq": "scrna", "sc_rna": "scrna", "sc_rnaseq": "scrna",
        "single_cell_rna": "scrna", "bulk": "bulk_rna", "rna": "bulk_rna",
        "bulk_rnaseq": "bulk_rna", "bulkrna": "bulk_rna", "exome": "wes",
    }
    return aliases.get(key, key)


def normalize_locus(value: str) -> str:
    locus = value.strip().upper().replace("HLA-", "")
    if locus not in LOCI:
        raise ValueError(f"unsupported class-I locus: {value!r}")
    return locus


def normalize_allele(value: str, locus: str) -> str:
    text = value.strip().upper().replace("HLA-", "")
    if not text or text in {"NA", "N/A", ".", "NONE", "MISSING", "-"}:
        return ""
    if "*" not in text:
        text = f"{locus}*{text}"
    prefix, fields = text.split("*", 1)
    if prefix != locus:
        raise ValueError(f"allele {value!r} does not match HLA-{locus}")
    parts = fields.split(":")
    if len(parts) < 2:
        raise ValueError(f"allele is not two-field resolvable: {value!r}")
    return f"{locus}*{parts[0]}:{parts[1]}"


def canonical_pair(allele1: str, allele2: str, locus: str) -> tuple[str, str] | None:
    first = normalize_allele(allele1, locus)
    second = normalize_allele(allele2, locus)
    if not first or not second:
        return None
    return tuple(sorted((first, second)))


def caller_panels(call_rows: Iterable[dict[str, str]]) -> dict[str, set[str]]:
    """Map each modality to the set of callers that actually emitted rows for it."""
    panels: dict[str, set[str]] = defaultdict(set)
    for row in call_rows:
        panels[normalize_modality(row["modality"])].add(row["caller"].strip())
    return dict(panels)


def simple_plurality_lex(
    rows: Iterable[dict[str, str]],
    locus: str,
    allowed_callers: Sequence[str] | set[str] | None = None,
) -> dict[str, object]:
    """Equal-weight plurality over a caller panel, lexicographic tie-break.

    ``allowed_callers`` restricts the vote to a caller subset, which is how the
    disjoint-panel sensitivity analysis removes callers shared between two assays.
    """
    votes: Counter[tuple[str, str]] = Counter()
    contributors: set[str] = set()
    partial = 0
    missing = 0
    for row in rows:
        caller = row.get("caller", "").strip()
        if allowed_callers is not None and caller not in allowed_callers:
            continue
        contributors.add(caller)
        first = normalize_allele(row.get("allele1", ""), locus)
        second = normalize_allele(row.get("allele2", ""), locus)
        if first and second:
            votes[tuple(sorted((first, second)))] += 1
        elif first or second:
            partial += 1
        else:
            missing += 1
    panel = ",".join(sorted(contributors))
    if not votes:
        state = "partial" if partial else "missing"
        return {
            "allele1": "", "allele2": "", "call_state": state,
            "support": 0, "complete_votes": 0, "partial_votes": partial,
            "missing_votes": missing, "tie_count": 0,
            "panel": panel, "panel_size": len(contributors),
        }
    support = max(votes.values())
    winners = sorted(pair for pair, count in votes.items() if count == support)
    winner = winners[0]
    return {
        "allele1": winner[0], "allele2": winner[1],
        "call_state": "tie" if len(winners) > 1 else "complete",
        "support": support, "complete_votes": sum(votes.values()),
        "partial_votes": partial, "missing_votes": missing,
        "tie_count": len(winners) if len(winners) > 1 else 0,
        "panel": panel, "panel_size": len(contributors),
    }


def collapse_donor_calls(sample_rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    """Collapse longitudinal specimens to one donor call, or flag the conflict."""
    groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in sample_rows:
        groups[(str(row["export_id"]), str(row["modality"]), str(row["locus"]))].append(row)
    result: list[dict[str, object]] = []
    for (export_id, modality, locus), rows in sorted(groups.items()):
        complete = {
            (str(row["allele1"]), str(row["allele2"]))
            for row in rows if row["call_state"] in COMPLETE_STATES
        }
        if len(complete) > 1:
            state, pair = "longitudinal_conflict", ("", "")
        elif len(complete) == 1:
            pair = next(iter(complete))
            state = "tie" if any(row["call_state"] == "tie" for row in rows) else "complete"
        elif any(row["call_state"] == "partial" for row in rows):
            state, pair = "partial", ("", "")
        else:
            state, pair = "missing", ("", "")
        panel = sorted({
            caller
            for row in rows
            for caller in str(row.get("panel", "")).split(",")
            if caller
        })
        result.append({
            "export_id": export_id, "modality": modality, "locus": locus,
            "allele1": pair[0], "allele2": pair[1], "call_state": state,
            "samples": len(rows), "panel": ",".join(panel), "panel_size": len(panel),
        })
    return result


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> tuple[float | None, float | None]:
    if total <= 0:
        return None, None
    proportion = successes / total
    denominator = 1 + z * z / total
    centre = (proportion + z * z / (2 * total)) / denominator
    half = z * math.sqrt(
        proportion * (1 - proportion) / total + z * z / (4 * total * total)
    ) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def cross_modality_concordance(
    donor_calls: Iterable[dict[str, object]],
    pairs: Sequence[tuple[str, str]] = MODALITY_PAIRS,
    panel_policy: str = "full_panel",
    panels: dict[str, set[str]] | None = None,
) -> list[dict[str, object]]:
    """Exact unordered two-field agreement between assays, per locus and pooled.

    This is agreement, not accuracy: neither modality is a reference. Where a caller
    appears in both panels the comparison is partly self-referential, which is why
    ``shared_callers`` is reported on every row and why the caller supplies a
    ``disjoint_callers`` policy run alongside the full-panel one.
    """
    lookup = {
        (str(row["export_id"]), str(row["modality"]), str(row["locus"])): row
        for row in donor_calls
    }
    donors = sorted({key[0] for key in lookup})
    output: list[dict[str, object]] = []
    for left, right in pairs:
        left_panel = set(panels.get(left, set())) if panels else set()
        right_panel = set(panels.get(right, set())) if panels else set()
        shared = sorted(left_panel & right_panel)
        for label, loci in [(locus, (locus,)) for locus in LOCI] + [("ALL", LOCI)]:
            agreement = overlap = 0
            state_counts: Counter[str] = Counter()
            for donor in donors:
                for locus in loci:
                    a = lookup.get((donor, left, locus), {"call_state": "missing"})
                    b = lookup.get((donor, right, locus), {"call_state": "missing"})
                    a_state, b_state = str(a["call_state"]), str(b["call_state"])
                    state_counts[f"{left}_{a_state}"] += 1
                    state_counts[f"{right}_{b_state}"] += 1
                    if a_state in COMPLETE_STATES and b_state in COMPLETE_STATES:
                        overlap += 1
                        if (a.get("allele1"), a.get("allele2")) == (
                            b.get("allele1"), b.get("allele2")
                        ):
                            agreement += 1
            low, high = wilson_interval(agreement, overlap)
            output.append({
                "endpoint": f"{left}_vs_{right}", "locus": label,
                "panel_policy": panel_policy,
                "overlap": overlap, "agreement": agreement,
                "estimate": agreement / overlap if overlap else "",
                "ci_lo": low if low is not None else "",
                "ci_hi": high if high is not None else "",
                "left_panel": ",".join(sorted(left_panel)),
                "right_panel": ",".join(sorted(right_panel)),
                "left_panel_size": len(left_panel),
                "right_panel_size": len(right_panel),
                "shared_callers": ",".join(shared),
                "shared_caller_count": len(shared),
                "thin_panel_flag": int(
                    bool(left_panel) and bool(right_panel)
                    and min(len(left_panel), len(right_panel)) < 3
                ),
                **dict(sorted(state_counts.items())),
            })
    return output


def _is_a02(pair: tuple[str, str], broad: bool) -> bool:
    groups = {"02", "68", "69"} if broad else {"02"}
    return any(allele.split("*", 1)[1].split(":", 1)[0] in groups for allele in pair)


def _metric(successes: int, total: int) -> tuple[object, object, object]:
    low, high = wilson_interval(successes, total)
    if not total:
        return "", "", ""
    return successes / total, low, high


def flow_validation(
    donor_calls: Iterable[dict[str, object]],
    flow_rows: Iterable[dict[str, str]],
    unlinked_positive: int = 0,
    unlinked_negative: int = 0,
) -> list[dict[str, object]]:
    """BB7.2 (HLA-A2) serogroup comparison against flow cytometry.

    ``unlinked_positive`` / ``unlinked_negative`` carry the flow records that could not
    be linked to any sequenced specimen. They are not used in any estimate; they are
    propagated onto every row so the selection denominator travels with the metric and
    cannot be reported without it.
    """
    flow_by_donor: dict[str, set[bool]] = defaultdict(set)
    for row in flow_rows:
        status = row["flow_positive"].strip().lower()
        if status not in {
            "1", "0", "true", "false", "positive", "negative", "yes", "no"
        }:
            raise ValueError(f"invalid flow status: {row['flow_positive']!r}")
        flow_by_donor[row["export_id"]].add(status in {"1", "true", "positive", "yes"})
    calls = {
        (str(row["export_id"]), str(row["modality"])): row
        for row in donor_calls if row["locus"] == "A"
    }
    output: list[dict[str, object]] = []
    for modality in MODALITIES + ("legacy_pooled",):
        if modality == "legacy_pooled" and not any(key[1] == modality for key in calls):
            continue
        for mapping, broad in (("A*02", False), ("A*02/A*68/A*69", True)):
            tp = tn = fp = fn = excluded = 0
            for donor, statuses in sorted(flow_by_donor.items()):
                call = calls.get((donor, modality))
                if (
                    len(statuses) != 1
                    or not call
                    or call["call_state"] not in COMPLETE_STATES
                ):
                    excluded += 1
                    continue
                predicted = _is_a02((str(call["allele1"]), str(call["allele2"])), broad)
                observed = next(iter(statuses))
                if predicted and observed:
                    tp += 1
                elif predicted:
                    fp += 1
                elif observed:
                    fn += 1
                else:
                    tn += 1
            metrics = {
                "sensitivity": _metric(tp, tp + fn), "specificity": _metric(tn, tn + fp),
                "ppv": _metric(tp, tp + fp), "npv": _metric(tn, tn + fn),
                "accuracy": _metric(tp + tn, tp + tn + fp + fn),
            }
            for name, (estimate, low, high) in metrics.items():
                informative = tp + tn + fp + fn
                output.append({
                    "modality": modality, "mapping": mapping, "metric": name,
                    "estimate": estimate, "ci_lo": low, "ci_hi": high,
                    "tp": tp, "tn": tn, "fp": fp, "fn": fn,
                    "informative": informative, "excluded": excluded,
                    "unlinked_flow_positive": unlinked_positive,
                    "unlinked_flow_negative": unlinked_negative,
                    "flow_records_total": (
                        informative + excluded + unlinked_positive + unlinked_negative
                    ),
                    "linkage_fraction": (
                        informative
                        / (informative + excluded + unlinked_positive + unlinked_negative)
                        if (informative + excluded + unlinked_positive + unlinked_negative)
                        else ""
                    ),
                })
    return output


def classify_imbalance(major_fraction: float | None, informative_sites: int | None) -> str:
    if major_fraction is None or informative_sites is None or informative_sites < 20:
        return "insufficient"
    if major_fraction >= 0.80:
        return "threshold_positive_review"
    if 0.35 <= major_fraction <= 0.65:
        return "balanced"
    return "observed_imbalance_review"


def imbalance_screen(
    rows: Iterable[dict[str, str]],
    donor_calls: Iterable[dict[str, object]],
    sample_to_export: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    """Screen the earliest eligible WES specimen per donor for allelic imbalance.

    A category is a screening flag for review, never a confirmed loss of
    heterozygosity call.
    """
    linked: list[tuple[dict[str, str], str, int]] = []
    for row in rows:
        specimen = row["specimen_id"]
        mapping = sample_to_export.get(specimen)
        if not mapping:
            continue
        export_id = str(mapping["export_id"])
        order = int(mapping["collection_order"])
        linked.append((row, export_id, order))
    earliest_order = {
        export_id: min(order for _, candidate, order in linked if candidate == export_id)
        for export_id in {candidate for _, candidate, _ in linked}
    }
    earliest: dict[tuple[str, str], dict[str, str]] = {}
    for row, export_id, order in linked:
        if order != earliest_order[export_id]:
            continue
        locus = normalize_locus(row["locus"])
        key = (export_id, locus)
        if key in earliest:
            raise ValueError(
                f"duplicate imbalance record in earliest WES specimen: {export_id} HLA-{locus}"
            )
        earliest[key] = row
    wes = {
        (str(row["export_id"]), str(row["locus"])): row
        for row in donor_calls if row["modality"] == "wes"
    }
    output: list[dict[str, object]] = []
    for (export_id, locus), row in sorted(earliest.items()):
        call = wes.get((export_id, locus))
        heterozygous = bool(
            call and call["call_state"] in COMPLETE_STATES
            and call["allele1"] != call["allele2"]
        )
        fraction_text = row.get("major_fraction", "").strip()
        sites_text = row.get("informative_heterozygous_sites", "").strip()
        fraction = float(fraction_text) if fraction_text else None
        sites = int(sites_text) if sites_text else None
        category = (
            classify_imbalance(fraction, sites) if heterozygous else "excluded_nonheterozygous"
        )
        output.append({
            "export_id": export_id, "locus": locus,
            "major_fraction": fraction if fraction is not None else "",
            "informative_heterozygous_sites": sites if sites is not None else "",
            "category": category,
        })
    return output


def _resolve_inputs(
    manifest_path: Path, manifest: dict
) -> tuple[dict[str, Path], list[str], list[dict[str, str]]]:
    resolved: dict[str, Path] = {}
    failures: list[str] = []
    provenance: list[dict[str, str]] = []
    for name, descriptor in sorted(manifest.get("inputs", {}).items()):
        path = Path(descriptor.get("path", ""))
        if not path.is_absolute():
            path = manifest_path.parent / path
        expected = descriptor.get("sha256", "")
        if not path.is_file():
            failures.append(f"{name}: missing input")
            observed = ""
        else:
            observed = sha256(path)
            if not HEX64.fullmatch(expected):
                failures.append(f"{name}: checksum is not frozen")
            elif observed != expected:
                failures.append(f"{name}: checksum mismatch")
        resolved[name] = path
        provenance.append({
            "input": name, "filename": path.name,
            "expected_sha256": expected, "observed_sha256": observed,
        })
    return resolved, failures, provenance


def _fields(rows: list[dict[str, object]]) -> list[str]:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    return fields


def _write_rows(
    path: Path, rows: list[dict[str, object]], fallback_fields: list[str]
) -> None:
    write_tsv(path, rows, _fields(rows) if rows else fallback_fields)


def _stable_value(value: object) -> str:
    if value == "" or value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def _legacy_sensitivity(
    call_rows: list[dict[str, str]],
    donor_to_export: dict[str, str],
    flow_rows: list[dict[str, str]],
) -> list[dict[str, object]]:
    by_method: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in call_rows:
        method = row["method"]
        export_id = row.get("export_id", "") or donor_to_export.get(row.get("donor_id", ""), "")
        if not export_id:
            raise ValueError("legacy call cannot be linked to a verified donor pseudonym")
        locus = normalize_locus(row["locus"])
        pair = canonical_pair(row.get("allele1", ""), row.get("allele2", ""), locus)
        state = row.get("call_state", "complete")
        if state in COMPLETE_STATES and pair is None:
            raise ValueError("legacy complete call lacks a complete pair")
        by_method[method].append({
            "export_id": export_id, "modality": normalize_modality(row["modality"]),
            "locus": locus, "allele1": pair[0] if pair else "",
            "allele2": pair[1] if pair else "", "call_state": state,
        })
    summary: list[dict[str, object]] = []
    for method, calls in sorted(by_method.items()):
        if any(row["modality"] in MODALITIES for row in calls):
            for row in cross_modality_concordance(calls):
                if row["locus"] != "ALL":
                    continue
                for metric in ("overlap", "agreement", "estimate"):
                    summary.append({
                        "record_key": f"{method}|concordance|{row['endpoint']}|{metric}",
                        "method": method, "endpoint": row["endpoint"], "stratum": "ALL",
                        "metric": metric, "value": _stable_value(row[metric]),
                    })
        pooled = [row for row in calls if row["modality"] == "legacy_pooled"]
        if pooled:
            for row in flow_validation(pooled, flow_rows):
                if row["modality"] != "legacy_pooled":
                    continue
                for metric in ("tp", "tn", "fp", "fn", "informative", "excluded", "estimate"):
                    summary.append({
                        "record_key": f"{method}|flow|{row['mapping']}|{row['metric']}|{metric}",
                        "method": method, "endpoint": f"flow_{row['metric']}",
                        "stratum": row["mapping"], "metric": metric,
                        "value": _stable_value(row[metric]),
                    })
    return summary


def _reconcile_legacy(
    observed: list[dict[str, object]], expected: list[dict[str, str]]
) -> dict[str, object]:
    observed_map = {str(row["record_key"]): str(row["value"]) for row in observed}
    expected_map = {row["record_key"]: row["value"] for row in expected}
    missing = sorted(set(expected_map) - set(observed_map))
    unexpected = sorted(set(observed_map) - set(expected_map))
    mismatches = sorted(
        key for key in set(observed_map) & set(expected_map)
        if observed_map[key] != expected_map[key]
    )
    passed = not missing and not unexpected and not mismatches
    return {
        "schema_version": "panelhla-fimm-legacy-reconciliation-1",
        "status": "REPRODUCED" if passed else "DISCREPANCY_BLOCKED",
        "passed": passed, "missing_keys": missing, "unexpected_keys": unexpected,
        "mismatched_keys": mismatches,
    }


def _registry_rows(
    concordance: list[dict[str, object]],
    flow: list[dict[str, object]],
    imbalance: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Analysis-local result rows, later mapped into the repository result registry."""
    output: list[dict[str, object]] = []
    for row in concordance:
        if row["locus"] != "ALL":
            continue
        policy = str(row["panel_policy"]).upper()
        output.append({
            "result_id": f"FIMM_CONCORDANCE_{str(row['endpoint']).upper()}_{policy}",
            "result_kind": "concordance",
            "endpoint": f"cross_modality_caller_agreement:{row['endpoint']}",
            "panel_policy": row["panel_policy"],
            "estimate": row["estimate"], "ci_lo": row["ci_lo"], "ci_hi": row["ci_hi"],
            "unit": "proportion", "denominator": row["overlap"],
            "shared_callers": row["shared_callers"],
            "evidence_role": "exploratory", "abstract_allowed": 0,
            "claim_boundary": (
                "cross-modality caller agreement; FIMM carries no independent HLA truth, "
                "so this is not accuracy and not external validation"
            ),
        })
    for row in flow:
        scope = "BROAD" if row["mapping"] != "A*02" else "STRICT"
        output.append({
            "result_id": (
                f"FIMM_FLOW_{str(row['modality']).upper()}_{scope}_{str(row['metric']).upper()}"
            ),
            "result_kind": "flow-comparison",
            "endpoint": f"bb72_serogroup_agreement:{row['metric']}",
            "panel_policy": "flow_linked",
            "estimate": row["estimate"], "ci_lo": row["ci_lo"], "ci_hi": row["ci_hi"],
            "unit": "proportion", "denominator": row["informative"],
            "shared_callers": "",
            "evidence_role": "exploratory", "abstract_allowed": 0,
            "claim_boundary": (
                "serogroup-level HLA-A2 agreement on flow-linked donors only; "
                f"{row['excluded']} excluded and {row['unlinked_flow_positive']} positive plus "
                f"{row['unlinked_flow_negative']} negative flow records were never linked"
            ),
        })
    counts = Counter(str(row["category"]) for row in imbalance)
    for category, count in sorted(counts.items()):
        output.append({
            "result_id": f"FIMM_IMBALANCE_{category.upper()}",
            "result_kind": "categorical-summary",
            "endpoint": "wes_allele_imbalance_category",
            "panel_policy": "wes_earliest_specimen",
            "estimate": count, "ci_lo": "", "ci_hi": "",
            "unit": "donor-locus records", "denominator": len(imbalance),
            "shared_callers": "",
            "evidence_role": "exploratory", "abstract_allowed": 0,
            "claim_boundary": "screening category for review only; never a confirmed LOH call",
        })
    return output


def _build_sample_calls(
    call_groups: dict[tuple[str, str, str], list[dict[str, str]]],
    sample_map: dict[str, dict[str, object]],
    allowed_by_modality: dict[str, set[str]] | None = None,
) -> list[dict[str, object]]:
    sample_calls: list[dict[str, object]] = []
    for (specimen, modality, locus), rows in sorted(call_groups.items()):
        allowed = allowed_by_modality.get(modality) if allowed_by_modality else None
        if allowed is not None and not allowed:
            continue
        call = simple_plurality_lex(rows, locus, allowed)
        sample_calls.append({
            "export_id": sample_map[specimen]["export_id"],
            "export_sample_id": sample_map[specimen]["export_sample_id"],
            "collection_order": sample_map[specimen]["collection_order"],
            "modality": modality, "locus": locus, **call,
        })
    present = {
        (str(row["export_sample_id"]), str(row["modality"]), str(row["locus"]))
        for row in sample_calls
    }
    for specimen, modality, _ in sorted(call_groups):
        if allowed_by_modality is not None and not allowed_by_modality.get(modality):
            continue
        for locus in LOCI:
            key = (str(sample_map[specimen]["export_sample_id"]), modality, locus)
            if key in present:
                continue
            present.add(key)
            sample_calls.append({
                "export_id": sample_map[specimen]["export_id"],
                "export_sample_id": sample_map[specimen]["export_sample_id"],
                "collection_order": sample_map[specimen]["collection_order"],
                "modality": modality, "locus": locus, "allele1": "", "allele2": "",
                "call_state": "missing", "support": 0, "complete_votes": 0,
                "partial_votes": 0, "missing_votes": 0, "tie_count": 0,
                "panel": "", "panel_size": 0,
            })
    return sample_calls


def _densify_donor_calls(
    donor_calls: list[dict[str, object]], export_ids: Iterable[str]
) -> list[dict[str, object]]:
    present = {
        (str(row["export_id"]), str(row["modality"]), str(row["locus"]))
        for row in donor_calls
    }
    for export_id in sorted(set(export_ids)):
        for modality in MODALITIES:
            for locus in LOCI:
                if (export_id, modality, locus) not in present:
                    donor_calls.append({
                        "export_id": export_id, "modality": modality, "locus": locus,
                        "allele1": "", "allele2": "", "call_state": "missing",
                        "samples": 0, "panel": "", "panel_size": 0,
                    })
    donor_calls.sort(
        key=lambda row: (str(row["export_id"]), str(row["modality"]), str(row["locus"]))
    )
    return donor_calls


def run_fimm_analysis(manifest_path: str | Path, output_dir: str | Path) -> dict[str, object]:
    manifest_file = Path(manifest_path).resolve()
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    failures: list[str] = []
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        failures.append("unsupported manifest schema")
    if manifest.get("cohort_id") != COHORT_ID:
        failures.append(f"cohort_id must be {COHORT_ID}")
    if manifest.get("ipd_imgt_hla_release") != IPD_RELEASE:
        failures.append(f"IPD-IMGT/HLA release must be {IPD_RELEASE}")
    missing = sorted(REQUIRED_INPUTS - set(manifest.get("inputs", {})))
    if missing:
        failures.append(f"missing input declarations: {missing}")
    inputs, input_failures, provenance = _resolve_inputs(manifest_file, manifest)
    failures.extend(input_failures)
    legacy_inputs: dict[str, Path] = {}
    if manifest.get("legacy_inputs"):
        legacy_inputs, legacy_failures, legacy_provenance = _resolve_inputs(
            manifest_file, {"inputs": manifest["legacy_inputs"]}
        )
        failures.extend(f"legacy_{failure}" for failure in legacy_failures)
        provenance.extend(
            {**row, "input": f"legacy_{row['input']}"} for row in legacy_provenance
        )
    provenance_doc = {
        "schema_version": "panelhla-fimm-provenance-1", "cohort_id": COHORT_ID,
        "tier": manifest.get("tier", ""),
        "manifest_filename": manifest_file.name, "manifest_sha256": sha256(manifest_file),
        "pipeline_filename": Path(__file__).name, "pipeline_sha256": sha256(Path(__file__)),
        "ipd_imgt_hla_release": manifest.get("ipd_imgt_hla_release"), "inputs": provenance,
        "secure_paths_exported": False,
        "accuracy_endpoint_present": False,
        "external_validation_claim_permitted": False,
    }
    write_json(output / "provenance.json", provenance_doc)
    if failures:
        status = {
            "schema_version": "panelhla-fimm-analysis-status-1", "status": "BLOCKED_EVIDENCE",
            "failures": failures, "numeric_outputs_emitted": False,
        }
        write_json(output / "analysis_status.json", status)
        return status

    crosswalk_rows = read_tsv(inputs["crosswalk"])
    sample_map: dict[str, dict[str, object]] = {}
    donor_to_export: dict[str, str] = {}
    for row in crosswalk_rows:
        specimen, donor, export_id = row["specimen_id"], row["donor_id"], row["export_id"]
        if not export_id.startswith("FIMM-"):
            raise ValueError("export IDs must use the FIMM- pseudonym namespace")
        if donor in donor_to_export and donor_to_export[donor] != export_id:
            raise ValueError("one real donor maps to multiple export IDs")
        donor_to_export[donor] = export_id
        sample_map[specimen] = {
            "export_id": export_id, "export_sample_id": row["export_sample_id"],
            "collection_order": int(row["collection_order"]),
        }

    raw_calls = read_tsv(inputs["calls"])
    call_groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in raw_calls:
        specimen = row["specimen_id"]
        if specimen not in sample_map:
            raise ValueError(f"call specimen absent from verified crosswalk: {specimen}")
        modality = normalize_modality(row["modality"])
        if modality not in MODALITIES:
            raise ValueError(f"unsupported modality: {modality}")
        locus = normalize_locus(row["locus"])
        call_groups[(specimen, modality, locus)].append(row)

    panels = caller_panels(raw_calls)
    sample_calls = _build_sample_calls(call_groups, sample_map)
    donor_calls = _densify_donor_calls(
        collapse_donor_calls(sample_calls), donor_to_export.values()
    )

    concordance = cross_modality_concordance(donor_calls, panel_policy="full_panel", panels=panels)
    for left, right in MODALITY_PAIRS:
        shared = panels.get(left, set()) & panels.get(right, set())
        if not shared:
            continue
        restricted = {
            left: panels.get(left, set()) - shared,
            right: panels.get(right, set()) - shared,
        }
        disjoint_samples = _build_sample_calls(call_groups, sample_map, restricted)
        disjoint_donors = _densify_donor_calls(
            collapse_donor_calls(disjoint_samples), donor_to_export.values()
        )
        concordance.extend(cross_modality_concordance(
            disjoint_donors, pairs=[(left, right)],
            panel_policy="disjoint_callers", panels=restricted,
        ))

    flow_rows = []
    unlinked_positive = unlinked_negative = 0
    for row in read_tsv(inputs["flow"]):
        donor = row["donor_id"]
        if donor not in donor_to_export:
            positive = row["flow_positive"].strip().lower() in {
                "1", "true", "positive", "yes"
            }
            unlinked_positive += int(positive)
            unlinked_negative += int(not positive)
            continue
        flow_rows.append({
            "export_id": donor_to_export[donor], "flow_positive": row["flow_positive"],
        })
    flow = flow_validation(donor_calls, flow_rows, unlinked_positive, unlinked_negative)

    legacy_status = "NOT_SUPPLIED"
    if "calls" in legacy_inputs:
        legacy_summary = _legacy_sensitivity(
            read_tsv(legacy_inputs["calls"]), donor_to_export, flow_rows
        )
        _write_rows(
            output / "legacy_sensitivity.tsv", legacy_summary,
            ["record_key", "method", "endpoint", "stratum", "metric", "value"],
        )
        if "expected" in legacy_inputs:
            reconciliation = _reconcile_legacy(
                legacy_summary, read_tsv(legacy_inputs["expected"])
            )
            legacy_status = str(reconciliation["status"])
        else:
            legacy_status = "BLOCKED_EVIDENCE"
            reconciliation = {
                "schema_version": "panelhla-fimm-legacy-reconciliation-1",
                "status": "BLOCKED_EVIDENCE", "passed": False,
                "reason": "checksum-frozen expected legacy summary not supplied",
            }
        write_json(output / "legacy_reconciliation.json", reconciliation)

    imbalance = imbalance_screen(read_tsv(inputs["imbalance"]), donor_calls, sample_map)
    registry = _registry_rows(concordance, flow, imbalance)

    cohort_flow = [
        {"stage": "verified_crosswalk", "unit": "donors", "count": len(donor_to_export)},
        {"stage": "verified_crosswalk", "unit": "specimens", "count": len(sample_map)},
        {"stage": "plurality_input", "unit": "specimens",
         "count": len({key[0] for key in call_groups})},
        {"stage": "plurality_output", "unit": "donor_modality_loci", "count": len(donor_calls)},
        {"stage": "bb72_linked", "unit": "donors",
         "count": len({row["export_id"] for row in flow_rows})},
        {"stage": "bb72_unlinked", "unit": "flow_records",
         "count": unlinked_positive + unlinked_negative},
        {"stage": "imbalance_screen", "unit": "donor_loci", "count": len(imbalance)},
    ]
    panel_rows = [
        {"modality": modality, "panel": ",".join(sorted(callers)), "panel_size": len(callers)}
        for modality, callers in sorted(panels.items())
    ]

    _write_rows(output / "cohort_flow.tsv", cohort_flow, ["stage", "unit", "count"])
    _write_rows(output / "caller_panels.tsv", panel_rows, ["modality", "panel", "panel_size"])
    _write_rows(
        output / "sample_plurality.tsv", sample_calls,
        ["export_id", "export_sample_id", "modality", "locus"],
    )
    _write_rows(
        output / "donor_plurality.tsv", donor_calls, ["export_id", "modality", "locus"]
    )
    _write_rows(
        output / "cross_modality_concordance.tsv", concordance,
        ["endpoint", "locus", "panel_policy", "overlap", "agreement"],
    )
    _write_rows(output / "bb72_metrics.tsv", flow, ["modality", "mapping", "metric"])
    _write_rows(
        output / "wes_allele_imbalance.tsv", imbalance, ["export_id", "locus", "category"]
    )
    _write_rows(
        output / "fimm_result_registry.tsv", registry,
        ["result_id", "result_kind", "endpoint", "estimate"],
    )
    # Figures are deliberately NOT generated here. The exported TSVs are the source
    # artifacts, and scripts/generate_figures.py renders every published figure under
    # the repository style contract (four formats, 600 dpi, manifest entry). Rendering
    # them twice would let the secure copy and the published copy drift apart.

    exported_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in output.rglob("*") if path.suffix in {".tsv", ".json"}
    )
    privacy_failures = [
        label for label, values in (
            ("real_donor_id", donor_to_export),
            ("secure_specimen_id", sample_map),
            ("secure_absolute_path", ["/scratch/", "/projappl/"]),
        )
        if any(value and value in exported_text for value in values)
    ]
    if re.search(r"\b\d{4}-\d{2}-\d{2}\b", exported_text):
        privacy_failures.append("calendar_date")
    if privacy_failures:
        raise ValueError(f"privacy audit failed: {sorted(set(privacy_failures))}")
    write_json(output / "privacy_audit.json", {
        "schema_version": "panelhla-fimm-privacy-audit-1", "passed": True,
        "checks": [
            "real_donor_ids", "secure_specimen_ids", "calendar_dates", "secure_absolute_paths"
        ],
    })

    checksums = []
    for path in sorted(candidate for candidate in output.rglob("*") if candidate.is_file()):
        if path.name not in {"artifact_checksums.tsv", "analysis_status.json"}:
            checksums.append({
                "artifact": path.relative_to(output).as_posix(), "sha256": sha256(path),
            })
    _write_rows(output / "artifact_checksums.tsv", checksums, ["artifact", "sha256"])
    status = {
        "schema_version": "panelhla-fimm-analysis-status-1", "status": "COMPLETE",
        "numeric_outputs_emitted": True, "tier": manifest.get("tier", ""),
        "donors": len(donor_to_export), "specimens": len(sample_map),
        "registry_records": len(registry), "legacy_sensitivity_status": legacy_status,
        "accuracy_endpoint_present": False,
    }
    write_json(output / "analysis_status.json", status)
    return status
