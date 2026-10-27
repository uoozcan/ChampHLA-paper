from __future__ import annotations

import math
import random
from collections import Counter, defaultdict


def _binomial_tail_at_least(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def _binomial_tail_at_most(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def exact_binomial_ci(successes: int, trials: int, alpha: float = 0.05) -> tuple[float, float]:
    """Two-sided Clopper-Pearson interval without an optional statistics package."""
    if trials <= 0 or not 0 <= successes <= trials:
        raise ValueError("binomial interval requires 0 <= successes <= trials and trials > 0")
    target = alpha / 2
    if successes == 0:
        lower = 0.0
    else:
        lo, hi = 0.0, successes / trials
        for _ in range(80):
            mid = (lo + hi) / 2
            if _binomial_tail_at_least(successes, trials, mid) < target:
                lo = mid
            else:
                hi = mid
        lower = (lo + hi) / 2
    if successes == trials:
        upper = 1.0
    else:
        lo, hi = successes / trials, 1.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if _binomial_tail_at_most(successes, trials, mid) > target:
                lo = mid
            else:
                hi = mid
        upper = (lo + hi) / 2
    return lower, upper


def exact_cluster_signflip(subject_deltas) -> float:
    """Two-sided exact sign-flip test using an aggregated integer distribution."""
    values = [int(value) for value in subject_deltas if int(value) != 0]
    if not values:
        return 1.0
    distribution = Counter({0: 1})
    for value in values:
        updated = Counter()
        for total, count in distribution.items():
            updated[total + value] += count
            updated[total - value] += count
        distribution = updated
    observed = abs(sum(values))
    numerator = sum(count for total, count in distribution.items() if abs(total) >= observed)
    return numerator / sum(distribution.values())


def subject_cluster_signflip(subject_deltas, *, exact_max: int = 25,
                             iterations: int = 1000000,
                             seed: int = 20260926) -> tuple[float, str]:
    """Two-sided subject sign-flip test with an explicit exact/Monte Carlo policy.

    Up to 25 nonzero subject deltas are enumerated exactly by default. The
    aggregated distribution avoids materialising all 2**n assignments. Above
    that boundary the Monte Carlo branch uses the standard plus-one correction,
    so it can never report a zero p-value. Inputs are subject-aggregate locus
    differences.
    """
    values = [int(value) for value in subject_deltas if int(value) != 0]
    if not values:
        return 1.0, "exact_enumeration"
    if len(values) <= exact_max:
        return exact_cluster_signflip(values), "exact_enumeration"
    if iterations <= 0:
        raise ValueError("Monte Carlo sign-flip iterations must be positive")
    observed = abs(sum(values))
    try:
        import numpy as np

        rng_np = np.random.default_rng(seed)
        value_array = np.asarray(values, dtype=np.int64)
        extreme = 0
        remaining = iterations
        while remaining:
            size = min(100000, remaining)
            signs = rng_np.integers(0, 2, size=(size, len(values)), dtype=np.int8) * 2 - 1
            totals = signs @ value_array
            extreme += int(np.count_nonzero(np.abs(totals) >= observed))
            remaining -= size
    except ImportError:
        rng = random.Random(seed)
        extreme = 0
        for _ in range(iterations):
            total = sum(value if rng.getrandbits(1) else -value for value in values)
            extreme += abs(total) >= observed
    return (extreme + 1) / (iterations + 1), "monte_carlo_plus_one"


def cluster_t_difference(by_subject: dict[str, list[int]], *, alpha: float = 0.05,
                         family_size: int = 1) -> dict[str, float | int | str]:
    """CR1 cluster-robust inference for a locus-weighted mean difference.

    The point estimate weights every locus equally.  Dependence is handled by
    summing residuals within subjects and applying the finite-cluster CR1
    correction.  The Bonferroni interval uses the same comparison family as
    the Holm-adjusted tests, making the two displays logically coherent.
    """
    if not by_subject:
        raise ValueError("cluster-t inference requires at least one subject")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between zero and one")
    if family_size < 1:
        raise ValueError("family_size must be positive")
    clusters = sorted(by_subject)
    cluster_count = len(clusters)
    observations = sum(len(by_subject[subject]) for subject in clusters)
    if observations == 0:
        raise ValueError("cluster-t inference requires at least one locus")
    estimate = sum(sum(by_subject[subject]) for subject in clusters) / observations
    if cluster_count == 1:
        raise ValueError("cluster-t inference requires at least two subjects")
    residual_sums = [
        sum(float(value) - estimate for value in by_subject[subject])
        for subject in clusters
    ]
    variance = (cluster_count / (cluster_count - 1)) * sum(
        value * value for value in residual_sums
    ) / (observations * observations)
    standard_error = math.sqrt(max(0.0, variance))
    degrees_freedom = cluster_count - 1
    if standard_error == 0:
        p_value = 1.0 if estimate == 0 else 0.0
        point_lo = point_hi = adjusted_lo = adjusted_hi = estimate
    else:
        try:
            from scipy.stats import t as student_t
        except ImportError as exc:  # pragma: no cover - release environment gate
            raise RuntimeError("cluster-t inference requires scipy") from exc
        statistic = estimate / standard_error
        p_value = 2 * float(student_t.sf(abs(statistic), degrees_freedom))
        point_critical = float(student_t.ppf(1 - alpha / 2, degrees_freedom))
        adjusted_critical = float(
            student_t.ppf(1 - alpha / (2 * family_size), degrees_freedom)
        )
        point_lo = estimate - point_critical * standard_error
        point_hi = estimate + point_critical * standard_error
        adjusted_lo = estimate - adjusted_critical * standard_error
        adjusted_hi = estimate + adjusted_critical * standard_error
    return {
        "estimate": estimate,
        "standard_error": standard_error,
        "degrees_freedom": degrees_freedom,
        "clusters": cluster_count,
        "observations": observations,
        "p_value": p_value,
        "pointwise_ci_lo": point_lo,
        "pointwise_ci_hi": point_hi,
        "adjusted_ci_lo": adjusted_lo,
        "adjusted_ci_hi": adjusted_hi,
        "family_size": family_size,
        "inference_method": "locus_weighted_cr1_cluster_t",
    }


def cluster_bootstrap_ratio_ci(by_subject: dict[str, list[tuple[int, int]]],
                               iterations: int = 100000, seed: int = 20260925,
                               alpha: float = 0.05) -> tuple[float, float]:
    """Subject-cluster percentile interval for a locus-weighted ratio estimator."""
    subjects = sorted(by_subject)
    if not subjects:
        return 0.0, 0.0
    if iterations <= 0:
        raise ValueError("bootstrap iterations must be positive")
    totals = [(sum(int(value) for value, _ in by_subject[subject]),
               sum(int(weight) for _, weight in by_subject[subject]))
              for subject in subjects]
    try:
        import numpy as np

        values = np.asarray(totals, dtype=np.int64)
        rng_np = np.random.default_rng(seed)
        batches = []
        remaining = iterations
        while remaining:
            size = min(10000, remaining)
            sampled = values[rng_np.integers(0, len(subjects), size=(size, len(subjects)))].sum(axis=1)
            batches.append(np.divide(sampled[:, 0], sampled[:, 1],
                                     out=np.zeros(size, dtype=float),
                                     where=sampled[:, 1] != 0))
            remaining -= size
        estimates = np.concatenate(batches).tolist()
    except ImportError:
        rng = random.Random(seed)
        estimates = []
        for _ in range(iterations):
            sampled = [totals[rng.randrange(len(subjects))] for _subject in subjects]
            numerator = sum(value for value, _ in sampled)
            denominator = sum(weight for _, weight in sampled)
            estimates.append(numerator / denominator if denominator else 0.0)
    estimates.sort()
    lo = estimates[min(iterations - 1, int((alpha / 2) * iterations))]
    hi = estimates[min(iterations - 1, int((1 - alpha / 2) * iterations))]
    return lo, hi


def cluster_bootstrap_ci_from_deltas(by_subject: dict[str, list[int]],
                                     iterations: int = 100000, seed: int = 20260831,
                                     alpha: float = 0.05) -> tuple[float, float]:
    """Subject bootstrap of the fixed-denominator ratio-estimator difference.

    ``alpha`` is the two-sided error rate. Pass ``alpha / m`` to obtain intervals
    that hold simultaneously across a family of m comparators, which is what a
    non-inferiority decision over a whole comparator family needs; the default
    0.05 gives the ordinary per-comparator interval.
    """
    ratios = {subject: [(sum(values), len(values))]
              for subject, values in by_subject.items()}
    return cluster_bootstrap_ratio_ci(ratios, iterations, seed, alpha)


def cluster_bootstrap_ci(rows: list[dict], baseline_field: str, selected_field: str,
                         iterations: int = 100000, seed: int = 20260831,
                         alpha: float = 0.05) -> tuple[float, float]:
    """Subject bootstrap over locus rows carrying two correctness fields."""
    by_subject: dict[str, list[int]] = defaultdict(list)
    for row in rows:
        by_subject[row["subject"]].append(int(row[selected_field]) - int(row[baseline_field]))
    return cluster_bootstrap_ci_from_deltas(by_subject, iterations, seed, alpha)


def holm_adjust(records: list[dict], p_field: str = "p_value") -> list[dict]:
    """Return records with monotone Holm-adjusted p-values and rejection flags."""
    ordered = sorted(enumerate(records), key=lambda item: float(item[1][p_field]))
    adjusted = [1.0] * len(records)
    running = 0.0
    total = len(records)
    for rank, (index, row) in enumerate(ordered):
        value = min(1.0, (total - rank) * float(row[p_field]))
        running = max(running, value)
        adjusted[index] = running
    result = []
    for index, row in enumerate(records):
        result.append({**row, "holm_adjusted_p": adjusted[index],
                       "holm_significant": int(adjusted[index] < 0.05)})
    return result


def subject_deltas(rows: list[dict], baseline_field: str, selected_field: str) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for row in rows:
        totals[row["subject"]] += int(row[selected_field]) - int(row[baseline_field])
    return dict(totals)
