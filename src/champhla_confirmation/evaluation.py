from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from itertools import product
from pathlib import Path

from .io import canonical_pair, is_callable, read_json, read_tsv, sha256, write_json, write_tsv
from .panels import (METHOD_BASELINE, METHOD_GUARDED_CC, METHOD_PLURALITY, MODALITIES,
                     REFERENCE_ALIASES)
from .statistics import (cluster_bootstrap_ci, cluster_bootstrap_ratio_ci,
                         cluster_t_difference, exact_binomial_ci, holm_adjust,
                         subject_cluster_signflip, subject_deltas)
from .freeze import validate_freeze

# Non-inferiority margin, in percentage points of fixed-denominator accuracy.
# Introduced 2026-09-21; it is not part of the frozen pre-registration in
# configs/confirmation_protocol.json.
NONINFERIORITY_MARGIN_POINTS = 2.0
NONINFERIORITY_SEED = 20260921


def _boundary_safe(interval: tuple[float, float], successes: int,
                   trials: int) -> tuple[tuple[float, float], bool]:
    """A percentile bootstrap collapses to a point at 0% or 100% (every resample
    is 153/153), so those estimates take the exact Clopper-Pearson interval."""
    if trials and successes in (0, trials):
        return exact_binomial_ci(successes, trials), True
    return interval, False


def _stable_seed(base: int, *parts: str) -> int:
    digest = hashlib.sha256("\x1f".join(parts).encode("utf-8")).digest()
    return base + int.from_bytes(digest[:4], "big")


def prediction_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    return (row.get("cohort", ""), row["subject"], row["modality"], row["gene"], row["method"])


def truth_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return (row.get("cohort", ""), row["subject"], row["modality"], row["gene"])


def join_truth(predictions_path: str, truth_path: str, freeze_manifest_path: str,
               output_path: str, join_manifest_path: str,
               allow_prediction_superset: bool = False) -> dict:
    freeze = read_json(freeze_manifest_path)
    validation = validate_freeze(freeze_manifest_path)
    if not validation["valid"]:
        raise ValueError(f"confirmation freeze is invalid: {validation['failures']}")
    prediction_hash = sha256(predictions_path)
    frozen_prediction = freeze.get("inputs", {}).get("predictions")
    if not frozen_prediction or prediction_hash != frozen_prediction.get("sha256"):
        raise ValueError("prediction file is absent from the freeze or its checksum changed")
    predictions = read_tsv(predictions_path)
    truth_rows = read_tsv(truth_path)
    required = {"truth_allele1", "truth_allele2", "truth_status", "truth_source", "source_sha256"}
    if not truth_rows or not required.issubset(truth_rows[0]):
        raise ValueError(f"truth table missing required columns: {sorted(required - set(truth_rows[0] if truth_rows else {}))}")
    truth = {}
    for row in truth_rows:
        key = truth_key(row)
        if key in truth:
            raise ValueError(f"duplicate truth locus: {key}")
        truth[key] = row
    joined = []
    prediction_loci = {prediction_key(row)[:4] for row in predictions}
    if allow_prediction_superset:
        missing = set(truth) - prediction_loci
        if missing:
            raise ValueError(f"predictions missing {len(missing)} truth loci")
    elif prediction_loci != set(truth):
        raise ValueError(f"prediction/truth locus mismatch predictions={len(prediction_loci)} truth={len(truth)}")
    for row in predictions:
        locus = prediction_key(row)[:4]
        if locus not in truth:
            continue
        t = truth[locus]
        joined.append({**row, "truth_allele1": t["truth_allele1"],
                       "truth_allele2": t["truth_allele2"], "truth_status": t["truth_status"],
                       "truth_source": t["truth_source"], "truth_source_sha256": t["source_sha256"]})
    write_tsv(output_path, joined)
    payload = {
        "schema_version": "truth-join-2", "join_once": True, "loci": len(truth),
        "prediction_rows": len(predictions), "prediction_sha256": prediction_hash,
        "prediction_loci": len(prediction_loci),
        "prediction_superset_allowed": allow_prediction_superset,
        "truth_sha256": sha256(truth_path), "joined_sha256": sha256(output_path),
        "freeze_manifest_sha256": sha256(freeze_manifest_path),
    }
    write_json(join_manifest_path, payload)
    return payload


def _evaluate_rows(joined: list[dict[str, str]]) -> list[dict]:
    output = []
    for row in joined:
        truth = canonical_pair(row["truth_allele1"], row["truth_allele2"], row["gene"])
        callable_ = is_callable(row)
        pair = canonical_pair(row["allele1"], row["allele2"], row["gene"]) if callable_ else None
        if callable_:
            predicted_counts, truth_counts = Counter(pair), Counter(truth)
            alleles_correct = sum((predicted_counts & truth_counts).values())
        else:
            alleles_correct = 0
        output.append({**row, "is_callable": int(callable_),
                       "is_correct": int(pair == truth) if callable_ else 0,
                       "alleles_correct": alleles_correct})
    return output


