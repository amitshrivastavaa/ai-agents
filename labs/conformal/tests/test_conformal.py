import unittest

from labs.conformal.data import heteroscedastic, split
from labs.conformal.conformal import (conformal_quantile, calibrate, coverage,
                                      mean_width)


class TestQuantile(unittest.TestCase):
    def test_conformal_quantile_order_statistic(self):
        scores = [5, 1, 3, 2, 4]                    # n=5
        # alpha=0.2 → rank = ceil(6*0.8) = 5 → 5th smallest = 5
        self.assertEqual(conformal_quantile(scores, 0.2), 5)
        # alpha=0.4 → rank = ceil(6*0.6) = 4 → 4th smallest = 4
        self.assertEqual(conformal_quantile(scores, 0.4), 4)

    def test_too_few_points_is_infinite(self):
        self.assertEqual(conformal_quantile([1, 2], 0.01), float("inf"))


class TestCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.X, cls.y = heteroscedastic(n=700, seed="t")

    def _mean_coverage(self, alpha, runs=30, normalized=False):
        covs = []
        for s in range(runs):
            tr, cal, te = split(self.X, self.y, seed=("s", s))
            p = calibrate(tr[0], tr[1], cal[0], cal[1], alpha=alpha, k=9,
                          normalized=normalized)
            covs.append(coverage(p, te[0], te[1]))
        return sum(covs) / len(covs)

    def test_marginal_coverage_matches_target(self):
        """The headline: coverage ≈ 1−α, distribution-free, across splits."""
        for alpha in (0.1, 0.2):
            mc = self._mean_coverage(alpha)
            self.assertGreaterEqual(mc, 1 - alpha - 0.03)     # ≳ guarantee
            self.assertLessEqual(mc, 1 - alpha + 0.06)        # not absurdly loose

    def test_smaller_alpha_wider_intervals(self):
        tr, cal, te = split(self.X, self.y, seed="w")
        wide = calibrate(tr[0], tr[1], cal[0], cal[1], alpha=0.05, k=9)
        narrow = calibrate(tr[0], tr[1], cal[0], cal[1], alpha=0.3, k=9)
        self.assertGreater(mean_width(wide, te[0]), mean_width(narrow, te[0]))

    def test_adaptive_widens_with_noise(self):
        tr, cal, te = split(self.X, self.y, seed="a")
        adp = calibrate(tr[0], tr[1], cal[0], cal[1], alpha=0.1, k=9, normalized=True)
        left = [adp(x)[1] - adp(x)[0] for x in te[0] if x < -1]
        right = [adp(x)[1] - adp(x)[0] for x in te[0] if x > 1]
        self.assertGreater(sum(right) / len(right), sum(left) / len(left))

    def test_adaptive_keeps_coverage(self):
        self.assertGreaterEqual(self._mean_coverage(0.1, normalized=True), 0.85)

    def test_deterministic(self):
        tr, cal, te = split(self.X, self.y, seed="z")
        p1 = calibrate(tr[0], tr[1], cal[0], cal[1], alpha=0.1)
        p2 = calibrate(tr[0], tr[1], cal[0], cal[1], alpha=0.1)
        self.assertEqual(coverage(p1, te[0], te[1]), coverage(p2, te[0], te[1]))


if __name__ == "__main__":
    unittest.main()
