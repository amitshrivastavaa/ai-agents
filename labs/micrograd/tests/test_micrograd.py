"""Tests for micrograd — offline, stdlib only.

    python -m unittest labs.micrograd.tests.test_micrograd -v
"""
from __future__ import annotations

import math
import unittest

from labs.micrograd.engine import Value
from labs.micrograd.nn import MLP
from labs.micrograd.train import get_dataset, train


class EngineTests(unittest.TestCase):
    def test_forward_values(self):
        a, b = Value(2.0), Value(-3.0)
        self.assertEqual((a * b + Value(1.0)).data, -5.0)
        self.assertAlmostEqual(Value(0.0).tanh().data, 0.0)
        self.assertEqual(Value(-2.0).relu().data, 0.0)
        self.assertAlmostEqual(Value(1.0).exp().data, math.e)

    def test_backward_matches_numerical(self):
        a, b, c = Value(-1.5), Value(2.0), Value(0.7)
        f = (a * b + c.tanh()) * b - a ** 2
        f.backward()

        def fa(x):
            return ((x * 2.0) + math.tanh(0.7)) * 2.0 - x ** 2

        def fb(x):
            return ((-1.5 * x) + math.tanh(0.7)) * x - (-1.5) ** 2

        num_a = (fa(-1.5 + 1e-6) - fa(-1.5 - 1e-6)) / 2e-6
        num_b = (fb(2.0 + 1e-6) - fb(2.0 - 1e-6)) / 2e-6
        self.assertAlmostEqual(a.grad, num_a, places=4)
        self.assertAlmostEqual(b.grad, num_b, places=4)

    def test_gradient_accumulates_on_reuse(self):
        x = Value(3.0)
        y = x + x          # dy/dx = 2
        y.backward()
        self.assertAlmostEqual(x.grad, 2.0)

    def test_division_and_power(self):
        self.assertAlmostEqual((Value(6.0) / Value(2.0)).data, 3.0)
        self.assertAlmostEqual((Value(2.0) ** 3).data, 8.0)


class NetTests(unittest.TestCase):
    def test_mlp_shape_and_param_count(self):
        net = MLP(2, [4, 1], seed="t")
        out = net([Value(0.5), Value(-0.5)])
        self.assertIsInstance(out, Value)
        # layer1: 4*(2+1)=12, layer2: 1*(4+1)=5 → 17 params
        self.assertEqual(len(net.parameters()), 17)

    def test_zero_grad(self):
        net = MLP(2, [3, 1], seed="t")
        net([Value(1.0), Value(1.0)]).backward()
        net.zero_grad()
        self.assertTrue(all(p.grad == 0.0 for p in net.parameters()))


class TrainTests(unittest.TestCase):
    def test_learns_xor(self):
        res = train(get_dataset("xor"), hidden=(8,), epochs=120, seed="t")
        self.assertEqual(res.accuracy, 1.0)             # solves the canonical nonlinear task
        self.assertLess(res.final_loss, res.loss_history[0])

    def test_loss_decreases(self):
        res = train(get_dataset("xor"), hidden=(8,), epochs=60, seed="t")
        self.assertLess(res.final_loss, res.loss_history[0] * 0.5)

    def test_fits_regression(self):
        res = train(get_dataset("sine"), hidden=(10,), epochs=100, seed="t")
        self.assertLess(res.final_loss, 0.1)            # MSE well below the variance of sin

    def test_separates_a_blob_cluster(self):
        res = train(get_dataset("blobs"), hidden=(6,), epochs=40, seed="t")
        self.assertGreaterEqual(res.accuracy, 0.9)

    def test_deterministic(self):
        a = train(get_dataset("xor"), epochs=20, seed="z").loss_history
        b = train(get_dataset("xor"), epochs=20, seed="z").loss_history
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
