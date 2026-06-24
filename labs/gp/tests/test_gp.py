import math
import unittest

from labs.gp.linalg import cholesky, chol_solve, solve_lower
from labs.gp.gp import GP, rbf


class TestLinalg(unittest.TestCase):
    def test_cholesky_reconstructs(self):
        A = [[4.0, 2.0, 1.0], [2.0, 5.0, 3.0], [1.0, 3.0, 6.0]]
        L = cholesky(A)
        n = len(A)
        rec = [[sum(L[i][k] * L[j][k] for k in range(n)) for j in range(n)]
               for i in range(n)]
        self.assertLess(max(abs(rec[i][j] - A[i][j])
                            for i in range(n) for j in range(n)), 1e-12)

    def test_cholesky_rejects_non_pd(self):
        with self.assertRaises(ValueError):
            cholesky([[1.0, 2.0], [2.0, 1.0]])      # indefinite

    def test_chol_solve(self):
        A = [[4.0, 1.0], [1.0, 3.0]]
        L = cholesky(A)
        x = chol_solve(L, [1.0, 2.0])
        Ax = [sum(A[i][j] * x[j] for j in range(2)) for i in range(2)]
        self.assertAlmostEqual(Ax[0], 1.0, places=9)
        self.assertAlmostEqual(Ax[1], 2.0, places=9)


class TestGP(unittest.TestCase):
    def setUp(self):
        self.X = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
        self.y = [math.sin(x) for x in self.X]
        self.gp = GP(rbf(length=1.0, var=1.0), noise=1e-4, prior_var=1.0).fit(self.X, self.y)

    def test_interpolates_training_data(self):
        for x, y in zip(self.X, self.y):
            mean, _ = self.gp.predict(x)
            self.assertAlmostEqual(mean, y, delta=0.02)

    def test_variance_small_at_data_large_away(self):
        for x in self.X:
            self.assertLess(self.gp.predict(x)[1], 0.02)         # ≈ noise floor
        far = self.gp.predict(20.0)[1]
        self.assertAlmostEqual(far, 1.0, delta=0.02)             # → prior_var

    def test_variance_is_bounded(self):
        for x in [-3.0, 0.5, 2.5, 4.5, 10.0]:
            v = self.gp.predict(x)[1]
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0 + 1e-9)

    def test_mean_reverts_to_prior_far_away(self):
        self.assertAlmostEqual(self.gp.predict(30.0)[0], 0.0, delta=1e-3)

    def test_interpolation_is_accurate_in_range(self):
        mse = sum((self.gp.predict(x)[0] - math.sin(x)) ** 2
                  for x in [0.5, 1.5, 2.5, 3.5, 4.5]) / 5
        self.assertLess(mse, 0.01)

    def test_longer_lengthscale_fills_gaps_more_confidently(self):
        Xg = [0.0, 1.0, 5.0, 6.0]                                # gap in [1,5]
        yg = [math.sin(x) for x in Xg]
        short = GP(rbf(length=0.5), noise=1e-3).fit(Xg, yg).predict(3.0)[1]
        long = GP(rbf(length=2.0), noise=1e-3).fit(Xg, yg).predict(3.0)[1]
        self.assertLess(long, short)            # more correlation reaches the gap

    def test_deterministic(self):
        a = [self.gp.predict(x) for x in [0.3, 1.7, 9.0]]
        b = [self.gp.predict(x) for x in [0.3, 1.7, 9.0]]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
