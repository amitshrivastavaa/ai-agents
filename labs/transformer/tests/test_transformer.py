import unittest

from labs.transformer.block import (TransformerBlock, attention, layernorm,
                                    linear, softmax, multihead)
from labs.transformer import induction as I
from labs.transformer.tasks import repeat_pattern, induction_accuracy


class TestBlockParts(unittest.TestCase):
    def test_softmax_distribution(self):
        p = softmax([1.0, 2.0, 3.0])
        self.assertAlmostEqual(sum(p), 1.0)
        self.assertTrue(all(x > 0 for x in p))

    def test_layernorm_normalizes(self):
        out = layernorm([3.0, 1.0, 4.0, 1.0, 5.0, 9.0])
        n = len(out)
        self.assertAlmostEqual(sum(out) / n, 0.0, places=9)
        self.assertAlmostEqual(sum(v * v for v in out) / n, 1.0, places=4)

    def test_attention_weights_are_causal_and_normalized(self):
        Q = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
        _, W = attention(Q, Q, Q, causal=True)
        for i, row in enumerate(W):
            self.assertAlmostEqual(sum(row), 1.0)
            for j in range(i + 1, len(row)):
                self.assertEqual(row[j], 0.0)        # no attention to the future

    def test_multihead_runs_and_shapes(self):
        d = 8
        X = [[(i + d_) / 10.0 for d_ in range(d)] for i in range(4)]
        I_ = [[1.0 if a == b else 0.0 for b in range(d)] for a in range(d)]
        out = multihead(X, I_, I_, I_, I_, n_heads=2, causal=True)
        self.assertEqual(len(out), 4)
        self.assertEqual(len(out[0]), d)


class TestBlock(unittest.TestCase):
    def setUp(self):
        self.blk = TransformerBlock(d_model=16, n_heads=4, d_ff=32, seed="t")
        self.X = [[((i * 5 + d * 2) % 7 - 3) / 3.0 for d in range(16)] for i in range(5)]

    def test_output_shape(self):
        Y = self.blk.forward(self.X)
        self.assertEqual(len(Y), 5)
        self.assertEqual(len(Y[0]), 16)

    def test_causal_no_future_leak(self):
        Y = self.blk.forward(self.X)
        X2 = [r[:] for r in self.X]
        X2[-1] = [v + 2.0 for v in X2[-1]]
        Y2 = self.blk.forward(X2)
        leak = max(abs(Y[i][d] - Y2[i][d]) for i in range(4) for d in range(16))
        self.assertLess(leak, 1e-9)
        changed = max(abs(Y[4][d] - Y2[4][d]) for d in range(16))
        self.assertGreater(changed, 0.0)

    def test_residual_identity_when_sublayers_zeroed(self):
        self.blk.Wo = [[0.0] * 16 for _ in range(16)]
        self.blk.W2 = [[0.0] * 32 for _ in range(16)]
        Y = self.blk.forward(self.X)
        diff = max(abs(Y[i][d] - self.X[i][d]) for i in range(5) for d in range(16))
        self.assertLess(diff, 1e-9)

    def test_deterministic(self):
        a = TransformerBlock(seed="z").forward(self.X)
        b = TransformerBlock(seed="z").forward(self.X)
        self.assertEqual(a, b)


class TestInduction(unittest.TestCase):
    def test_clean_examples(self):
        self.assertEqual(I.next_token("abcabca"), "b")
        self.assertEqual(I.next_token("xyzwxyzw"), "x")
        self.assertEqual(I.next_token("1 2 3 1 2 3 1"), "2")

    def test_two_layer_solves_repeats(self):
        for seed in range(12):
            seq = repeat_pattern(8, 4, 3, seed=seed)
            self.assertEqual(induction_accuracy(seq, I.predict, block=4), 1.0)

    def test_one_layer_cannot_induct(self):
        accs = [induction_accuracy(repeat_pattern(8, 4, 3, seed=s),
                                   I.one_layer_predict, block=4) for s in range(12)]
        self.assertEqual(max(accs), 0.0)              # the ablation fully fails

    def test_prev_token_head_marks_predecessor(self):
        # PREV[i] should be (near) the one-hot of token i-1.
        seq, vocab, _ = I.encode("abcd")
        prev = I._prev_token_head(seq, len(vocab), strength=12.0)
        # position 3's previous token is 'c' (index 2)
        self.assertEqual(max(range(len(vocab)), key=lambda v: prev[3][v]), 2)

    def test_deterministic(self):
        self.assertEqual(I.predict("abcabca"), I.predict("abcabca"))


if __name__ == "__main__":
    unittest.main()