def evaluate(joined_path: str, output_dir: str, bootstrap: int = 100000,
             seed: int = 20260831, allow_partial: bool = False,
             mode: str = "discovery", wgs_audit_summary: str | None = None,
             signflip_seed: int | None = None) -> dict:
    """``signflip_seed``: base seed for the subject sign-flip test. Unset, sign-flip seeds
    derive from ``seed`` as they always have; the confirmatory extension sets the locked
    protocol's separate sign-flip seed (configs/benchmark_resource_protocol_v2.json)."""
    signflip_base = seed if signflip_seed is None else signflip_seed
    evaluated = _evaluate_rows(read_tsv(joined_path))
    by_locus_method = {}
    for row in evaluated:
        key = prediction_key(row)
        if key in by_locus_method:
            raise ValueError(f"duplicate prediction method/locus row: {key}")
        by_locus_method[key] = row
    methods = {row["method"] for row in evaluated}
    required_methods = {METHOD_BASELINE, METHOD_GUARDED_CC, METHOD_PLURALITY}
    if not required_methods.issubset(methods):
        raise ValueError(f"missing required methods: {sorted(required_methods - methods)}")
    loci = sorted({key[:4] for key in by_locus_method})
    paired = []
    for locus in loci:
        rows = {method: by_locus_method.get((*locus, method)) for method in required_methods}
        if any(value is None for value in rows.values()):
            raise ValueError(f"incomplete required method set at {locus}")
        baseline, guarded, plurality = rows[METHOD_BASELINE], rows[METHOD_GUARDED_CC], rows[METHOD_PLURALITY]
        paired.append({
            "cohort": locus[0], "subject": locus[1], "modality": locus[2], "gene": locus[3],
            "superpopulation": guarded.get("superpopulation", ""),
            "truth_homozygous": int(guarded["truth_allele1"] == guarded["truth_allele2"]),
            "baseline_callable": baseline["is_callable"], "baseline_correct": baseline["is_correct"],
            "guarded_correct": guarded["is_correct"], "plurality_correct": plurality["is_correct"],
            "baseline_pair": f"{baseline['allele1']}+{baseline['allele2']}" if int(baseline["is_callable"]) else "",
            "guarded_pair": f"{guarded['allele1']}+{guarded['allele2']}",
            "plurality_pair": f"{plurality['allele1']}+{plurality['allele2']}",
            "guarded_decision_reason": guarded.get("decision_reason", ""),
        })
    present_modalities = sorted({row["modality"] for row in paired})
    if not allow_partial and set(present_modalities) != set(MODALITIES):
        raise ValueError(f"confirmation requires all modalities; present={present_modalities}")
    primary = []
    for index, modality in enumerate(MODALITIES):
        subset = [row for row in paired if row["modality"] == modality]
        if not subset:
            continue
        deltas = subject_deltas(subset, "baseline_correct", "guarded_correct")
        ci_lo, ci_hi = cluster_bootstrap_ci(subset, "baseline_correct", "guarded_correct",
                                            iterations=bootstrap, seed=seed + index)
        baseline_correct = sum(int(row["baseline_correct"]) for row in subset)
        guarded_correct = sum(int(row["guarded_correct"]) for row in subset)
        plurality_correct = sum(int(row["plurality_correct"]) for row in subset)
        p_value, signflip_method = subject_cluster_signflip(
            deltas.values(), seed=_stable_seed(seed, modality, "primary")
        )
        primary.append({
            "modality": modality, "subjects": len({row["subject"] for row in subset}), "loci": len(subset),
            "baseline_callable": sum(int(row["baseline_callable"]) for row in subset),
            "baseline_correct": baseline_correct, "guarded_correct": guarded_correct,
            "plurality_correct": plurality_correct,
            "baseline_accuracy": baseline_correct / len(subset),
            "guarded_accuracy": guarded_correct / len(subset),
            "plurality_accuracy": plurality_correct / len(subset),
            "delta_points": 100 * (guarded_correct - baseline_correct) / len(subset),
            "plurality_delta_points": 100 * (guarded_correct - plurality_correct) / len(subset),
            "wins": sum(int(row["guarded_correct"]) > int(row["baseline_correct"]) for row in subset),
            "losses": sum(int(row["guarded_correct"]) < int(row["baseline_correct"]) for row in subset),
            "ties": sum(int(row["guarded_correct"]) == int(row["baseline_correct"]) for row in subset),
            "discordant_correctness_subjects": sum(value != 0 for value in deltas.values()),
            "ci_lo_points": 100 * ci_lo, "ci_hi_points": 100 * ci_hi,
            "p_value": p_value, "signflip_method": signflip_method,
        })
    primary = holm_adjust(primary)
    def _per_gene(field: str) -> list[dict]:
        """Per-gene harm of one method against the abstaining two-thirds baseline.

        A positive delta means the method under test is ahead of the baseline in
        that gene; a significant negative delta is a harm that blocks the
        headline.
        """
        tests = []
        for modality in present_modalities:
            for gene in ("A", "B", "C"):
                subset = [row for row in paired
                          if row["modality"] == modality and row["gene"] == gene]
                if not subset:
                    continue
                deltas = subject_deltas(subset, "baseline_correct", field)
                delta = sum(deltas.values()) / len(subset)
                p_value, signflip_method = subject_cluster_signflip(
                    deltas.values(), seed=_stable_seed(seed, modality, gene, field)
                )
                tests.append({"modality": modality, "gene": gene, "loci": len(subset),
                              "method": field.replace("_correct", ""),
                              "reference": METHOD_BASELINE,
                              "delta_points": 100 * delta,
                              "p_value": p_value, "signflip_method": signflip_method})
        tests = holm_adjust(tests)
        for row in tests:
            row["significant_harm"] = int(row["delta_points"] < 0 and row["holm_significant"])
        return tests

    # The headline gate must test the primary method, not the demoted ablation.
    gene_tests = _per_gene("plurality_correct")
    guarded_gene_tests = _per_gene("guarded_correct")
    all_three = set(present_modalities) == set(MODALITIES)
    minimums = {"wgs": 120, "wes": 89, "rnaseq": 130}
    cohort_sizes = {row["modality"]: row["subjects"] for row in primary}
    sample_size_pass = all(cohort_sizes.get(modality, 0) >= minimums[modality] for modality in MODALITIES)
    wgs_audit_pass = False
    if wgs_audit_summary:
        wgs_audit_pass = bool(read_json(wgs_audit_summary).get("passed"))
    if mode not in {"discovery", "external"}:
        raise ValueError(f"unsupported evaluation mode: {mode}")
    if mode == "external" and not wgs_audit_summary:
        raise ValueError("external evaluation requires --wgs-audit-summary")
    # Ablation record: TwoThirdsGuardedCC against the abstaining two-thirds rule.
    # This is no longer the headline gate, only a retained ablation measurement.
    guarded_ablation_pass = bool(all_three and all(
        row["delta_points"] > 0 and row["ci_lo_points"] > 0 and row["holm_significant"] for row in primary))
    plurality_retention = all(row["plurality_delta_points"] >= -2.0 for row in primary)
    no_gene_harm = not any(row["significant_harm"] for row in gene_tests)

    # Every paired comparison is anchored on the always-call consensus rule
    # (ChampHLA-Consensus / SimplePluralityLex), which is the primary method.
    # TwoThirdsGuardedCC is one comparator among the rest, not the reference.
    secondary_methods = sorted(methods - REFERENCE_ALIASES)
    secondary_tests = []
    for modality in present_modalities:
        modality_loci = [locus for locus in loci if locus[2] == modality]
        consensus_map = {locus: int(by_locus_method[(*locus, METHOD_PLURALITY)]["is_correct"])
                         for locus in modality_loci}
        for method in secondary_methods:
            if not any((*locus, method) in by_locus_method for locus in modality_loci):
                continue
            subject_delta = defaultdict(int)
            subject_locus_deltas = defaultdict(list)
            covered = sum(1 for locus in modality_loci if (*locus, method) in by_locus_method)
            method_correct = consensus_correct = wins = losses = 0
            for locus in modality_loci:
                candidate = by_locus_method.get((*locus, method))
                candidate_correct = int(candidate["is_correct"]) if candidate else 0
                selected_correct = consensus_map[locus]
                method_correct += candidate_correct
                consensus_correct += selected_correct
                wins += int(selected_correct > candidate_correct)
                losses += int(selected_correct < candidate_correct)
                subject_delta[locus[1]] += selected_correct - candidate_correct
                subject_locus_deltas[locus[1]].append(selected_correct - candidate_correct)
            discordant_subjects = sum(value != 0 for value in subject_delta.values())
            signflip_seed = _stable_seed(signflip_base, modality, method)
            p_value, signflip_method = subject_cluster_signflip(
                subject_delta.values(), seed=signflip_seed
            )
            method_row = next(
                (by_locus_method[(*locus, method)] for locus in modality_loci
                 if (*locus, method) in by_locus_method),
                None,
            )
            inference_family = (method_row or {}).get("analysis_scope", "")
            if not inference_family:
                inference_family = (
                    "descriptive_comparator"
                    if method.startswith("Caller:")
                    or method in {METHOD_BASELINE, "SimpleStrictMajority"}
                    else "exploratory_fitted"
                )
            if inference_family not in {"descriptive_comparator", "exploratory_fitted"}:
                raise ValueError(
                    f"paired comparator {method!r} has invalid analysis scope "
                    f"{inference_family!r}"
                )
            secondary_tests.append({
                "_subject_locus_deltas": dict(subject_locus_deltas),
                "modality": modality, "comparator": method, "loci": len(modality_loci),
                "inference_family": inference_family,
                "comparator_coverage": covered,
                "comparator_absent_loci": len(modality_loci) - covered,
                "consensus_correct": consensus_correct, "comparator_correct": method_correct,
                "delta_points": 100 * (consensus_correct - method_correct) / len(modality_loci),
                "wins": wins, "losses": losses,
                "signflip_p_value": p_value, "signflip_method": signflip_method,
                "signflip_assignments": (
                    2 ** discordant_subjects if discordant_subjects <= 25 else 1_000_000
                ),
                "signflip_seed": signflip_seed,
                "discordant_subjects": discordant_subjects,
            })
    # Inference is separated by assay and declared descriptive/fitted scope.
    # Zero-discordance comparisons remain visible but consume no multiplicity slot.
    inferred_tests = []
    for modality in present_modalities:
        for family in ("descriptive_comparator", "exploratory_fitted"):
            members = [row for row in secondary_tests
                       if row["modality"] == modality and row["inference_family"] == family]
            active = [row for row in members if row["wins"] or row["losses"]]
            family_size = len(active)
            for row in members:
                if row not in active:
                    row.update({
                        "p_value": 1.0,
                        "pointwise_ci_lo_points": 0.0,
                        "pointwise_ci_hi_points": 0.0,
                        "simultaneous_ci_lo_points": 0.0,
                        "simultaneous_ci_hi_points": 0.0,
                        "standard_error_points": 0.0,
                        "degrees_freedom": len(row["_subject_locus_deltas"]) - 1,
                        "clusters": len(row["_subject_locus_deltas"]),
                        "family_size": family_size,
                        "multiplicity_included": 0,
                        "inference_method": "locus_weighted_cr1_cluster_t",
                    })
                    continue
                inference = cluster_t_difference(
                    row["_subject_locus_deltas"], family_size=family_size
                )
                row.update({
                    "p_value": inference["p_value"],
                    "pointwise_ci_lo_points": 100 * inference["pointwise_ci_lo"],
                    "pointwise_ci_hi_points": 100 * inference["pointwise_ci_hi"],
                    "simultaneous_ci_lo_points": 100 * inference["adjusted_ci_lo"],
                    "simultaneous_ci_hi_points": 100 * inference["adjusted_ci_hi"],
                    "standard_error_points": 100 * inference["standard_error"],
                    "degrees_freedom": inference["degrees_freedom"],
                    "clusters": inference["clusters"],
                    "family_size": family_size,
                    "multiplicity_included": 1,
                    "inference_method": inference["inference_method"],
                })
            adjusted = {row["comparator"]: row for row in holm_adjust(active)}
            signflip_adjusted = {
                row["comparator"]: row
                for row in holm_adjust(active, p_field="signflip_p_value")
            }
            for row in members:
                primary_result = adjusted.get(row["comparator"])
                sensitivity_result = signflip_adjusted.get(row["comparator"])
                row["holm_adjusted_p"] = (
                    primary_result["holm_adjusted_p"] if primary_result else 1.0
                )
                row["holm_significant"] = (
                    primary_result["holm_significant"] if primary_result else 0
                )
                row["signflip_holm_adjusted_p"] = (
                    sensitivity_result["holm_adjusted_p"] if sensitivity_result else 1.0
                )
                row["signflip_holm_significant"] = (
                    sensitivity_result["holm_significant"] if sensitivity_result else 0
                )
                inferred_tests.append(row)
    secondary_tests = inferred_tests

    secondary_endpoints = []
    for modality in present_modalities:
        subset = [row for row in paired if row["modality"] == modality]
        called = [row for row in subset if int(row["baseline_callable"])]
        caller_methods = [method for method in methods if method.startswith("Caller:")]
        oracle = 0
        for row in subset:
            locus = (row["cohort"], row["subject"], row["modality"], row["gene"])
            oracle += int(any(by_locus_method.get((*locus, method), {}).get("is_correct") == 1
                              for method in caller_methods))
        secondary_endpoints.append({
            "modality": modality, "loci": len(subset), "baseline_callable": len(called),
            "baseline_callability": len(called) / len(subset),
            "baseline_called_only_accuracy": (sum(int(row["baseline_correct"]) for row in called) / len(called)
                                                if called else 0.0),
            "guarded_accuracy_at_baseline_coverage": (sum(int(row["guarded_correct"]) for row in called) / len(called)
                                                       if called else 0.0),
            "candidate_oracle_correct": oracle, "candidate_oracle_accuracy": oracle / len(subset),
            "protected_loci": sum(row["guarded_decision_reason"] == "protected_two_thirds_consensus"
                                  for row in subset),
            "challenged_loci": sum(row["guarded_decision_reason"] == "champion_challenger_resolved_disagreement"
                                   for row in subset),
        })

    method_performance = []
    for modality in present_modalities:
        modality_loci = [locus for locus in loci if locus[2] == modality]
        modality_methods = sorted({key[4] for key in by_locus_method if key[2] == modality})
        for method in modality_methods:
            candidates = [by_locus_method.get((*locus, method)) for locus in modality_loci]
            correct = sum(int(row["is_correct"]) for row in candidates if row)
            callable_count = sum(int(row["is_callable"]) for row in candidates if row)
            allele_correct = sum(int(row["alleles_correct"]) for row in candidates if row)
            genotype_by_subject = defaultdict(list)
            allele_by_subject = defaultdict(list)
            callability_by_subject = defaultdict(list)
            called_only_by_subject = defaultdict(list)
            for locus, row in zip(modality_loci, candidates):
                correct_value = int(row["is_correct"]) if row else 0
                callable_value = int(row["is_callable"]) if row else 0
                allele_value = int(row["alleles_correct"]) if row else 0
                genotype_by_subject[locus[1]].append((correct_value, 1))
                allele_by_subject[locus[1]].append((allele_value, 2))
                callability_by_subject[locus[1]].append((callable_value, 1))
                called_only_by_subject[locus[1]].append((correct_value, callable_value))
            method_seed = _stable_seed(seed, modality, method)
            ci_lo, ci_hi = cluster_bootstrap_ratio_ci(
                genotype_by_subject, bootstrap, method_seed)
            allele_lo, allele_hi = cluster_bootstrap_ratio_ci(
                allele_by_subject, bootstrap, method_seed + 1)
            callability_lo, callability_hi = cluster_bootstrap_ratio_ci(
                callability_by_subject, bootstrap, method_seed + 2)
            called_only_lo, called_only_hi = cluster_bootstrap_ratio_ci(
                called_only_by_subject, bootstrap, method_seed + 3)
            intervals = {
                "genotype": ((ci_lo, ci_hi), correct, len(modality_loci)),
                "allele": ((allele_lo, allele_hi), allele_correct, 2 * len(modality_loci)),
                "callability": ((callability_lo, callability_hi), callable_count,
                                len(modality_loci)),
                "called_only": ((called_only_lo, called_only_hi), correct, callable_count),
            }
            boundary = []
            for name, (interval, successes, trials) in intervals.items():
                interval, switched = _boundary_safe(interval, successes, trials)
                intervals[name] = (interval, successes, trials)
                if switched:
                    boundary.append(name)
            (ci_lo, ci_hi), (allele_lo, allele_hi), (callability_lo, callability_hi), (
                called_only_lo, called_only_hi) = (intervals[name][0] for name in intervals)
            # When every locus is callable, fixed-denominator and called-only
            # outcomes are the same vector. Reuse the same interval exactly;
            # separate Monte Carlo draws must not create conflicting bounds.
            if callable_count == len(modality_loci):
                called_only_lo, called_only_hi = ci_lo, ci_hi
            called_only_accuracy = correct / callable_count if callable_count else 0.0
            scope = next((row.get("analysis_scope", "") for row in candidates if row), "")
            method_performance.append({
                "modality": modality, "method": method, "analysis_scope": scope,
                "subjects": len({locus[1] for locus in modality_loci}),
                "loci": len(modality_loci), "rows_present": sum(row is not None for row in candidates),
                "callable": callable_count, "callability": callable_count / len(modality_loci),
                "callability_ci_lo": callability_lo, "callability_ci_hi": callability_hi,
                "genotypes_correct": correct, "genotype_accuracy": correct / len(modality_loci),
                "genotype_ci_lo": ci_lo, "genotype_ci_hi": ci_hi,
                "called_only_accuracy": called_only_accuracy,
                "called_only_ci_lo": called_only_lo, "called_only_ci_hi": called_only_hi,
                "alleles_correct": allele_correct, "alleles_total": 2 * len(modality_loci),
                "allele_accuracy": allele_correct / (2 * len(modality_loci)),
                "allele_ci_lo": allele_lo, "allele_ci_hi": allele_hi,
                "interval_method": "subject_cluster_percentile_bootstrap",
                "boundary_intervals": ",".join(boundary),
                "bootstrap_iterations": bootstrap, "bootstrap_seed": method_seed,
            })

    stratum_rows = []
    for field in ("gene", "superpopulation", "truth_homozygous"):
        values = sorted({str(row[field]) for row in paired})
        for value in values:
            subset = [row for row in paired if str(row[field]) == value]
            if not subset:
                continue
            stratum_rows.append({
                "stratum_type": field, "stratum": value, "loci": len(subset),
                "baseline_correct": sum(int(row["baseline_correct"]) for row in subset),
                "guarded_correct": sum(int(row["guarded_correct"]) for row in subset),
                "delta_points": 100 * sum(int(row["guarded_correct"]) - int(row["baseline_correct"])
                                          for row in subset) / len(subset),
            })
    external_prerequisites = mode == "external" and wgs_audit_pass and sample_size_pass
    # A criterion phrased as "no comparator significantly exceeds consensus" passes
    # automatically wherever the comparison is underpowered, and most of the
    # integration comparisons here are underpowered by construction: the exact test
    # cannot return p < 0.05 when only a handful of subjects differ. Retained for
    # continuity, but it no longer decides anything. Significance is the exact
    # subject sign-flip test's (decisions/20261009_signflip_governs.json); the CR1
    # cluster-t is a descriptive interval estimate.
    consensus_losses = [row for row in secondary_tests
                        if row["delta_points"] < 0 and row["signflip_holm_significant"]]
    consensus_not_exceeded = not consensus_losses
    # The two-point non-inferiority margin is retained only as a post hoc
    # sensitivity and uses the same family-adjusted cluster-t interval.
    for row in secondary_tests:
        row.pop("_subject_locus_deltas")
        row["noninferior_2pp"] = int(
            row["simultaneous_ci_lo_points"] > -NONINFERIORITY_MARGIN_POINTS
        )
    noninferiority_failures = [row for row in secondary_tests if not row["noninferior_2pp"]]
    consensus_noninferior = not noninferiority_failures
    primary_pass = False
    headline = bool(external_prerequisites and consensus_noninferior and no_gene_harm)
    final = {
        "schema_version": "three-modality-confirmation-evaluation-2",
        "mode": mode,
        "primary_method": METHOD_PLURALITY,
        "status": "consensus_headline_confirmed" if headline else
                  "discovery_only" if mode == "discovery" else "confirmation_not_achieved",
        "primary_pass": primary_pass,
        "primary_pass_definition": "No confirmatory pass/fail claim is made for this retrospective development analysis.",
        "development_analysis_complete": True,
        "consensus_not_exceeded_pass": consensus_not_exceeded,
        "consensus_not_exceeded_is_advisory": "absence of a significant exceedance "
                                              "passes automatically under low power and "
                                              "does not decide the headline",
        "consensus_noninferior_2pp_pass": consensus_noninferior,
        "noninferiority_status": "post_hoc_exploratory_sensitivity_only",
        "noninferiority_margin_points": NONINFERIORITY_MARGIN_POINTS,
        "comparators_failing_noninferiority": [
            {"modality": row["modality"], "comparator": row["comparator"],
             "delta_points": row["delta_points"],
             "simultaneous_ci_lo_points": row["simultaneous_ci_lo_points"]}
            for row in noninferiority_failures
        ],
        "comparators_significantly_exceeding_consensus": [
            {"modality": row["modality"], "comparator": row["comparator"],
             "delta_points": row["delta_points"],
             "signflip_holm_adjusted_p": row["signflip_holm_adjusted_p"]}
            for row in consensus_losses
        ],
        "governing_paired_test": "exact_subject_signflip_holm",
        "descriptive_paired_inference": "locus_weighted_cr1_cluster_t",
        "guarded_cc_ablation_pass": guarded_ablation_pass,
        "guarded_cc_per_gene_harm": [
            {"modality": row["modality"], "gene": row["gene"], "delta_points": row["delta_points"]}
            for row in guarded_gene_tests if row["significant_harm"]
        ],
        "plurality_retention_pass": plurality_retention,
        "per_gene_harm_pass": no_gene_harm,
        "modalities_evaluated": list(present_modalities),
        "all_modalities_present": all_three,
        "absent_comparator_scoring": "a comparator with no row at a locus is scored "
                                     "incorrect there; comparator_coverage reports how "
                                     "often this occurs",
        "wgs_audit_pass": wgs_audit_pass, "sample_size_pass": sample_size_pass,
        "cohort_subjects": cohort_sizes, "minimum_subjects": minimums,
        "external_prerequisites_pass": external_prerequisites,
        "headline_retained": headline,
        "claim_boundary": "retrospective development performance of equal-weight consensus "
                          "relative only to the named evaluated callers and fitted policies; "
                          "no equivalence, state-of-the-art, or external-validity claim",
        "input_sha256": sha256(joined_path),
    }
    out = Path(output_dir)
    write_tsv(out / "paired_locus_audit.tsv", paired)
    write_tsv(out / "primary_modality_results.tsv", primary)
    write_tsv(out / "per_gene_results.tsv", gene_tests)
    write_tsv(out / "per_gene_guarded_ablation.tsv", guarded_gene_tests)
    write_tsv(out / "secondary_method_results.tsv", secondary_tests)
    write_tsv(out / "secondary_endpoints.tsv", secondary_endpoints)
    write_tsv(out / "method_performance.tsv", method_performance)
    write_tsv(out / "stratified_results.tsv", stratum_rows)
    write_json(out / "confirmation_decision.json", final)
    return final


