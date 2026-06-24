import unittest

from labs.kmeans.data import blobs
from labs.kmeans.kmeans import KMeans
from labs.kmeans.metrics import purity, best_of, elbow


class TestKMeans(unittest.TestCase):
    def setUp(self):
        self.X, self.true, _ = blobs(n=400, k=4, spread=0.5, seed="t")

    def test_inertia_monotone_non_increasing(self):
        km = KMeans(k=4, init="kmeans++", seed="t").fit(self.X)
        h = km.history
        for a, b in zip(h, h[1:]):
            self.assertLessEqual(b, a + 1e-9)        # Lloyd never increases inertia

    def test_converges_before_max_iter(self):
        km = KMeans(k=4, seed="t", max_iter=100).fit(self.X)
        self.assertLess(km.n_iter, 100)

    def test_recovers_separated_blobs(self):
        km = best_of(self.X, k=4, restarts=5, seed="t")
        self.assertGreater(purity(km.labels, self.true, 4), 0.9)

    def test_kmeanspp_beats_random(self):
        pp = [KMeans(k=4, init="kmeans++", seed=("p", s)).fit(self.X).inertia
              for s in range(15)]
        rr = [KMeans(k=4, init="random", seed=("r", s)).fit(self.X).inertia
              for s in range(15)]
        self.assertLess(sum(pp) / len(pp), sum(rr) / len(rr))    # better on average
        self.assertLess(max(pp), max(rr))                        # and worst-case

    def test_elbow_at_true_k(self):
        el = dict(elbow(self.X, ks=range(1, 7), seed="t"))
        # the biggest relative drop should bottom out by k=4; k=5 barely helps.
        self.assertLess(el[4], 0.2 * el[2])
        self.assertGreater(el[5], 0.5 * el[4])      # diminishing returns past 4

    def test_labels_and_centroids_consistent(self):
        km = KMeans(k=4, seed="t").fit(self.X)
        self.assertEqual(len(km.labels), len(self.X))
        self.assertEqual(len(km.centroids), 4)
        self.assertTrue(all(0 <= c < 4 for c in km.labels))

    def test_deterministic(self):
        a = KMeans(k=4, seed="z").fit(self.X)
        b = KMeans(k=4, seed="z").fit(self.X)
        self.assertEqual(a.labels, b.labels)
        self.assertEqual(a.inertia, b.inertia)


if __name__ == "__main__":
    unittest.main()
