from __future__ import annotations

import math
import json
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from .io import canonical_pair, is_callable, read_json, read_tsv, sha256, write_json, write_tsv
from .panels import METHOD_PLURALITY, PANELS
from .statistics import exact_binomial_ci


def _locus(row: dict[str, str]) -> tuple[str, str, str, str]:
    return row.get("cohort", ""), row["subject"], row["modality"], row["gene"]


def _result(successes: int, trials: int) -> dict[str, float | int]:
    lo, hi = exact_binomial_ci(successes, trials)
    return {"loci": trials, "correct": successes, "accuracy": successes / trials,
            "ci_lo": lo, "ci_hi": hi}


#: Subject-cluster bootstrap for caller-error phi (PSR-027).
PHI_BOOTSTRAP = 100000
PHI_SEED = 20260925


def _phi_bootstrap_ci(cells_by_subject: list[tuple[int, int, int, int]],
                      iterations: int = PHI_BOOTSTRAP,
                      seed: int = PHI_SEED) -> tuple[float, float]:
    """Percentile interval for phi, resampling subjects with their 2x2 cells."""
    import numpy as np

    cells = np.asarray(cells_by_subject, dtype=np.int64)
    rng = np.random.default_rng(seed)
    sums = cells[rng.integers(0, len(cells), size=(iterations, len(cells)))].sum(axis=1)
    n00, n01, n10, n11 = sums.T.astype(float)
    denominator = np.sqrt((n10 + n11) * (n00 + n01) * (n01 + n11) * (n00 + n10))
    phi = np.divide(n11 * n00 - n10 * n01, denominator,
                    out=np.zeros_like(denominator), where=denominator > 0)
    low, high = np.percentile(phi, [2.5, 97.5])
    return float(low), float(high)


