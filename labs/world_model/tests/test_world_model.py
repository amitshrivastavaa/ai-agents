"""Tests for world_model — offline, stdlib only.

    python -m unittest labs.world_model.tests.test_world_model -v
"""
from __future__ import annotations

import unittest

from labs.world_model.env import GOAL_REWARD, LAVA_REWARD, MAPS, get_map
from labs.world_model.planners import (LookaheadPlanner, ReactivePlanner,
                                       RolloutPlanner)
from labs.world_model.runner import run_episode


class EnvTests(unittest.TestCase):
    def test_parse_finds_start_goal(self):
        env = get_map("lava_gap")
        self.assertTrue(env.passable(env.start))
        self.assertNotEqual(env.start, env.goal)

    def test_wall_bump_is_noop_with_cost(self):
        env = get_map("open")
        # stepping W from the start (against the wall) keeps position, costs a step
        nxt, r, done = env.step(env.start, "W")
        self.assertEqual(nxt, env.start)
        self.assertFalse(done)
        self.assertEqual(r, -1.0)

    def test_goal_terminates_positively(self):
        env = get_map("lava_gap")
        gx, gy = env.goal
        # step onto the goal from a passable neighbour
        for a, (dx, dy) in {"N": (0, 1), "S": (0, -1), "E": (-1, 0), "W": (1, 0)}.items():
            nb = (gx + dx, gy + dy)
            if env.passable(nb):
                _, r, done = env.step(nb, a)
                self.assertTrue(done)
                self.assertEqual(r, GOAL_REWARD)
                return
        self.fail("goal has no passable neighbour")

    def test_lava_terminates_negatively(self):
        env = get_map("lava_gap")
        lx, ly = next(iter(env.lava))
        for a, (dx, dy) in {"N": (0, 1), "S": (0, -1), "E": (-1, 0), "W": (1, 0)}.items():
            nb = (lx + dx, ly + dy)
            if env.passable(nb) and nb not in env.lava:
                _, r, done = env.step(nb, a)
                self.assertTrue(done)
                self.assertEqual(r, LAVA_REWARD)
                return
        self.fail("lava cell has no passable neighbour")


class PlannerTests(unittest.TestCase):
    def test_reactive_dies_in_lava_gap(self):
        ep = run_episode(get_map("lava_gap"), ReactivePlanner(), map_name="lava_gap")
        self.assertEqual(ep.outcome, "lava")

    def test_lookahead_solves_every_map(self):
        for name in MAPS:
            with self.subTest(map=name):
                ep = run_episode(get_map(name), LookaheadPlanner(), map_name=name)
                self.assertEqual(ep.outcome, "goal")

    def test_lookahead_is_optimal_on_lava_gap(self):
        # BFS optimum for lava_gap is 8 steps
        ep = run_episode(get_map("lava_gap"), LookaheadPlanner(), map_name="lava_gap")
        self.assertEqual(ep.steps, 8)

    def test_rollout_beats_reactive_on_hazard_detour(self):
        env = get_map("lava_gap")
        reactive = run_episode(env, ReactivePlanner(), map_name="lava_gap")
        rollout = run_episode(env, RolloutPlanner(), map_name="lava_gap")
        self.assertEqual(reactive.outcome, "lava")
        self.assertEqual(rollout.outcome, "goal")  # imagination avoids the lava

    def test_rollout_solves_open_room(self):
        ep = run_episode(get_map("open"), RolloutPlanner(), map_name="open")
        self.assertEqual(ep.outcome, "goal")

    def test_rollout_is_deterministic(self):
        env = get_map("lava_gap")
        a = run_episode(env, RolloutPlanner(seed="z"), map_name="lava_gap")
        b = run_episode(env, RolloutPlanner(seed="z"), map_name="lava_gap")
        self.assertEqual(a.trajectory, b.trajectory)


if __name__ == "__main__":
    unittest.main()