def capacity(predictions_path: str, output_json: str) -> dict:
    rows = read_tsv(predictions_path)
    by_key = {(row.get("cohort", ""), row["subject"], row["modality"], row["gene"], row["method"]): row
              for row in rows}
    loci = sorted({key[:4] for key in by_key})
    counts = defaultdict(set)
    for locus in loci:
        baseline = by_key.get((*locus, METHOD_BASELINE))
        guarded = by_key.get((*locus, METHOD_GUARDED_CC))
        if not baseline or not guarded:
            continue
        baseline_pair = (baseline.get("allele1", ""), baseline.get("allele2", ""), baseline.get("call_status", ""))
        guarded_pair = (guarded.get("allele1", ""), guarded.get("allele2", ""), guarded.get("call_status", ""))
        if baseline_pair != guarded_pair:
            counts[locus[2]].add(locus[1])
    values = {modality: len(counts[modality]) for modality in MODALITIES}
    result = {
        "schema_version": "truth-blind-capacity-gate-1", "discordant_subjects": values,
        "minimum_six_each": all(values[m] >= 6 for m in MODALITIES),
        "minimum_seven_in_two": sum(values[m] >= 7 for m in MODALITIES) >= 2,
    }
    result["passed"] = result["minimum_six_each"] and result["minimum_seven_in_two"]
    write_json(output_json, result)
    return result


