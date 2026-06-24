import math
import unittest

from labs.pca.pca import PCA
from labs.pca.data import correlated_2d, low_rank
from labs.pca.linalg import dot


def _mse(X, R):
    return sum(sum((a - b) ** 2 for a, b in zip(x, r)) for x, r in zip(X, R)) / len(X)


class TestPCA(unittest.TestCase):
    def setUp(self):
        self.pts, self.axis = correlated_2d(n=500, angle=0.5, seed="t")
        self.p = PCA(2).fit(self.pts)

    def test_pc1_recovers_known_axis(self):
        self.assertGreater(abs(dot(self.p.components[0], self.axis)), 0.99)

    def test_components_orthonormal(self):
        c0, c1 = self.p.components
        self.assertAlmostEqual(math.sqrt(dot(c0, c0)), 1.0, places=6)
        self.assertAlmostEqual(math.sqrt(dot(c1, c1)), 1.0, places=6)
        self.assertAlmostEqual(dot(c0, c1), 0.0, places=6)

    def test_explained_variance_descending_and_bounded(self):
        evr = self.p.explained_variance_ratio
        self.assertEqual(evr, sorted(evr, reverse=True))
        self.assertLessEqual(sum(evr), 1.0 + 1e-9)
        self.assertGreater(evr[0], 0.9)            # the stretched axis dominates

    def test_transform_shape(self):
        Z = self.p.transform(self.pts[:5])
        self.assertTrue(all(len(z) == 2 for z in Z))


class TestCompression(unittest.TestCase):
    def setUp(self):
        self.X = low_rank(n=200, dim=30, rank=3, noise=0.02, seed="c")

    def test_reconstruction_error_decreases(self):
        errs = [_mse(self.X, PCA(k).fit(self.X).reconstruct(self.X))
                for k in (1, 2, 3, 4)]
        for a, b in zip(errs, errs[1:]):
            self.assertLessEqual(b, a + 1e-9)      # monotone non-increasing

    def test_rank_components_capture_the_variance(self):
        p = PCA(3).fit(self.X)                      # true rank is 3
        self.assertGreater(sum(p.explained_variance_ratio), 0.95)

    def test_full_reconstruction_is_near_exact(self):
        Y = low_rank(n=60, dim=6, rank=6, noise=0.0, seed="f")
        p = PCA(6).fit(Y)
        self.assertLess(_mse(Y, p.reconstruct(Y)), 1e-6)

    def test_top_k_beats_random_subspace(self):
        # PCA's 2-D reconstruction should beat projecting onto 2 raw axes.
        p = PCA(2).fit(self.X)
        pca_err = _mse(self.X, p.reconstruct(self.X))
        mean = p.mean
        raw = [[v if i < 2 else m for i, (v, m) in enumerate(zip(x, mean))]
               for x in self.X]
        self.assertLess(pca_err, _mse(self.X, raw))

    def test_deterministic(self):
        a = PCA(3).fit(self.X)
        b = PCA(3).fit(self.X)
        self.assertEqual(a.explained_variance, b.explained_variance)


if __name__ == "__main__":
    unittest.main()
