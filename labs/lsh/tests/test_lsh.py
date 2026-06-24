import math
import unittest

from labs.lsh.data import make_dataset, make_queries, cosine, normalize
from labs.lsh.hashing import SimHash, angle, collision_prob
from labs.lsh.index import LSHIndex
from labs.lsh.eval import build, recall_at_k


class TestHashing(unittest.TestCase):
    def test_collision_law(self):
        """Empirical bit-agreement matches 1 − θ/π for several angles."""
        sh = SimHash(16, 6000, seed="law")
        for c in (0.9, 0.5, 0.0, -0.4):
            a = [1.0] + [0.0] * 15
            b = normalize([c, math.sqrt(1 - c * c)] + [0.0] * 14)
            agree = sum(1 for x, y in zip(sh.signature(a), sh.signature(b))
                        if x == y) / 6000
            self.assertAlmostEqual(agree, collision_prob(angle(a, b)), delta=0.03)

    def test_signature_length_and_determinism(self):
        sh = SimHash(8, 12, seed="s")
        v = normalize([1.0, 2.0, 3.0, -1.0, 0.5, 0.0, -2.0, 1.0])
        sig = sh.signature(v)
        self.assertEqual(len(sig), 12)
        self.assertEqual(sig, sh.signature(v))
        self.assertTrue(all(b in (0, 1) for b in sig))

    def test_identical_vectors_collide(self):
        sh = SimHash(10, 20, seed="x")
        v = normalize([0.3, -0.7, 0.1, 0.9, -0.2, 0.0, 0.4, 0.5, -0.8, 0.2])
        self.assertEqual(sh.signature(v), sh.signature(v))


class TestIndex(unittest.TestCase):
    def setUp(self):
        self.data, _ = make_dataset(n=500, dim=24, clusters=10, spread=0.12, seed="t")
        self.queries = make_queries(n=80, dim=24, clusters=10, spread=0.12,
                                    seed="q", base_seed="t")

    def test_brute_force_is_sorted_by_cosine(self):
        q = self.queries[0]
        nn = self.index().brute_force(q, 5)
        sims = [cosine(q, self.data[i]) for i in nn]
        self.assertEqual(sims, sorted(sims, reverse=True))

    def index(self, n_bits=8, n_tables=10):
        return build(self.data, n_bits=n_bits, n_tables=n_tables, seed="i")

    def test_high_recall_with_real_speedup(self):
        rec, frac = recall_at_k(self.index(n_bits=8, n_tables=12), self.queries, k=10)
        self.assertGreater(rec, 0.85)            # finds most true neighbours
        self.assertLess(frac, 0.3)               # while scanning <30% of the data

    def test_more_tables_raise_recall(self):
        few, _ = recall_at_k(self.index(n_bits=10, n_tables=4), self.queries, k=10)
        many, _ = recall_at_k(self.index(n_bits=10, n_tables=16), self.queries, k=10)
        self.assertGreater(many, few)

    def test_more_bits_shrink_candidate_set(self):
        _, frac_lo = recall_at_k(self.index(n_bits=8, n_tables=8), self.queries, k=10)
        _, frac_hi = recall_at_k(self.index(n_bits=12, n_tables=8), self.queries, k=10)
        self.assertLess(frac_hi, frac_lo)

    def test_candidates_are_real_neighbours(self):
        # The LSH top-k should overlap the exact top-k substantially.
        idx = self.index(n_bits=8, n_tables=12)
        q = self.queries[0]
        got, _ = idx.query(q, 10)
        true = set(idx.brute_force(q, 10))
        self.assertGreaterEqual(len(set(got) & true), 7)

    def test_deterministic(self):
        a = recall_at_k(self.index(), self.queries, k=10)
        b = recall_at_k(self.index(), self.queries, k=10)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
