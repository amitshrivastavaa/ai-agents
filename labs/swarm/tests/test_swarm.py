"""Tests for swarm (ACO) — offline, stdlib only.

    python -m unittest labs.swarm.tests.test_swarm -v
"""
from __future__ import annotations

import unittest

from labs.swarm.aco import AntColony
from labs.swarm.render import plot_tour
from labs.swarm.tsp import (INSTANCES, get_instance, nearest_neighbor, optimal,
                            tour_length)


class TSPTests(unittest.TestCase):
    def test_nearest_neighbor_is_a_valid_tour(self):
        tsp = get_instance("random8")
        tour = nearest_neighbor(tsp)
        self.assertEqual(sorted(tour), list(range(tsp.n)))

    def test_circle_optimal_is_perimeter(self):
        tsp = get_instance("circle")
        # the ring tour 0,1,2,...,n-1 has exactly the optimal length
        ring = list(range(tsp.n))
        self.assertAlmostEqual(tour_length(ring, tsp.dist), optimal(tsp), places=6)

    def test_brute_optimal_small(self):
        tsp = get_instance("random8")
        self.assertIsNotNone(optimal(tsp))
        self.assertLessEqual(optimal(tsp), tour_length(nearest_neighbor(tsp), tsp.dist))


class ACOTests(unittest.TestCase):
    def test_returns_valid_tour(self):
        tsp = get_instance("random15")
        res = AntColony(iterations=30).solve(tsp)
        self.assertEqual(sorted(res.best_tour), list(range(tsp.n)))

    def test_beats_or_matches_nearest_neighbor(self):
        for name in ("circle", "random8", "random15"):
            tsp = get_instance(name)
            nn = tour_length(nearest_neighbor(tsp), tsp.dist)
            aco = AntColony().solve(tsp).best_length
            with self.subTest(instance=name):
                self.assertLessEqual(aco, nn + 1e-9)

    def test_finds_optimal_where_known(self):
        for name in ("circle", "random8"):
            tsp = get_instance(name)
            aco = AntColony().solve(tsp).best_length
            with self.subTest(instance=name):
                self.assertLessEqual(aco, optimal(tsp) * 1.001)  # within 0.1%

    def test_convergence_is_monotonic(self):
        res = AntColony().solve(get_instance("random15"))
        for a, b in zip(res.history, res.history[1:]):
            self.assertGreaterEqual(a, b)  # best-so-far never worsens

    def test_deterministic(self):
        a = AntColony(seed="z").solve(get_instance("random15")).best_length
        b = AntColony(seed="z").solve(get_instance("random15")).best_length
        self.assertEqual(a, b)


class RenderTests(unittest.TestCase):
    def test_plot_dimensions_and_labels(self):
        tsp = get_instance("circle")
        out = plot_tour(tsp, list(range(tsp.n)), width=30, height=12)
        rows = out.splitlines()
        self.assertEqual(len(rows), 12)
        self.assertIn("0", out)  # first city labelled


if __name__ == "__main__":
    unittest.main()
