"""Tests for tree_of_thoughts — offline, stdlib only.

    python -m unittest labs.tree_of_thoughts.tests.test_tot -v
"""
from __future__ import annotations

import unittest
from fractions import Fraction

from labs.tree_of_thoughts.game24 import (TARGET, exact_solve, expand, expression,
                                          is_goal, to_state)
from labs.tree_of_thoughts.search import (PUZZLES, brute_force, compare,
                                          random_search, tot_search)


class Game24Tests(unittest.TestCase):
    def test_exact_solver_known_solutions(self):
        self.assertIsNotNone(exact_solve((1, 2, 3, 4)))
        self.assertIsNotNone(exact_solve((3, 3, 8, 8)))   # the hard one
        self.assertIsNone(exact_solve((1, 1, 1, 1)))      # unsolvable

    def test_exact_division_path_found(self):
        sol = exact_solve((3, 3, 8, 8))
        # the only solution uses a non-integer intermediate (8/3)
        self.assertTrue(any(s.result.denominator != 1 for s in sol))

    def test_expand_children_are_valid(self):
        state = to_state((3, 3, 8, 8))
        for child, step in expand(state):
            self.assertEqual(len(child), 3)
            self.assertEqual(eval_step(step), step.result)

    def test_solution_reaches_target(self):
        sol = exact_solve((4, 7, 8, 8))
        self.assertEqual(sol[-1].result, TARGET)
        self.assertIn("=", expression(sol))


def eval_step(step):
    a, b = step.a, step.b
    return {"+": a + b, "-": a - b, "*": a * b,
            "/": a / b if b else None}[step.op]


class SearchTests(unittest.TestCase):
    def test_tot_solves_all_solvable_puzzles(self):
        for p in PUZZLES:
            if exact_solve(p) is not None:
                with self.subTest(puzzle=p):
                    self.assertTrue(tot_search(p).solved, f"ToT missed {p}")

    def test_tot_does_not_falsely_solve_unsolvable(self):
        self.assertFalse(tot_search((1, 1, 1, 1)).solved)
        self.assertFalse(brute_force((1, 1, 1, 1)).solved)

    def test_tot_returns_a_valid_solution(self):
        res = tot_search((3, 3, 8, 8))
        self.assertTrue(res.solved)
        self.assertEqual(res.path[-1].result, TARGET)

    def test_tot_is_deterministic(self):
        a = tot_search((2, 3, 5, 12), seed="z")
        b = tot_search((2, 3, 5, 12), seed="z")
        self.assertEqual([str(s) for s in a.path], [str(s) for s in b.path])

    def test_tot_examines_fewer_states_than_brute(self):
        c = compare()
        self.assertLess(c["tree_of_thoughts"]["avg_nodes"], c["brute_force"]["avg_nodes"])

    def test_tot_solves_at_least_as_many_as_random(self):
        c = compare()
        self.assertGreaterEqual(c["tree_of_thoughts"]["solved"], c["random"]["solved"])


if __name__ == "__main__":
    unittest.main()