def evaluate_ambiguity_compatibility(predictions_path: str, candidate_truth_path: str,
                                     freeze_manifest_path: str, output_path: str,
                                     bootstrap: int = 100000,
                                     seed: int = 20260925) -> list[dict]:
    """Secondary set-valued scoring after validation of the truth-free freeze."""
    freeze = read_json(freeze_manifest_path)
    # Predictions, not the later analysis code, are the truth-firewall object.
    # Verify every frozen input and the manifest content hash. The historical
    # project-file inventory may live in another immutable checkout.
    validation = validate_freeze(freeze_manifest_path, verify_project_files=False)
    if not validation["valid"]:
        raise ValueError(f"prediction freeze is invalid: {validation['failures']}")
    prediction_hash = sha256(predictions_path)
    frozen_prediction = freeze.get("inputs", {}).get("predictions", {})
    if frozen_prediction.get("sha256") != prediction_hash:
        raise ValueError("prediction file does not match the truth-free freeze")
    predictions = read_tsv(predictions_path)
    truth_rows = read_tsv(candidate_truth_path)
    truth = {}
    for row in truth_rows:
        key = (row["subject"], row["modality"], row["gene"])
        candidates = {tuple(pair) for pair in json.loads(row["truth_candidate_pairs_json"])}
        if candidates:
            truth[key] = (candidates, row["truth_status"])
    methods = sorted({row["method"] for row in predictions})
    pred = {(row["subject"], row["modality"], row["gene"], row["method"]): row
            for row in predictions}
    loci = sorted({key[:3] for key in pred if key[:3] in truth})
    output = []
    for modality in sorted({locus[1] for locus in loci}):
        modality_loci = [locus for locus in loci if locus[1] == modality]
        for method in methods:
            if not any((*locus, method) in pred for locus in modality_loci):
                continue
            by_subject = defaultdict(list)
            correct = callable_count = resolved = ambiguous = 0
            for locus in modality_loci:
                row = pred.get((*locus, method))
                callable_ = bool(row and is_callable(row))
                pair = canonical_pair(row["allele1"], row["allele2"], locus[2]) if callable_ else None
                compatible = int(pair in truth[locus][0]) if pair else 0
                by_subject[locus[0]].append((compatible, 1))
                correct += compatible
                callable_count += int(callable_)
                resolved += truth[locus][1] == "resolved"
                ambiguous += truth[locus][1] == "ambiguous"
            ci_lo, ci_hi = cluster_bootstrap_ratio_ci(
                by_subject, bootstrap, _stable_seed(seed, modality, method, "compatible"))
            output.append({
                "modality": modality, "method": method,
                "subjects": len(by_subject), "loci": len(modality_loci),
                "resolved_truth_loci": resolved, "ambiguous_truth_loci": ambiguous,
                "callable": callable_count, "compatible": correct,
                "compatibility_concordance": correct / len(modality_loci),
                "ci_lo": ci_lo, "ci_hi": ci_hi,
                "interval_method": "subject_cluster_percentile_bootstrap",
                "prediction_sha256": prediction_hash,
                "candidate_truth_sha256": sha256(candidate_truth_path),
            })
    paired = []
    for modality in sorted({locus[1] for locus in loci}):
        modality_loci = [locus for locus in loci if locus[1] == modality]
        if not all((*locus, METHOD_PLURALITY) in pred for locus in modality_loci):
            raise ValueError(f"{modality}: plurality prediction missing from set-valued locus")
        consensus_score = {}
        for locus in modality_loci:
            row = pred[(*locus, METHOD_PLURALITY)]
            pair = (canonical_pair(row["allele1"], row["allele2"], locus[2])
                    if is_callable(row) else None)
            consensus_score[locus] = int(pair in truth[locus][0]) if pair else 0
        for method in sorted(set(methods) - set(REFERENCE_ALIASES)):
            if not any((*locus, method) in pred for locus in modality_loci):
                continue
            subject_delta = defaultdict(int)
            wins = losses = comparator_compatible = consensus_compatible = covered = 0
            for locus in modality_loci:
                candidate = pred.get((*locus, method))
                covered += int(candidate is not None)
                pair = (canonical_pair(candidate["allele1"], candidate["allele2"], locus[2])
                        if candidate and is_callable(candidate) else None)
                candidate_compatible = int(pair in truth[locus][0]) if pair else 0
                selected_compatible = consensus_score[locus]
                comparator_compatible += candidate_compatible
                consensus_compatible += selected_compatible
                wins += int(selected_compatible > candidate_compatible)
                losses += int(selected_compatible < candidate_compatible)
                subject_delta[locus[0]] += selected_compatible - candidate_compatible
            discordant_subjects = sum(value != 0 for value in subject_delta.values())
            signflip_seed = _stable_seed(seed, "ambiguity-compatible", modality, method)
            p_value, signflip_method = subject_cluster_signflip(
                subject_delta.values(), seed=signflip_seed
            )
            method_row = next(
                (pred[(*locus, method)] for locus in modality_loci
                 if (*locus, method) in pred),
                None,
            )
            inference_family = (method_row or {}).get("analysis_scope", "")
            if not inference_family:
                inference_family = (
                    "descriptive_comparator"
                    if method.startswith("Caller:")
                    or method in {METHOD_BASELINE, "SimpleStrictMajority"}
                    else "exploratory_fitted"
                )
            if inference_family not in {"descriptive_comparator", "exploratory_fitted"}:
                raise ValueError(
                    f"set-valued comparator {method!r} has invalid analysis scope "
                    f"{inference_family!r}"
                )
            paired.append({
                "modality": modality,
                "comparator": method,
                "endpoint": "set_valued_two_field_compatibility",
                "loci": len(modality_loci),
                "clusters": len(subject_delta),
                "inference_family": inference_family,
                "comparator_coverage": covered,
                "comparator_absent_loci": len(modality_loci) - covered,
                "consensus_compatible": consensus_compatible,
                "comparator_compatible": comparator_compatible,
                "delta_points": (
                    100 * (consensus_compatible - comparator_compatible)
                    / len(modality_loci)
                ),
                "wins": wins,
                "losses": losses,
                "signflip_p_value": p_value,
                "signflip_method": signflip_method,
                "signflip_assignments": (
                    2 ** discordant_subjects if discordant_subjects <= 25 else 1_000_000
                ),
                "signflip_seed": signflip_seed,
                "discordant_subjects": discordant_subjects,
            })
    paired_output = []
    for modality in sorted({row["modality"] for row in paired}):
        for family in ("descriptive_comparator", "exploratory_fitted"):
            members = [
                row for row in paired
                if row["modality"] == modality and row["inference_family"] == family
            ]
            active = [row for row in members if row["wins"] or row["losses"]]
            adjusted = {
                row["comparator"]: row
                for row in holm_adjust(active, p_field="signflip_p_value")
            }
            for row in members:
                result = adjusted.get(row["comparator"])
                row["family_size"] = len(active)
                row["multiplicity_included"] = int(row in active)
                row["signflip_holm_adjusted_p"] = (
                    result["holm_adjusted_p"] if result else 1.0
                )
                row["signflip_holm_significant"] = (
                    result["holm_significant"] if result else 0
                )
                paired_output.append(row)
    write_tsv(output_path, output)
    paired_path = Path(output_path).with_name("ambiguity_paired_results.tsv")
    write_tsv(paired_path, paired_output)
    return output


