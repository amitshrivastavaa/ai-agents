import unittest

from labs.speculative.corpus import CORPUS
from labs.speculative.ngram import NgramModel, tokenize
from labs.speculative.speculative import speculative_decode, target_greedy


class TestNgram(unittest.TestCase):
    def setUp(self):
        self.model = NgramModel(order=4).train(CORPUS)

    def test_tokenize_lowercases_and_splits_punct(self):
        self.assertEqual(tokenize("A good Agent."), ["a", "good", "agent", "."])

    def test_greedy_is_deterministic(self):
        ctx = tokenize("a good agent")
        self.assertEqual(self.model.greedy_next(ctx), self.model.greedy_next(ctx))

    def test_greedy_backs_off_to_shorter_context(self):
        # An unseen 3-word context still yields a token via back-off, never crashes.
        tok = self.model.greedy_next(["zzz", "yyy", "qqq"])
        self.assertIn(tok, self.model.unigram)

    def test_generate_length(self):
        out = self.model.generate(tokenize("a language model"), 12)
        self.assertEqual(len(out), 3 + 12)


class TestSpeculative(unittest.TestCase):
    def setUp(self):
        self.draft = NgramModel(order=2).train(CORPUS)
        self.target = NgramModel(order=4).train(CORPUS)
        self.prompt = tokenize("A good agent")
        self.steps = 40

    def test_lossless_for_all_k(self):
        """Speculative output must equal pure target greedy output, for every k."""
        base, _ = target_greedy(self.target, self.prompt, self.steps)
        for k in (1, 2, 3, 4, 6, 8):
            res = speculative_decode(self.draft, self.target, self.prompt,
                                     self.steps, k=k)
            self.assertEqual(res.tokens, base, f"mismatch at k={k}")
            self.assertEqual(len(res.tokens), len(self.prompt) + self.steps)

    def test_speedup_above_one(self):
        res = speculative_decode(self.draft, self.target, self.prompt,
                                 self.steps, k=4)
        self.assertLess(res.target_calls, self.steps)
        self.assertGreater(res.speedup, 1.0)

    def test_acceptance_rate_in_range(self):
        res = speculative_decode(self.draft, self.target, self.prompt,
                                 self.steps, k=4)
        self.assertTrue(0.0 <= res.acceptance_rate <= 4.0)
        self.assertEqual(len(res.accepted_per_round), res.target_calls)

    def test_deterministic(self):
        a = speculative_decode(self.draft, self.target, self.prompt, self.steps, k=4)
        b = speculative_decode(self.draft, self.target, self.prompt, self.steps, k=4)
        self.assertEqual(a.tokens, b.tokens)
        self.assertEqual(a.target_calls, b.target_calls)

    def test_k1_matches_target_calls_to_steps(self):
        # With k=1 the draft proposes a single token; a miss still advances by the
        # correction, so we never exceed `steps` target calls.
        res = speculative_decode(self.draft, self.target, self.prompt, self.steps, k=1)
        self.assertLessEqual(res.target_calls, self.steps)


if __name__ == "__main__":
    unittest.main()
