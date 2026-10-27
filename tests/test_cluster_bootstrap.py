from __future__ import annotations

import unittest

from champhla_confirmation.statistics import (cluster_bootstrap_ci,
                                              cluster_bootstrap_ci_from_deltas,
                                              subject_deltas)

ITERATIONS = 2000


def _rows(per_subject: dict[str, list[tuple[int, int]]]) -> list[dict]:
    """Locus rows carrying a baseline and a selected correctness flag."""
    return [{"subject": subject, "baseline_correct": baseline, "selected_correct": selected}
            for subject, pairs in per_subject.items() for baseline, selected in pairs]


class SubjectDeltasTests(unittest.TestCase):
    def test_deltas_aggregate_per_subject_and_signs_follow_selected_minus_baseline(self):
        rows = _rows({"S1": [(0, 1), (1, 1)], "S2": [(1, 0)]})
        self.assertEqual({"S1": 1, "S2": -1},
                         subject_deltas(rows, "baseline_correct", "selected_correct"))

    def test_string_flags_are_accepted(self):
        rows = [{"subject": "S1", "baseline_correct": "0", "selected_correct": "1"}]
        self.assertEqual({"S1": 1}, subject_deltas(rows, "baseline_correct", "selected_correct"))


class ClusterBootstrapTests(unittest.TestCase):
    def test_empty_input_returns_a_degenerate_interval(self):
        self.assertEqual((0.0, 0.0), cluster_bootstrap_ci_from_deltas({}))

    def test_a_constant_difference_has_a_zero_width_interval_at_that_value(self):
        """Every subject differs by the same amount, so resampling cannot move it."""
        lo, hi = cluster_bootstrap_ci_from_deltas({f"S{i}": [1] for i in range(8)},
                                                  iterations=ITERATIONS)
        self.assertEqual((1.0, 1.0), (lo, hi))

    def test_no_difference_anywhere_gives_a_zero_interval(self):
        lo, hi = cluster_bootstrap_ci_from_deltas({f"S{i}": [0, 0] for i in range(8)},
                                                  iterations=ITERATIONS)
        self.assertEqual((0.0, 0.0), (lo, hi))

    def test_the_interval_brackets_the_observed_difference(self):
        deltas = {f"S{i}": [1 if i % 3 else 0] for i in range(12)}
        observed = sum(sum(v) for v in deltas.values()) / sum(len(v) for v in deltas.values())
        lo, hi = cluster_bootstrap_ci_from_deltas(deltas, iterations=ITERATIONS)
        self.assertLessEqual(lo, observed)
        self.assertLessEqual(observed, hi)

    def test_the_same_seed_reproduces_the_interval_exactly(self):
        deltas = {f"S{i}": [1 if i % 3 else -1] for i in range(10)}
        first = cluster_bootstrap_ci_from_deltas(deltas, iterations=ITERATIONS, seed=7)
        second = cluster_bootstrap_ci_from_deltas(deltas, iterations=ITERATIONS, seed=7)
        self.assertEqual(first, second)

    def test_different_seeds_resample_differently(self):
        """The guard on the defect in decisions/20260917_protocol_amendment.json:
        a seed shared across comparators makes every one of them resample on an
        identical sequence, so their intervals come out perfectly correlated. The
        seed must therefore actually change the resampling.

        Deltas are deliberately heterogeneous across 40 subjects. On a small,
        near-constant cohort the bootstrap distribution is coarse enough that two
        seeds can land on the same percentile endpoints by chance, which would make
        this assertion flaky rather than wrong.
        """
        deltas = {f"S{i}": [(i % 5) - 2] * (1 + i % 3) for i in range(40)}
        intervals = {cluster_bootstrap_ci_from_deltas(deltas, iterations=ITERATIONS, seed=seed)
                     for seed in range(7, 13)}
        self.assertGreater(len(intervals), 1,
                           "the seed does not affect the resampling: a shared seed would "
                           "make every comparator's interval identical")

    def test_a_smaller_alpha_widens_the_interval(self):
        """alpha/m is how a family-simultaneous bound is obtained, so a smaller
        alpha must not produce a narrower interval."""
        deltas = {f"S{i}": [1 if i % 3 else -1] for i in range(16)}
        wide = cluster_bootstrap_ci_from_deltas(deltas, iterations=ITERATIONS, alpha=0.05 / 12)
        narrow = cluster_bootstrap_ci_from_deltas(deltas, iterations=ITERATIONS, alpha=0.05)
        self.assertLessEqual(wide[0], narrow[0])
        self.assertGreaterEqual(wide[1], narrow[1])

    def test_row_wrapper_agrees_with_the_delta_form(self):
        per_subject = {"S1": [(0, 1), (1, 1)], "S2": [(1, 0)], "S3": [(0, 1)]}
        rows = _rows(per_subject)
        from_rows = cluster_bootstrap_ci(rows, "baseline_correct", "selected_correct",
                                         iterations=ITERATIONS, seed=11)
        by_subject = {"S1": [1, 0], "S2": [-1], "S3": [1]}
        from_deltas = cluster_bootstrap_ci_from_deltas(by_subject, iterations=ITERATIONS, seed=11)
        self.assertEqual(from_deltas, from_rows)

    def test_clustering_is_by_subject_not_by_locus(self):
        """One subject contributing many concordant loci must not be resampled as
        many independent units; the interval stays at the constant difference."""
        lo, hi = cluster_bootstrap_ci_from_deltas({"S1": [1] * 50, "S2": [1] * 50},
                                                  iterations=ITERATIONS)
        self.assertEqual((1.0, 1.0), (lo, hi))


if __name__ == "__main__":
    unittest.main()