# The 2014 reference table labels the CEU HapMap samples "CEPH".
SELECTION_POPULATIONS = ("CEPH", "YRI")


def evaluate_truth_selection(predictions_path: str, candidate_truth_path: str,
                             freeze_manifest_path: str, output_path: str, profile_path: str,
                             bootstrap: int = 100000, seed: int = 20260925) -> list[dict]:
    """Compatibility on loci the exact audit retained against loci it excluded.

    The exact endpoint keeps only uniquely resolved reference typings. Scoring the
    same set-valued compatibility separately on resolved (retained) and ambiguous
    (excluded but scorable) loci shows whether method rankings depend on that
    selection; the truth-free profile shows how the two strata differ in population
    and in caller agreement, without reading any truth label.
    """
    validation = validate_freeze(freeze_manifest_path)
    if not validation["valid"]:
        raise ValueError(f"prediction freeze is invalid: {validation['failures']}")
    prediction_hash = sha256(predictions_path)
    freeze = read_json(freeze_manifest_path)
    if freeze.get("inputs", {}).get("predictions", {}).get("sha256") != prediction_hash:
        raise ValueError("prediction file does not match the truth-free freeze")
    predictions = read_tsv(predictions_path)
    truth = {}
    population = {}
    pair_counts = {}
    for row in read_tsv(candidate_truth_path):
        candidates = {tuple(pair) for pair in json.loads(row["truth_candidate_pairs_json"])}
        if candidates and row["truth_status"] in {"resolved", "ambiguous"}:
            key = (row["subject"], row["modality"], row["gene"])
            truth[key] = (candidates, row["truth_status"])
            population[key] = row["population"]
            pair_counts[key] = len(candidates)
    pred = {(row["subject"], row["modality"], row["gene"], row["method"]): row
            for row in predictions}
    methods = sorted({row["method"] for row in predictions})
    loci = sorted({key[:3] for key in pred if key[:3] in truth})
    output, profile = [], []
    for modality in sorted({locus[1] for locus in loci}):
        callers = sorted(m for m in methods if m.startswith("Caller:")
                         and any((*locus, m) in pred for locus in loci if locus[1] == modality))
        for stratum in ("resolved", "ambiguous"):
            stratum_loci = [l for l in loci if l[1] == modality and truth[l][1] == stratum]
            for method in methods:
                if not any((*locus, method) in pred for locus in stratum_loci):
                    continue
                by_subject = defaultdict(list)
                compatible_total = 0
                for locus in stratum_loci:
                    row = pred.get((*locus, method))
                    pair = (canonical_pair(row["allele1"], row["allele2"], locus[2])
                            if row and is_callable(row) else None)
                    compatible = int(pair in truth[locus][0]) if pair else 0
                    by_subject[locus[0]].append((compatible, 1))
                    compatible_total += compatible
                ci_lo, ci_hi = cluster_bootstrap_ratio_ci(
                    by_subject, bootstrap, _stable_seed(seed, modality, method, stratum))
                output.append({
                    "modality": modality, "stratum": stratum, "method": method,
                    "subjects": len(by_subject), "loci": len(stratum_loci),
                    "compatible": compatible_total,
                    "compatibility_concordance": compatible_total / len(stratum_loci),
                    "ci_lo": ci_lo, "ci_hi": ci_hi,
                    "interval_method": "subject_cluster_percentile_bootstrap",
                    "prediction_sha256": prediction_hash,
                    "candidate_truth_sha256": sha256(candidate_truth_path),
                })
            # Truth-free difficulty: how often at least two panel callers made a call
            # and every callable caller made the same one.
            unanimous = 0
            for locus in stratum_loci:
                callable_rows = [row for row in (pred.get((*locus, c)) for c in callers)
                                 if row and is_callable(row)]
                calls = {canonical_pair(row["allele1"], row["allele2"], locus[2])
                         for row in callable_rows}
                unanimous += int(len(callable_rows) >= 2 and len(calls) == 1)
            pairs = sorted(pair_counts[l] for l in stratum_loci)
            middle = len(pairs) // 2
            selected = sum(population[l] in SELECTION_POPULATIONS for l in stratum_loci)
            profile.append({
                "modality": modality, "stratum": stratum, "loci": len(stratum_loci),
                "subjects": len({l[0] for l in stratum_loci}),
                "ceu_ceph_or_yri_loci": selected,
                "ceu_ceph_or_yri_share": selected / len(stratum_loci),
                "caller_unanimous_loci": unanimous,
                "caller_unanimous_share": unanimous / len(stratum_loci),
                "median_candidate_pairs": (pairs[middle] if len(pairs) % 2
                                           else (pairs[middle - 1] + pairs[middle]) / 2),
                "unanimity_definition": "at least two panel callers callable and all agree",
            })
    write_tsv(output_path, output)
    write_tsv(profile_path, profile)
    return output