def characterise_development(joined_path: str, truth_manifest_path: str,
                             output_dir: str,
                             candidate_truth_path: str | None = None,
                             reference=None) -> dict:
    rows = read_tsv(joined_path)
    truth_manifest = read_json(truth_manifest_path)
    by_method = {(*_locus(row), row["method"]): row for row in rows}
    loci = sorted({_locus(row) for row in rows})
    truth = {}
    population = {}
    for row in rows:
        key = _locus(row)
        truth[key] = canonical_pair(row["truth_allele1"], row["truth_allele2"], row["gene"])
        population[key] = row.get("superpopulation", "")

    def correct(row: dict[str, str] | None, key: tuple[str, str, str, str]) -> int:
        if not row or not is_callable(row):
            return 0
        return int(canonical_pair(row["allele1"], row["allele2"], key[3]) == truth[key])

    subjects = {modality: {key[1] for key in loci if key[2] == modality}
                for modality in ("wes", "rnaseq")}
    overlap = subjects["wes"] & subjects["rnaseq"]
    cohort_rows = []
    for modality in ("wes", "rnaseq"):
        subset = [key for key in loci if key[2] == modality]
        cohort_rows.append({
            "modality": modality, "subjects": len(subjects[modality]), "loci": len(subset),
            "subjects_shared_between_assays": len(overlap),
            "requested_subjects_before_truth_filter": truth_manifest["requested_subjects"][modality],
            "requested_subjects_shared_between_assays": truth_manifest["requested_subject_overlap"],
            "requested_loci": truth_manifest["requested_loci"][modality],
            "excluded_ambiguous_or_unresolved_loci":
                truth_manifest["excluded_ambiguous_or_unresolved_loci"][modality],
        })

    allele_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for key, pair in truth.items():
        allele_counts[key[2]].update(pair)

    strata: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for key in loci:
        row = by_method[(*key, METHOD_PLURALITY)]
        outcome = correct(row, key)
        rarest = min(allele_counts[key[2]][allele] for allele in truth[key])
        frequency_bin = "1" if rarest == 1 else "2-4" if rarest <= 4 else ">=5"
        values = {
            "gene": key[3],
            "population": population[key] or "unknown",
            "truth_zygosity": "homozygous" if truth[key][0] == truth[key][1] else "heterozygous",
            "minimum_within_benchmark_truth_allele_count": frequency_bin,
        }
        for kind, value in values.items():
            strata[(key[2], kind, value)].append(outcome)
    stratum_rows = []
    for (modality, kind, value), outcomes in sorted(strata.items()):
        stratum_rows.append({"modality": modality, "stratum_type": kind, "stratum": value,
                             **_result(sum(outcomes), len(outcomes))})

    missingness = []
    for modality in ("wes", "rnaseq"):
        subset = [key for key in loci if key[2] == modality]
        for caller in PANELS[modality]:
            candidates = [by_method.get((*key, f"Caller:{caller}")) for key in subset]
            status = Counter((row or {}).get("call_status", "absent") for row in candidates)
            missingness.append({
                "modality": modality, "caller": caller, "loci": len(subset),
                "rows_present": sum(row is not None for row in candidates),
                "callable": sum(bool(row and is_callable(row)) for row in candidates),
                "partial": status["partial"], "missing": status["missing"],
                "absent": status["absent"], "invalid": status["invalid"],
            })

    support_groups: dict[tuple[str, int, int], list[tuple[int, str]]] = defaultdict(list)
    for key in loci:
        row = by_method[(*key, METHOD_PLURALITY)]
        top = int(row.get("top_support", "0") or 0)
        callable_tools = int(row.get("callable_tools", "0") or 0)
        support_groups[(key[2], top, callable_tools)].append(
            (correct(row, key), row.get("tie_at_top", "0")))
    support_rows = []
    for (modality, top, callable_tools), records in sorted(support_groups.items()):
        outcomes = [record[0] for record in records]
        fraction = Fraction(top, callable_tools) if callable_tools else Fraction(0, 1)
        support_rows.append({
            "modality": modality,
            "support_fraction": float(fraction),
            "support_numerator": top,
            "callable_callers": callable_tools,
            "support_profile": f"{top}/{callable_tools}",
            "support_defined": int(callable_tools > 0),
            "tied_loci": sum(record[1] == "1" for record in records),
            **_result(sum(outcomes), len(outcomes)),
        })

    correlations = []
    for modality in ("wes", "rnaseq"):
        subset = [key for key in loci if key[2] == modality]
        errors = {caller: [1 - correct(by_method.get((*key, f"Caller:{caller}")), key)
                           for key in subset] for caller in PANELS[modality]}
        for first, second in combinations(PANELS[modality], 2):
            pairs = Counter(zip(errors[first], errors[second]))
            n00, n01, n10, n11 = pairs[(0, 0)], pairs[(0, 1)], pairs[(1, 0)], pairs[(1, 1)]
            denominator = math.sqrt((n10 + n11) * (n00 + n01) * (n01 + n11) * (n00 + n10))
            phi = ((n11 * n00 - n10 * n01) / denominator) if denominator else 0.0
            by_subject: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])
            for key, e1, e2 in zip(subset, errors[first], errors[second]):
                by_subject[key[1]][2 * e1 + e2] += 1
            phi_lo, phi_hi = _phi_bootstrap_ci(
                [tuple(by_subject[subject]) for subject in sorted(by_subject)],
                seed=PHI_SEED + len(correlations))
            mutually_callable = [
                key for key in subset
                if is_callable(by_method.get((*key, f"Caller:{first}"), {}))
                and is_callable(by_method.get((*key, f"Caller:{second}"), {}))
            ]
            mutual_pairs = Counter(
                (1 - correct(by_method.get((*key, f"Caller:{first}")), key),
                 1 - correct(by_method.get((*key, f"Caller:{second}")), key))
                for key in mutually_callable
            )
            m00, m01 = mutual_pairs[(0, 0)], mutual_pairs[(0, 1)]
            m10, m11 = mutual_pairs[(1, 0)], mutual_pairs[(1, 1)]
            mutual_denominator = math.sqrt(
                (m10 + m11) * (m00 + m01) * (m01 + m11) * (m00 + m10)
            )
            mutual_phi = (
                (m11 * m00 - m10 * m01) / mutual_denominator
                if mutual_denominator else 0.0
            )
            correlations.append({
                "modality": modality, "caller1": first, "caller2": second,
                "loci": len(subset), "both_correct": n00, "caller2_only_wrong": n01,
                "caller1_only_wrong": n10, "both_wrong": n11, "error_phi": phi,
                "error_phi_ci_lo": phi_lo, "error_phi_ci_hi": phi_hi,
                "error_phi_interval_method": "subject_cluster_percentile_bootstrap",
                "error_phi_bootstrap_iterations": PHI_BOOTSTRAP,
                "mutually_callable_loci": len(mutually_callable),
                "mutually_callable_error_phi": mutual_phi,
            })

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_tsv(out / "cohort_summary.tsv", cohort_rows)
    write_tsv(out / "stratified_primary_results.tsv", stratum_rows)
    write_tsv(out / "caller_missingness.tsv", missingness)
    write_tsv(out / "support_stratified_concordance.tsv", support_rows)
    write_tsv(out / "caller_error_correlation.tsv", correlations)
    nomenclature_rows = []
    if reference is not None:
        audited_methods = {METHOD_PLURALITY} | {
            f"Caller:{caller}" for callers in PANELS.values() for caller in callers
        }
        for key in loci:
            truth_pair = truth[key]
            truth_states = [reference.classify(value, value, "") for value in truth_pair]
            for method in sorted(audited_methods):
                row = by_method.get((*key, method))
                if correct(row, key):
                    continue
                predicted_pair = ()
                predicted_states = []
                if row and is_callable(row):
                    predicted_pair = canonical_pair(row["allele1"], row["allele2"], key[3])
                    predicted_states = [reference.classify(value, value, "")
                                        for value in predicted_pair]
                nomenclature_rows.append({
                    "subject": key[1], "modality": key[2], "gene": key[3],
                    "method": method,
                    "truth_pair": "+".join(truth_pair),
                    "predicted_pair": "+".join(predicted_pair),
                    "call_status": (row or {}).get("call_status", "absent"),
                    "truth_membership_3_65": ";".join(
                        state["membership_status"] for state in truth_states
                    ),
                    "prediction_membership_3_65": ";".join(
                        state["membership_status"] for state in predicted_states
                    ),
                    "caller_database_release": (row or {}).get("database_version", ""),
                    "native_truth_representability": "unknown_exact_database_unavailable",
                    "nomenclature_only_error": 0,
                    "attribution": "algorithm_database_and_deployment_effects_not_separable",
                })
        write_tsv(out / "nomenclature_discordance_audit.tsv", nomenclature_rows)
    truth_flow_rows = []
    exclusion_rows = []
    candidate_occurrence_rows = []
    if candidate_truth_path:
        candidate_rows = read_tsv(candidate_truth_path)
        flow = Counter((row["modality"], row["truth_status"]) for row in candidate_rows)
        for modality in ("wes", "rnaseq"):
            requested = sum(row["modality"] == modality for row in candidate_rows)
            for status in ("resolved", "ambiguous", "invalid", "absent"):
                truth_flow_rows.append({
                    "modality": modality,
                    "truth_state": status,
                    "loci": flow[(modality, status)],
                    "requested_loci": requested,
                })
        grouped = Counter(
            (row["modality"], row["gene"], row.get("population", "") or "unknown",
             row["truth_status"])
            for row in candidate_rows
        )
        for (modality, gene, population_code, status), count in sorted(grouped.items()):
            exclusion_rows.append({
                "modality": modality, "gene": gene, "population": population_code,
                "truth_state": status, "loci": count,
            })
        for modality in ("wes", "rnaseq"):
            ambiguous = [row for row in candidate_rows
                         if row["modality"] == modality and row["truth_status"] == "ambiguous"]
            bounds: dict[str, list[int]] = defaultdict(lambda: [0, 0])
            for row in ambiguous:
                candidates = [tuple(pair) for pair in json.loads(row["truth_candidate_pairs_json"])]
                alleles = {allele for pair in candidates for allele in pair}
                for allele in alleles:
                    bounds[allele][1] += 1
                    if all(allele in pair for pair in candidates):
                        bounds[allele][0] += 1
            for allele, (minimum, maximum) in sorted(bounds.items()):
                candidate_occurrence_rows.append({
                    "modality": modality, "allele": allele,
                    "ambiguous_loci": len(ambiguous),
                    "minimum_locus_occurrences": minimum,
                    "maximum_locus_occurrences": maximum,
                    "interpretation": "benchmark_candidate_occurrence_bound_not_population_frequency",
                })
        write_tsv(out / "truth_flow.tsv", truth_flow_rows)
        write_tsv(out / "truth_exclusion_by_gene_population.tsv", exclusion_rows)
        write_tsv(out / "truth_candidate_occurrence_bounds.tsv", candidate_occurrence_rows)
    manifest = {
        "schema_version": "panelhla-development-characterisation-2",
        "joined_sha256": sha256(joined_path),
        "truth_manifest_sha256": sha256(truth_manifest_path),
        "candidate_truth_sha256": sha256(candidate_truth_path) if candidate_truth_path else "",
        "normalization_release": reference.release if reference is not None else "",
        "wes_rnaseq_shared_subjects": len(overlap),
        "outputs": {path.name: sha256(path) for path in out.glob("*.tsv")},
    }
    write_json(out / "characterisation_manifest.json", manifest)
    return manifest


