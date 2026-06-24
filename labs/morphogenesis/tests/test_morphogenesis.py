"""Tests for morphogenesis — offline, stdlib only.

    python -m unittest labs.morphogenesis.tests.test_morphogenesis -v
"""
from __future__ import annotations

import unittest

from labs.morphogenesis.grid import Grid, PRESETS, get_preset
from labs.morphogenesis.render import shade


def _region_mean_v(g: Grid, x0, y0, x1, y1) -> float:
    vals = [g.V[(y % g.h) * g.w + (x % g.w)] for y in range(y0, y1) for x in range(x0, x1)]
    return sum(vals) / len(vals)


class GridTests(unittest.TestCase):
    def test_presets_valid(self):
        for name in PRESETS:
            F, k, desc = get_preset(name)
            self.assertGreater(F, 0)
            self.assertGreater(k, 0)
            self.assertTrue(desc)

    def test_seed_then_step_grows_pattern(self):
        g = Grid.from_preset("mitosis", w=32, h=16, seed="t")
        before = g.activity()
        g.step(600)
        self.assertGreater(g.activity(), before)         # V has spread

    def test_values_stay_bounded(self):
        g = Grid.from_preset("coral", w=30, h=14, seed="t")
        g.step(800)
        self.assertTrue(all(0.0 <= u <= 1.5 for u in g.U))
        self.assertTrue(all(-0.1 <= v <= 1.0 for v in g.V))  # no blow-up

    def test_deterministic(self):
        a = Grid.from_preset("maze", w=28, h=14, seed="z"); a.step(500)
        b = Grid.from_preset("maze", w=28, h=14, seed="z"); b.step(500)
        self.assertEqual(a.V, b.V)

    def test_damage_clears_region(self):
        g = Grid.from_preset("mitosis", w=32, h=16, seed="t")
        g.step(800)
        g.damage(x0=10, y0=4, x1=22, y1=12)
        self.assertEqual(_region_mean_v(g, 10, 4, 22, 12), 0.0)


class HealingTests(unittest.TestCase):
    def test_pattern_regrows_after_damage(self):
        g = Grid.from_preset("mitosis", w=40, h=18, seed="heal")
        g.step(1400)
        g.damage(x0=14, y0=5, x1=26, y1=13)
        wounded = _region_mean_v(g, 14, 5, 26, 13)   # ~0 right after damage
        g.step(1400)
        healed = _region_mean_v(g, 14, 5, 26, 13)
        self.assertEqual(wounded, 0.0)
        self.assertGreater(healed, 0.02)             # pattern grew back into the hole


class RenderTests(unittest.TestCase):
    def test_shade_dimensions(self):
        g = Grid.from_preset("spots", w=20, h=10, seed="t")
        g.step(200)
        rows = shade(g).splitlines()
        self.assertEqual(len(rows), 10)
        self.assertTrue(all(len(r) == 20 for r in rows))


if __name__ == "__main__":
    unittest.main()
