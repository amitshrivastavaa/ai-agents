"""Tests for moe — offline, stdlib only.

    python -m unittest labs.moe.tests.test_moe -v
"""
from __future__ import annotations

import unittest

from labs.moe.data import get_dataset
from labs.moe.experts import LinearExpert
from labs.moe.moe import MixtureOfExperts, single_model_error


class ExpertTests(unittest.TestCase):
    def test_fit_recovers_a_line(self):
        e = LinearExpert().fit([0, 1, 2, 3], [1, 3, 5, 7])   # y = 2x + 1
        self.assertAlmostEqual(e.slope, 2.0, places=6)
        self.assertAlmostEqual(e.intercept, 1.0, places=6)
        self.assertAlmostEqual(e.predict(10), 21.0, places=6)

    def test_weighted_fit_ignores_zero_weight_points(self):
        e = LinearExpert().fit_weighted([0, 1, 2, 100], [0, 1, 2, -999], [1, 1, 1, 0])
        self.assertAlmostEqual(e.slope, 1.0, places=6)      # the outlier is weight 0

    def test_single_point_predicts_constant(self):
        e = LinearExpert().fit([5.0], [3.0])
        self.assertEqual(e.predict(99), 3.0)


class MoETests(unittest.TestCase):
    def test_gate_is_a_distribution(self):
        moe = MixtureOfExperts(k=3).train(get_dataset("piecewise"))
        g = moe.gate(0.5)
        self.assertEqual(len(g), 3)
        self.assertAlmostEqual(sum(g), 1.0, places=6)

    def test_route_returns_valid_expert(self):
        moe = MixtureOfExperts(k=4).train(get_dataset("fan"))
        for x in (0.0, 0.3, 0.7, 1.0):
            self.assertIn(moe.route(x), range(4))

    def test_beats_single_model_on_piecewise(self):
        data = get_dataset("piecewise")
        single = single_model_error(data)
        moe = MixtureOfExperts(k=3).train(data)
        self.assertLess(moe.train_error(data), single * 0.5)   # clearly better

    def test_beats_single_model_on_fan(self):
        data = get_dataset("fan")
        single = single_model_error(data)
        moe = MixtureOfExperts(k=4).train(data)
        self.assertLess(moe.train_error(data), single * 0.6)

    def test_experts_specialize_and_share_the_load(self):
        moe = MixtureOfExperts(k=3).train(get_dataset("piecewise"))
        load = moe.load()
        self.assertEqual(sum(load), len(get_dataset("piecewise").X))
        self.assertTrue(all(c > 0 for c in load))           # no starved expert
        centres = [c for c, _ in moe.regions()]
        self.assertGreater(max(centres) - min(centres), 0.3)  # spread out

    def test_more_experts_help_then_plateau(self):
        data = get_dataset("piecewise")
        errs = [MixtureOfExperts(k=k).train(data).train_error(data) for k in (1, 2, 3)]
        self.assertGreater(errs[0], errs[1])
        self.assertGreater(errs[1], errs[2])

    def test_deterministic(self):
        data = get_dataset("fan")
        a = MixtureOfExperts(k=4).train(data).train_error(data)
        b = MixtureOfExperts(k=4).train(data).train_error(data)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
