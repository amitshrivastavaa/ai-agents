import unittest

from labs.pagerank import graph as G
from labs.pagerank.rank import pagerank, ranked
from labs.pagerank.surfer import surf


class TestPageRank(unittest.TestCase):
    def test_is_a_distribution(self):
        for name, g in G.GRAPHS.items():
            r, _ = pagerank(g)
            self.assertAlmostEqual(sum(r.values()), 1.0, places=9, msg=name)
            self.assertTrue(all(v > 0 for v in r.values()), name)

    def test_converges(self):
        _, iters = pagerank(G.web())
        self.assertLess(iters, 500)

    def test_web_ordering(self):
        order = ranked(G.web())
        self.assertEqual(order[0][0], "C")        # linked by A, B, D → top
        self.assertEqual(order[-1][0], "D")       # nothing links to D → bottom

    def test_matches_random_surfer(self):
        """PageRank == the surfer's stationary distribution (the definition)."""
        for name in ("web", "communities", "chain"):
            g = G.GRAPHS[name]
            r, _ = pagerank(g)
            s = surf(g, steps=300_000, seed=name)
            self.assertLess(max(abs(r[n] - s[n]) for n in r), 0.01, name)

    def test_damping_zero_is_uniform(self):
        r, _ = pagerank(G.web(), damping=0.0)
        self.assertTrue(all(abs(v - 0.25) < 1e-9 for v in r.values()))

    def test_dangling_node_handled(self):
        r, _ = pagerank(G.chain())                # last node has no out-links
        self.assertAlmostEqual(sum(r.values()), 1.0, places=9)

    def test_more_inlinks_more_rank(self):
        # 'hub' (many inlinks) must outrank a leaf spoke.
        g = G.star(6)
        r, _ = pagerank(g)
        self.assertGreater(r["hub"], r["s3"])

    def test_deterministic(self):
        self.assertEqual(pagerank(G.web()), pagerank(G.web()))


if __name__ == "__main__":
    unittest.main()