PER_LOCUS_FIELDS = ["subject", "superpopulation", "modality", "gene", "method",
                    "analysis_scope", "call_status", "allele1", "allele2",
                    "truth_allele1", "truth_allele2", "correct"]


def write_per_locus_results(joined_path: str, output_path: str) -> int:
    """Release the per-locus results (PSR-037): every method's call at every
    exact-endpoint locus, the public 2014 reference genotype and whether they agree.
    Both inputs are public; nothing beyond them is written."""
    rows = []
    for row in read_tsv(joined_path):
        if not (row.get("truth_allele1") or "").strip():
            continue
        called = canonical_pair(row["allele1"], row["allele2"], row["gene"]) if is_callable(row) else None
        truth = canonical_pair(row["truth_allele1"], row["truth_allele2"], row["gene"])
        rows.append({**{field: row.get(field, "") for field in PER_LOCUS_FIELDS[:-1]},
                     "correct": int(called is not None and called == truth)})
    rows.sort(key=lambda r: (r["modality"], r["subject"], r["gene"], r["method"]))
    write_tsv(output_path, rows, PER_LOCUS_FIELDS)
    return len(rows)


def _evaluate_group_compatibility(
    predictions_path: str,
    candidate_truth_path: str,
    freeze_manifest_path: str,
    output_path: str,
    reference,
    group_kind: str,
    bootstrap: int = 100000,
    seed: int = 20260925,
) -> list[dict]:
    """Score official P/G compatibility after mapping each two-field designation.

    A two-field designation can map to several official groups. The endpoint is
    therefore compatibility under a two-field mapping, not an inferred exact
    group call. Loci whose truth has no compatible official group are excluded.
    """
    normalized_kind = group_kind.upper()
    if normalized_kind not in {"P", "G"}:
        raise ValueError(f"unsupported HLA group kind: {group_kind}")
    validation = validate_freeze(freeze_manifest_path, verify_project_files=False)
    if not validation["valid"]:
        raise ValueError(f"prediction freeze is invalid: {validation['failures']}")
    prediction_hash = sha256(predictions_path)
    freeze = read_json(freeze_manifest_path)
    if freeze.get("inputs", {}).get("predictions", {}).get("sha256") != prediction_hash:
        raise ValueError("prediction file does not match the truth-free freeze")
    predictions = read_tsv(predictions_path)
    truth_rows = read_tsv(candidate_truth_path)

    from .hla_reference import _two_field
    source_groups = reference.p_groups if normalized_kind == "P" else reference.g_groups
    groups_by_two_field = defaultdict(set)
    for group, members in source_groups.items():
        for member in members:
            two_field = _two_field(member)
            if two_field:
                groups_by_two_field[two_field].add(group)

    def group_pairs(pair):
        left = groups_by_two_field.get(_two_field(pair[0]), set())
        right = groups_by_two_field.get(_two_field(pair[1]), set())
        return {tuple(sorted(item)) for item in product(left, right)}

    truth = {}
    unresolved_truth = set()
    for row in truth_rows:
        key = (row["subject"], row["modality"], row["gene"])
        candidates = {tuple(pair) for pair in json.loads(row["truth_candidate_pairs_json"])}
        groups = set().union(*(group_pairs(pair) for pair in candidates)) if candidates else set()
        if groups:
            truth[key] = (groups, row["truth_status"])
        elif candidates:
            unresolved_truth.add(key)
    pred = {
        (row["subject"], row["modality"], row["gene"], row["method"]): row
        for row in predictions
    }
    methods = sorted({row["method"] for row in predictions})
    loci = sorted(key for key in truth if any((*key, method) in pred for method in methods))
    output = []
    field_suffix = normalized_kind.lower() + "_group"
    for modality in sorted({key[1] for key in loci}):
        modality_loci = [key for key in loci if key[1] == modality]
        for method in methods:
            if not any((*key, method) in pred for key in modality_loci):
                continue
            by_subject = defaultdict(list)
            compatible = callable_count = unresolved_predictions = 0
            for locus in modality_loci:
                row = pred.get((*locus, method))
                predicted_groups = set()
                if row and is_callable(row):
                    callable_count += 1
                    pair = canonical_pair(row["allele1"], row["allele2"], locus[2])
                    predicted_groups = group_pairs(pair)
                    unresolved_predictions += int(not predicted_groups)
                matched = int(bool(predicted_groups & truth[locus][0]))
                by_subject[locus[0]].append((matched, 1))
                compatible += matched
            ci_lo, ci_hi = cluster_bootstrap_ratio_ci(
                by_subject,
                bootstrap,
                _stable_seed(seed, modality, method, field_suffix),
            )
            output.append({
                "modality": modality,
                "method": method,
                "subjects": len(by_subject),
                "loci": len(modality_loci),
                f"truth_loci_unresolved_for_{field_suffix}": sum(
                    key[1] == modality for key in unresolved_truth
                ),
                "callable": callable_count,
                f"prediction_loci_unresolved_for_{field_suffix}": unresolved_predictions,
                "compatible": compatible,
                "compatibility_concordance": compatible / len(modality_loci),
                "ci_lo": ci_lo,
                "ci_hi": ci_hi,
                "group_kind": normalized_kind,
                "designation_interpretation": (
                    f"{normalized_kind}_compatible_under_two_field_mapping"
                ),
                "normalization_release": reference.release,
                "prediction_sha256": prediction_hash,
                "candidate_truth_sha256": sha256(candidate_truth_path),
            })
    write_tsv(output_path, output)
    return output


def evaluate_g_group_compatibility(
    predictions_path: str,
    candidate_truth_path: str,
    freeze_manifest_path: str,
    output_path: str,
    reference,
    bootstrap: int = 100000,
    seed: int = 20260925,
) -> list[dict]:
    return _evaluate_group_compatibility(
        predictions_path, candidate_truth_path, freeze_manifest_path, output_path,
        reference, "G", bootstrap, seed,
    )


def evaluate_p_group_compatibility(
    predictions_path: str,
    candidate_truth_path: str,
    freeze_manifest_path: str,
    output_path: str,
    reference,
    bootstrap: int = 100000,
    seed: int = 20260925,
) -> list[dict]:
    return _evaluate_group_compatibility(
        predictions_path, candidate_truth_path, freeze_manifest_path, output_path,
        reference, "P", bootstrap, seed,
    )