def tie_break_sensitivity(joined_path: str, output_path: str) -> list[dict]:
    """Rescore ChampHLA-Consensus with the opposite tie-break.

    The rule breaks an exact tie toward the pair whose allele names sort first as
    character strings. Rebuilding the vote from the joined caller rows, this
    reports how many exact-endpoint loci were tied and how many would be correct
    if ties went to the pair that sorts last instead. The forward rebuild must
    reproduce every reported consensus call, or the comparison is refused.
    """
    by_locus: dict[tuple, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in read_tsv(joined_path):
        if row["modality"] in PANELS and (row.get("truth_allele1") or "").strip():
            by_locus[_locus(row)][row["method"]] = row
    output = []
    for modality in sorted({key[2] for key in by_locus}):
        loci = sorted(key for key in by_locus if key[2] == modality)
        ties = forward_correct = reverse_correct = 0
        for key in loci:
            rows = by_locus[key]
            truth = canonical_pair(rows[METHOD_PLURALITY]["truth_allele1"],
                                   rows[METHOD_PLURALITY]["truth_allele2"], key[3])
            votes: Counter = Counter()
            for caller in PANELS[modality]:
                row = rows.get(f"Caller:{caller}")
                if row and is_callable(row):
                    votes[canonical_pair(row["allele1"], row["allele2"], key[3])] += 1
            reported = rows[METHOD_PLURALITY]
            if not votes:
                continue
            top = max(votes.values())
            leaders = sorted(pair for pair, count in votes.items() if count == top)
            forward, reverse = leaders[0], leaders[-1]
            if forward != canonical_pair(reported["allele1"], reported["allele2"], key[3]):
                raise ValueError(f"forward rebuild does not reproduce the consensus at {key}")
            ties += len(leaders) > 1
            forward_correct += forward == truth
            reverse_correct += reverse == truth
        output.append({"modality": modality, "loci": len(loci), "tied_loci": ties,
                       "correct_first_pair": forward_correct,
                       "correct_last_pair": reverse_correct})
    write_tsv(output_path, output)
    return output


def single_allele_zygosity(calls_path: str, truth_path: str, output_path: str) -> list[dict]:
    """Where do callers report a single allele? (PSR-059)

    A caller that drops one haplotype reports a single allele at heterozygous loci.
    For every caller row with one reported allele -- a caller-native homozygous
    declaration or a partial call -- at an exact-endpoint locus, count whether the
    reference genotype there is homozygous.
    """
    truth = {(row["subject"], row["modality"], row["gene"]):
             row["truth_allele1"] == row["truth_allele2"] for row in read_tsv(truth_path)}
    counts: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for row in read_tsv(calls_path):
        single = (row.get("homozygosity_basis") == "caller_native_declaration"
                  or row["call_status"] == "partial")
        key = (row["subject"], row["modality"], row["gene"])
        if single and key in truth:
            counts[(row["modality"], row["caller"])][truth[key]] += 1
    output = []
    for modality in sorted({m for m, _ in counts}):
        for caller in sorted(c for m, c in counts if m == modality):
            tally = counts[(modality, caller)]
            output.append({"modality": modality, "caller": caller,
                           "single_allele_rows": sum(tally.values()),
                           "reference_homozygous": tally[True],
                           "reference_heterozygous": tally[False]})
        tally = sum((counts[key] for key in counts if key[0] == modality), Counter())
        output.append({"modality": modality, "caller": "all",
                       "single_allele_rows": sum(tally.values()),
                       "reference_homozygous": tally[True],
                       "reference_heterozygous": tally[False]})
    write_tsv(output_path, output)
    return output
