"""Tests for qlearning — offline, stdlib only.

    python -m unittest labs.qlearning.tests.test_qlearning -v
"""
from __future__ import annotations

import unittest

from labs.qlearning.agent import QLearningAgent, evaluate, train
from labs.qlearning.dp import value_iteration
from labs.qlearning.gridworld import GOAL_REWARD, PIT_REWARD, get_map


class GridWorldTests(unittest.TestCase):
    def test_goal_and_pit_terminate(self):
        env = get_map("cliff")
        # neighbour above the goal stepping down onto it
        gx, gy = env.goal
        s2, r, done = env.step((gx, gy - 1), "down")
        self.assertEqual((s2, r, done), (env.goal, GOAL_REWARD, True))

    def test_wall_bump_keeps_position(self):
        env = get_map("maze")
        # from start (0,0), moving up leaves the grid → stay put, pay step cost
        s2, r, done = env.step(env.start, "up")
        self.assertEqual(s2, env.start)
        self.assertFalse(done)
        self.assertEqual(r, -1.0)

    def test_pit_is_terminal_and_negative(self):
        env = get_map("cliff")
        pit = next(iter(env.pits))
        s2, r, done = env.step((pit[0], pit[1] - 1), "down")
        self.assertTrue(done)
        self.assertEqual(r, PIT_REWARD)


class AgentTests(unittest.TestCase):
    def test_update_moves_q_toward_target(self):
        a = QLearningAgent(alpha=0.5, gamma=0.0)
        a.update((0, 0), 1, 10.0, (1, 0), True)        # terminal target = 10
        self.assertAlmostEqual(a.q((0, 0))[1], 5.0)    # halfway with alpha 0.5

    def test_learns_to_reach_goal(self):
        for name in ("cliff", "maze", "rooms"):
            env = get_map(name)
            res = train(env, episodes=500, seed="t")
            reached, steps, _, _ = evaluate(env, res.agent)
            with self.subTest(map=name):
                self.assertTrue(reached, f"did not reach goal on {name}")

    def test_learning_curve_improves(self):
        res = train(get_map("cliff"), episodes=500, seed="t")
        early = sum(res.rewards[:30]) / 30
        late = sum(res.rewards[-30:]) / 30
        self.assertGreater(late, early + 50)           # huge improvement on the cliff

    def test_cliff_solution_is_near_optimal(self):
        env = get_map("cliff")
        res = train(env, episodes=600, seed="t")
        _, steps, _, _ = evaluate(env, res.agent)
        self.assertLessEqual(steps, 11)                # optimal is 9; allow slack

    def test_deterministic(self):
        a = train(get_map("maze"), episodes=100, seed="z").rewards
        b = train(get_map("maze"), episodes=100, seed="z").rewards
        self.assertEqual(a, b)


class ValueIterationTests(unittest.TestCase):
    def test_converges_and_policy_reaches_goal(self):
        env = get_map("maze")
        V, policy = value_iteration(env)
        self.assertIn(env.start, V)
        # follow the optimal policy from the start → should hit the goal
        from labs.qlearning.gridworld import ACTIONS
        s, seen = env.start, set()
        for _ in range(100):
            if s == env.goal:
                break
            self.assertNotIn(s, seen)                  # no cycles in an optimal policy
            seen.add(s)
            s, _, done = env.step(s, ACTIONS[policy[s]])
        self.assertEqual(s, env.goal)


if __name__ == "__main__":
    unittest.main()
