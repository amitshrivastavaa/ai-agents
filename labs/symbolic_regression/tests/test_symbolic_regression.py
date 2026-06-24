"""Tests for symbolic_regression — offline, stdlib only.

    python -m unittest labs.symbolic_regression.tests.test_symbolic_regression -v
"""
from __future__ import annotations

import unittest

from labs._kernel import rng
from labs.symbolic_regression.expr import (Expr, evaluate, random_tree, replace_at,
                                           simplify, size, subtree_at, to_string)
from labs.symbolic_regression.gp import evolve, mse
from labs.symbolic_regression.targets import get_target


def _const(v):
    return Expr("const", value=v)


class ExprTests(unittest.TestCase):
    def test_eval_basic(self):
        tree = Expr("op", op="+", children=[Expr("var"), _const(3)])  # x + 3
        self.assertEqual(evaluate(tree, 5), 8)

    def test_protected_division(self):
        tree = Expr("op", op="/", children=[Expr("var"), _const(0)])  # x / 0 → 1
        self.assertEqual(evaluate(tree, 7), 1.0)

    def test_to_string(self):
        tree = Expr("op", op="*", children=[Expr("var"), Expr("var")])
        self.assertEqual(to_string(tree), "(x * x)")

    def test_subtree_and_replace_roundtrip(self):
        tree = Expr("op", op="+", children=[Expr("var"), _const(2)])
        self.assertEqual(size(tree), 3)
        replaced = replace_at(tree, 2, Expr("var"))   # const at index 2 → x ⇒ x + x
        self.assertEqual(evaluate(replaced, 4), 8)
        self.assertEqual(subtree_at(tree, 0).op, "+")
        self.assertEqual(subtree_at(tree, 1).kind, "var")

    def test_simplify_preserves_semantics(self):
        # -(-(x)) * 1  →  x
        tree = Expr("op", op="*", children=[
            Expr("op", op="neg", children=[Expr("op", op="neg", children=[Expr("var")])]),
            _const(1)])
        s = simplify(tree)
        self.assertEqual(to_string(s), "x")
        for x in (-2.0, 0.0, 3.5):
            self.assertAlmostEqual(evaluate(tree, x), evaluate(s, x))

    def test_random_tree_is_finite(self):
        r = rng("t")
        for _ in range(50):
            v = evaluate(random_tree(r, max_depth=4), 1.23)
            self.assertEqual(v, v)            # not NaN
            self.assertLessEqual(abs(v), 1e6)


class EvolveTests(unittest.TestCase):
    def test_rediscovers_quadratic(self):
        res = evolve(get_target("quadratic"), seed="s")
        self.assertLess(res.best_mse, 1e-4)
        self.assertTrue(res.solved)

    def test_rediscovers_damped_with_sin(self):
        res = evolve(get_target("damped"), seed="s")
        self.assertLess(res.best_mse, 1e-4)
        self.assertIn("sin", res.formula)

    def test_error_never_increases(self):
        res = evolve(get_target("cubic"), seed="s")
        self.assertLessEqual(res.history[-1], res.history[0])

    def test_reported_formula_matches_reported_error(self):
        t = get_target("linear")
        res = evolve(t, seed="s")
        self.assertAlmostEqual(mse(res.best, t.X, t.y), res.best_mse, places=9)

    def test_deterministic(self):
        a = evolve(get_target("quadratic"), seed="z")
        b = evolve(get_target("quadratic"), seed="z")
        self.assertEqual(a.formula, b.formula)
        self.assertEqual(a.best_mse, b.best_mse)


if __name__ == "__main__":
    unittest.main()
