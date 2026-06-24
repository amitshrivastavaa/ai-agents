import unittest

from labs.hmm.model import HMM, logsumexp
from labs.hmm.casino import casino_hmm, sample, accuracy
from labs.hmm import brute


class TestModel(unittest.TestCase):
    def setUp(self):
        self.m = casino_hmm()

    def test_viterbi_matches_brute_force(self):
        """The DP path equals the exhaustively-searched best path — exactly."""
        for obs in (list("16326"), list("66666"), list("12345"), list("6612366")):
            vpath, vlp = self.m.viterbi(obs)
            bpath, blp = brute.best_path(self.m, obs)
            self.assertEqual(vpath, bpath)
            self.assertAlmostEqual(vlp, blp, places=9)

    def test_forward_matches_brute_force(self):
        for obs in (list("16326"), list("6666"), list("135246")):
            self.assertAlmostEqual(self.m.forward(obs),
                                   brute.total_logprob(self.m, obs), places=9)

    def test_posteriors_sum_to_one(self):
        post = self.m.forward_backward(list("66135266"))
        for row in post:
            self.assertAlmostEqual(sum(row.values()), 1.0, places=9)

    def test_logsumexp(self):
        import math
        self.assertAlmostEqual(logsumexp([0.0, 0.0]), math.log(2), places=12)
        self.assertEqual(logsumexp([float("-inf"), float("-inf")]), float("-inf"))


class TestCasino(unittest.TestCase):
    def setUp(self):
        self.m = casino_hmm()

    def test_obvious_sequences(self):
        # all sixes → loaded everywhere; a no-six spread → fair everywhere.
        self.assertEqual(self.m.viterbi(list("6666666666"))[0], ["L"] * 10)
        self.assertEqual(self.m.viterbi(list("1234512345"))[0], ["F"] * 10)

    def test_decode_accuracy(self):
        accs = []
        for seed in range(8):
            rolls, hidden = sample(self.m, n=300, seed=seed)
            path, _ = self.m.viterbi(rolls)
            accs.append(accuracy(hidden, path))
        self.assertGreater(sum(accs) / len(accs), 0.7)

    def test_no_underflow_on_long_sequence(self):
        rolls, _ = sample(self.m, n=600, seed="long")
        lp = self.m.forward(rolls)
        self.assertTrue(lp == lp and lp != float("-inf"))   # finite, not NaN

    def test_deterministic(self):
        a = sample(self.m, n=50, seed="z")
        b = sample(self.m, n=50, seed="z")
        self.assertEqual(a, b)
        self.assertEqual(self.m.viterbi(a[0]), self.m.viterbi(b[0]))


if __name__ == "__main__":
    unittest.main()
