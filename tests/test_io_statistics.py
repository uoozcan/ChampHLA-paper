from __future__ import annotations

import unittest

from champhla_confirmation.io import canonical_allele, canonical_pair
from champhla_confirmation.statistics import (
    cluster_bootstrap_ratio_ci,
    cluster_t_difference,
    exact_binomial_ci,
    exact_cluster_signflip,
    holm_adjust,
    subject_cluster_signflip,
)


class IoStatisticsTests(unittest.TestCase):
    def test_two_field_normalization_and_symmetry(self):
        self.assertEqual("A*01:01", canonical_allele("HLA-A*01:01:01", "A"))
        self.assertEqual(("A*01:01", "A*02:01"), canonical_pair("A*02:01", "01:01:01", "A"))

    def test_gene_mismatch_and_one_field_fail(self):
        with self.assertRaises(ValueError):
            canonical_allele("B*07:02", "A")
        with self.assertRaises(ValueError):
            canonical_allele("A*01", "A")

    def test_exact_signflip(self):
        self.assertEqual(1.0, exact_cluster_signflip([]))
        self.assertAlmostEqual(0.03125, exact_cluster_signflip([1] * 6))
        self.assertAlmostEqual(0.015625, exact_cluster_signflip([1] * 7))

    def test_signflip_policy_switches_and_is_deterministic(self):
        exact, exact_method = subject_cluster_signflip([1] * 6, exact_max=20)
        self.assertAlmostEqual(0.03125, exact)
        self.assertEqual("exact_enumeration", exact_method)
        first = subject_cluster_signflip([1] * 21, exact_max=20, iterations=5000, seed=7)
        second = subject_cluster_signflip([1] * 21, exact_max=20, iterations=5000, seed=7)
        self.assertEqual(first, second)
        self.assertEqual("monte_carlo_plus_one", first[1])
        self.assertGreater(first[0], 0.0)

    def test_default_exact_policy_extends_through_25_nonzero_subjects(self):
        p_value, method = subject_cluster_signflip([1] * 25)
        self.assertEqual("exact_enumeration", method)
        self.assertEqual(2 / 2**25, p_value)

        _, method = subject_cluster_signflip([1] * 26, iterations=1000, seed=11)
        self.assertEqual("monte_carlo_plus_one", method)

    def test_cluster_ratio_resamples_whole_subjects(self):
        by_subject = {
            "S1": [(1, 1), (1, 1), (1, 1)],
            "S2": [(0, 1)],
        }
        lo, hi = cluster_bootstrap_ratio_ci(by_subject, iterations=2000, seed=19)
        self.assertLessEqual(lo, 0.75)
        self.assertGreaterEqual(hi, 0.75)

    def test_holm_is_monotone(self):
        rows = holm_adjust([{"p_value": 0.01}, {"p_value": 0.02}, {"p_value": 0.5}])
        self.assertEqual([0.03, 0.04, 0.5], [row["holm_adjusted_p"] for row in rows])

    def test_cluster_t_is_locus_weighted_and_adjusted_interval_is_dual(self):
        by_subject = {"S1": [1, 1, 1], "S2": [-1], "S3": [0, 0]}
        result = cluster_t_difference(by_subject, family_size=3)
        self.assertAlmostEqual(result["estimate"], 2 / 6)
        self.assertEqual(result["clusters"], 3)
        self.assertEqual(result["observations"], 6)
        self.assertLessEqual(result["adjusted_ci_lo"], result["pointwise_ci_lo"])
        self.assertGreaterEqual(result["adjusted_ci_hi"], result["pointwise_ci_hi"])

    def test_cluster_t_zero_difference_is_exactly_degenerate(self):
        result = cluster_t_difference({"S1": [0], "S2": [0]}, family_size=2)
        self.assertEqual(result["estimate"], 0)
        self.assertEqual(result["p_value"], 1)
        self.assertEqual((result["adjusted_ci_lo"], result["adjusted_ci_hi"]), (0, 0))

    def test_exact_binomial_interval_has_correct_boundaries(self):
        self.assertEqual(0.0, exact_binomial_ci(0, 10)[0])
        self.assertEqual(1.0, exact_binomial_ci(10, 10)[1])
        lo, hi = exact_binomial_ci(5, 10)
        self.assertAlmostEqual(lo, 0.1871, places=3)
        self.assertAlmostEqual(hi, 0.8129, places=3)


if __name__ == "__main__":
    unittest.main()
