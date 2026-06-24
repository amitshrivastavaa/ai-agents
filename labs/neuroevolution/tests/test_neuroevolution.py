"""Tests for neuroevolution — offline, stdlib only.

    python -m unittest labs.neuroevolution.tests.test_neuroevolution -v
"""
from __future__ import annotations

import unittest

from labs.neuroevolution.cartpole import CartPole, THETA_LIMIT
from labs.neuroevolution.evolve import evolve, fitness
from labs.neuroevolution.policy import Policy, param_count


class CartPoleTests(unittest.TestCase):
    def test_reset_is_small_and_seeded(self):
        s = CartPole().reset(seed="t")
        self.assertTrue(all(abs(v) < 0.06 for v in s))

    def test_step_returns_shape_and_terminates(self):
        env = CartPole(max_steps=50)
        env.reset(seed="t")
        steps, done = 0, False
        while not done and steps < 1000:
            state, reward, done = env.step(1)   # always push right → pole falls
            self.assertEqual(len(state), 4)
            self.assertEqual(reward, 1.0)
            steps += 1
        self.assertTrue(done)
        self.assertLessEqual(env.steps, 50)

    def test_always_one_direction_fails_fast(self):
        env = CartPole()
        steps = env.rollout(_Const(1))
        self.assertLess(steps, 200)             # constant push can't balance


class _Const:
    def __init__(self, a): self.a = a
    def act(self, state): return self.a


class PolicyTests(unittest.TestCase):
    def test_param_count(self):
        self.assertEqual(param_count(6), 6 * 4 + 6 + 6 + 1)
        self.assertEqual(len(Policy.random(8, seed="t").params), param_count(8))

    def test_forward_deterministic_and_act_binary(self):
        pol = Policy.random(6, seed="t")
        s = [0.1, 0.0, 0.05, 0.0]
        self.assertEqual(pol.forward(s), pol.forward(s))
        self.assertIn(pol.act(s), (0, 1))


class EvolveTests(unittest.TestCase):
    def test_evolution_learns_to_balance(self):
        res = evolve(population=16, generations=12, seed="t")
        self.assertGreaterEqual(res.best_fitness, 200)        # random baseline is ~10
        self.assertGreater(res.best_fitness, res.history[0])

    def test_best_policy_generalizes(self):
        res = evolve(population=16, generations=12, seed="t")
        fresh = sum(CartPole().rollout(res.best_policy, seed=f"u{i}") for i in range(5)) / 5
        self.assertGreaterEqual(fresh, 150)                   # holds on unseen starts

    def test_beats_random_baseline(self):
        rnd = Policy.random(6, seed="r")
        base = sum(CartPole().rollout(rnd, seed=f"b{i}") for i in range(5)) / 5
        res = evolve(population=16, generations=12, seed="t")
        self.assertGreater(res.best_fitness, base * 3)

    def test_deterministic(self):
        a = evolve(population=12, generations=6, seed="z").best_fitness
        b = evolve(population=12, generations=6, seed="z").best_fitness
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
