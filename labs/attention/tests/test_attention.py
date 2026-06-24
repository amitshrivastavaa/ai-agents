"""Tests for attention — offline, stdlib only.

    python -m unittest labs.attention.tests.test_attention -v
"""
from __future__ import annotations

import unittest

from labs.attention.attention import attention, self_attention, softmax
from labs.attention.induction import induction_head, predict_next


class AttentionTests(unittest.TestCase):
    def test_softmax_is_a_distribution(self):
        w = softmax([1.0, 2.0, 3.0])
        self.assertAlmostEqual(sum(w), 1.0)
        self.assertLess(w[0], w[2])                    # bigger score → bigger weight

    def test_weights_sum_to_one(self):
        Q = [[1.0, 0.0]]
        K = [[1.0, 0.0], [0.0, 1.0], [1.0, 0.0]]
        V = [[1.0], [2.0], [3.0]]
        _, weights = attention(Q, K, V, scale=8.0)
        self.assertAlmostEqual(sum(weights[0]), 1.0)

    def test_retrieves_matching_value(self):
        # query matches key 1 strongly → output ≈ value 1
        Q = [[0.0, 1.0]]
        K = [[1.0, 0.0], [0.0, 1.0]]
        V = [[10.0], [20.0]]
        out, _ = attention(Q, K, V, scale=12.0)
        self.assertAlmostEqual(out[0][0], 20.0, places=2)

    def test_self_attention_identical_tokens_attend_together(self):
        X = [[1.0, 0.0], [0.0, 1.0], [1.0, 0.0]]       # tokens 0, 1, 0
        _, A = self_attention(X, scale=10.0)
        # token 0 splits attention between positions 0 and 2 (both token 0)
        self.assertAlmostEqual(A[0][0], A[0][2], places=2)
        self.assertGreater(A[0][0], A[0][1])
        self.assertAlmostEqual(A[1][1], 1.0, places=2)  # unique token attends to itself

    def test_higher_scale_sharpens(self):
        Q = [[1.0, 0.0]]
        K = [[1.0, 0.0], [0.5, 0.5]]
        V = [[1.0], [0.0]]
        soft, _ = attention(Q, K, V, scale=1.0)
        sharp, _ = attention(Q, K, V, scale=20.0)
        self.assertGreater(sharp[0][0], soft[0][0])    # sharper → closer to value 0


class InductionTests(unittest.TestCase):
    def test_continues_repeating_patterns(self):
        cases = [
            (["A", "B", "C", "A", "B", "C", "A"], "B"),
            (["the", "cat", "sat", "the", "cat"], "sat"),
            (["red", "green", "blue", "red", "green", "blue", "red", "green"], "blue"),
            ([1, 2, 3, 1, 2, 3, 1, 2], 3),
        ]
        for seq, expected in cases:
            with self.subTest(seq=seq):
                self.assertEqual(predict_next(seq), expected)

    def test_attends_to_a_matching_position(self):
        seq = ["A", "B", "C", "A", "B", "C", "A"]
        _, weights, _ = induction_head(seq)
        top = max(range(len(weights)), key=lambda i: weights[i])
        self.assertEqual(seq[top], "A")                # attended to an earlier 'A'

    def test_needs_two_tokens(self):
        with self.assertRaises(ValueError):
            induction_head(["A"])

    def test_deterministic(self):
        seq = ["x", "y", "z", "x", "y"]
        self.assertEqual(predict_next(seq), predict_next(seq))


if __name__ == "__main__":
    unittest.main()
