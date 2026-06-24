"""Tests for planner — offline, stdlib only.

    python -m unittest labs.planner.tests.test_planner -v
"""
from __future__ import annotations

import unittest

from labs.planner.blocksworld import get_problem, ground_actions
from labs.planner.search import astar_plan, bfs_plan, plan
from labs.planner.strips import Action, apply_action, applicable, satisfies


class StripsTests(unittest.TestCase):
    def test_applicable_and_apply(self):
        a = Action("a", pre=frozenset({("p",)}),
                   add=frozenset({("q",)}), delete=frozenset({("p",)}))
        s = frozenset({("p",)})
        self.assertTrue(applicable(a, s))
        self.assertEqual(apply_action(a, s), frozenset({("q",)}))
        self.assertFalse(applicable(a, frozenset({("q",)})))

    def test_ground_actions_count(self):
        # 3 blocks: pickup+putdown (2 per block = 6) + stack+unstack (2 per ordered pair = 12)
        self.assertEqual(len(ground_actions(("A", "B", "C"))), 6 + 12)


def _valid(problem, steps) -> bool:
    s = problem.init
    for a in steps:
        if not applicable(a, s):
            return False
        s = apply_action(a, s)
    return satisfies(s, problem.goal)


class SolveTests(unittest.TestCase):
    def test_solves_sussman_optimally(self):
        p = get_problem("sussman")
        steps, states = plan(p, method="bfs")
        self.assertIsNotNone(steps)
        self.assertTrue(_valid(p, steps))
        self.assertEqual(len(steps), 6)               # known optimum

    def test_astar_also_solves(self):
        for name in ("sussman", "reverse", "build4"):
            p = get_problem(name)
            steps, _ = plan(p, method="astar")
            with self.subTest(problem=name):
                self.assertIsNotNone(steps)
                self.assertTrue(_valid(p, steps))

    def test_bfs_and_astar_same_length(self):
        for name in ("sussman", "reverse", "build4"):
            p = get_problem(name)
            b, _ = plan(p, method="bfs")
            a, _ = plan(p, method="astar")
            with self.subTest(problem=name):
                self.assertEqual(len(b), len(a))      # both optimal here

    def test_trace_states_are_consistent(self):
        p = get_problem("reverse")
        steps, states = plan(p, method="bfs")
        self.assertEqual(len(states), len(steps) + 1)
        for a, before, after in zip(steps, states, states[1:]):
            self.assertEqual(apply_action(a, before), after)

    def test_goal_already_satisfied_is_empty_plan(self):
        actions = ground_actions(("A",))
        s = frozenset({("ontable", "A"), ("clear", "A"), ("handempty",)})
        self.assertEqual(bfs_plan(actions, s, frozenset({("ontable", "A")})), [])

    def test_deterministic(self):
        a = [str(x) for x in plan(get_problem("sussman"))[0]]
        b = [str(x) for x in plan(get_problem("sussman"))[0]]
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
