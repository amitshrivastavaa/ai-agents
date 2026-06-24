import math
import unittest

from labs.sketch.hashing import h64
from labs.sketch.countmin import CountMin
from labs.sketch.hyperloglog import HyperLogLog
from labs._kernel import rng


def _zipf_stream(n, seed):
    r = rng("sketch-test", seed, n)
    out = []
    for _ in range(n):
        if r.random() < 0.4:
            out.append("HOT" + str(r.randrange(5)))
        else:
            out.append("c" + str(r.randrange(6000)))
    return out


class TestHashing(unittest.TestCase):
    def test_deterministic_and_seeded(self):
        self.assertEqual(h64("x", 1), h64("x", 1))
        self.assertNotEqual(h64("x", 1), h64("x", 2))
        self.assertTrue(0 <= h64("y", 3) < (1 << 64))


class TestCountMin(unittest.TestCase):
    def setUp(self):
        self.stream = _zipf_stream(40000, seed=1)
        self.truth = {}
        for x in self.stream:
            self.truth[x] = self.truth.get(x, 0) + 1
        self.cm = CountMin(width=2000, depth=5)
        for x in self.stream:
            self.cm.add(x)

    def test_never_underestimates(self):
        self.assertTrue(all(self.cm.estimate(x) >= self.truth[x] for x in self.truth))

    def test_overshoot_within_bound(self):
        eps = math.e / self.cm.w
        bound = eps * self.cm.total
        self.assertTrue(all(self.cm.estimate(x) - self.truth[x] <= bound
                            for x in self.truth))

    def test_heavy_hitters_found(self):
        hh = dict(self.cm.heavy_hitters(set(self.stream), frac=0.02))
        for k in ("HOT0", "HOT1", "HOT2", "HOT3", "HOT4"):
            self.assertIn(k, hh)
        self.assertTrue(all(not k.startswith("c") for k in hh))   # no rare items

    def test_total_is_exact(self):
        self.assertEqual(self.cm.total, len(self.stream))

    def test_deterministic(self):
        cm2 = CountMin(width=2000, depth=5)
        for x in self.stream:
            cm2.add(x)
        self.assertEqual([cm2.estimate(k) for k in self.truth],
                         [self.cm.estimate(k) for k in self.truth])


class TestHyperLogLog(unittest.TestCase):
    def test_cardinality_accurate(self):
        for true_n in (500, 5000, 50000):
            hll = HyperLogLog(p=12)
            for i in range(true_n):
                hll.add("item" + str(i))
            err = abs(hll.count() - true_n) / true_n
            self.assertLess(err, 0.07, f"n={true_n} err={err:.3f}")

    def test_duplicates_dont_inflate(self):
        hll = HyperLogLog(p=12)
        for _ in range(5000):
            hll.add("the_same_key")
        self.assertLess(hll.count(), 5)              # ~1 distinct

    def test_empty_is_zero(self):
        self.assertEqual(HyperLogLog(p=10).count(), 0.0)

    def test_more_registers_less_error(self):
        def err(p):
            hll = HyperLogLog(p=p)
            for i in range(20000):
                hll.add("k" + str(i))
            return abs(hll.count() - 20000) / 20000
        self.assertLess(err(14), err(6) + 1e-9)      # finer p ≥ as accurate

    def test_deterministic(self):
        a, b = HyperLogLog(p=10), HyperLogLog(p=10)
        for i in range(3000):
            a.add(i)
            b.add(i)
        self.assertEqual(a.count(), b.count())


if __name__ == "__main__":
    unittest.main()
