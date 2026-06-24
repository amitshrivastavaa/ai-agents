"""Tests for diffusion — offline, stdlib only.

    python -m unittest labs.diffusion.tests.test_diffusion -v
"""
from __future__ import annotations

import math
import unittest

from labs._kernel import rng
from labs.diffusion.diffusion import (_noise_levels, generate,
                                      nearest_mode_distance, score)
from labs.diffusion.target import TARGETS, get_target


class ScoreTests(unittest.TestCase):
    def test_score_points_toward_a_mode(self):
        modes = [(5.0, 0.0)]
        # just to the right of the mode → score should pull left (negative x)
        sx, sy = score((6.0, 0.0), modes, var=1.0)
        self.assertLess(sx, 0.0)
        self.assertAlmostEqual(sy, 0.0, places=6)

    def test_score_at_a_lone_mode_is_zero(self):
        sx, sy = score((3.0, -2.0), [(3.0, -2.0)], var=1.0)
        self.assertAlmostEqual(sx, 0.0, places=6)
        self.assertAlmostEqual(sy, 0.0, places=6)

    def test_noise_levels_descend(self):
        levels = _noise_levels(10.0, 0.5, 8)
        self.assertEqual(len(levels), 8)
        self.assertAlmostEqual(levels[0], 10.0)
        self.assertAlmostEqual(levels[-1], 0.5)
        for a, b in zip(levels, levels[1:]):
            self.assertGreater(a, b)


class GenerateTests(unittest.TestCase):
    def test_samples_concentrate_on_modes(self):
        for name, target in TARGETS.items():
            samples = generate(target, n=120, seed="t")
            d = nearest_mode_distance(samples, target)
            with self.subTest(target=name):
                self.assertLess(d, 2.0)               # close to the modes
                # …and far closer than the noise they started from
                r = rng("n", name)
                noise = [(r.gauss(0, 12), r.gauss(0, 12)) for _ in range(120)]
                self.assertLess(d, nearest_mode_distance(noise, target) / 3)

    def test_right_number_of_samples(self):
        self.assertEqual(len(generate(get_target("ring"), n=77, seed="t")), 77)

    def test_deterministic(self):
        a = generate(get_target("blobs"), n=50, seed="z")
        b = generate(get_target("blobs"), n=50, seed="z")
        self.assertEqual(a, b)

    def test_samples_are_finite(self):
        for x, y in generate(get_target("spiral"), n=60, seed="t"):
            self.assertEqual(x, x)                    # not NaN
            self.assertLess(abs(x), 1e4)
            self.assertLess(abs(y), 1e4)


if __name__ == "__main__":
    unittest.main()
