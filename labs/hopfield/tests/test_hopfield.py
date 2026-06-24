"""Tests for hopfield — offline, stdlib only.

    python -m unittest labs.hopfield.tests.test_hopfield -v
"""
from __future__ import annotations

import unittest

from labs.hopfield.network import ClassicHopfield, ModernHopfield, overlap
from labs.hopfield.patterns import GLYPHS, corrupt, occlude, to_vec


class PatternTests(unittest.TestCase):
    def test_to_vec_is_pm_one(self):
        v = to_vec(["#.", ".#"])
        self.assertEqual(v, [1, -1, -1, 1])

    def test_corrupt_changes_about_the_right_fraction(self):
        v = GLYPHS["X"]
        c = corrupt(v, 0.5, seed="t")
        diff = sum(1 for a, b in zip(v, c) if a != b) / len(v)
        self.assertGreater(diff, 0.2)
        self.assertLess(diff, 0.8)


class ClassicTests(unittest.TestCase):
    def setUp(self):
        self.net = ClassicHopfield().store(GLYPHS)

    def test_stored_patterns_are_fixed_points(self):
        for name, vec in GLYPHS.items():
            res = self.net.recall(vec)
            self.assertEqual(res.pattern, vec, f"{name} is not a fixed point")

    def test_perfectly_recovers_low_noise(self):
        for name, vec in GLYPHS.items():
            res = self.net.recall(corrupt(vec, 0.1, seed=f"{name}lo"))
            with self.subTest(glyph=name):
                self.assertEqual(res.label, name)

    def test_average_recovery_high_at_moderate_noise(self):
        # individual noisy cues vary, but the average overlap stays high
        total = cnt = 0
        for name, vec in GLYPHS.items():
            for k in range(6):
                total += overlap(self.net.recall(corrupt(vec, 0.2, seed=f"{name}{k}")).pattern, vec)
                cnt += 1
        self.assertGreaterEqual(total / cnt, 0.9)

    def test_recovers_from_occlusion(self):
        for name, vec in GLYPHS.items():
            res = self.net.recall(occlude(vec, 0.4))
            with self.subTest(glyph=name):
                self.assertEqual(res.label, name)

    def test_energy_monotonically_decreases(self):
        res = self.net.recall(corrupt(GLYPHS["H"], 0.3, seed="e"))
        for a, b in zip(res.energy_history, res.energy_history[1:]):
            self.assertLessEqual(b, a + 1e-9)

    def test_deterministic(self):
        cue = corrupt(GLYPHS["O"], 0.3, seed="d")
        self.assertEqual(self.net.recall(cue).pattern, self.net.recall(cue).pattern)


class ModernTests(unittest.TestCase):
    def test_recovers_clean_and_noisy(self):
        net = ModernHopfield().store(GLYPHS)
        for name, vec in GLYPHS.items():
            self.assertEqual(net.recall(vec).label, name)
            self.assertGreaterEqual(overlap(net.recall(corrupt(vec, 0.2, seed=name)).pattern, vec), 0.9)

    def test_modern_at_least_as_robust_as_classic_under_noise(self):
        classic = ClassicHopfield().store(GLYPHS)
        modern = ModernHopfield().store(GLYPHS)
        c = m = cnt = 0
        for noise in (0.3, 0.4):
            for name, vec in GLYPHS.items():
                for k in range(6):
                    cue = corrupt(vec, noise, seed=f"{name}{k}")
                    c += overlap(classic.recall(cue).pattern, vec)
                    m += overlap(modern.recall(cue).pattern, vec)
                    cnt += 1
        self.assertGreaterEqual(m / cnt, c / cnt)  # modern degrades more gracefully


if __name__ == "__main__":
    unittest.main()
