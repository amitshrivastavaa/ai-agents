import unittest

from labs.bandits.bandit import BernoulliBandit
from labs.bandits.policies import Greedy, EpsilonGreedy, UCB1, Thompson, Random
from labs.bandits.run import simulate, evaluate

PROBS = [0.2, 0.5, 0.75, 0.55, 0.3]


class TestBandit(unittest.TestCase):
    def test_pull_is_binary_and_deterministic(self):
        b1 = BernoulliBandit(PROBS, seed="t")
        b2 = BernoulliBandit(PROBS, seed="t")
        pulls1 = [b1.pull(2) for _ in range(50)]
        pulls2 = [b2.pull(2) for _ in range(50)]
        self.assertTrue(all(r in (0.0, 1.0) for r in pulls1))
        self.assertEqual(pulls1, pulls2)          # same seed → same reward stream
        self.assertGreater(sum(pulls1), 0)        # p=0.75 → mostly wins

    def test_best_arm_and_gap(self):
        b = BernoulliBandit(PROBS)
        self.assertEqual(b.best_arm, 2)
        self.assertAlmostEqual(b.best_prob, 0.75)
        self.assertAlmostEqual(b.gap(0), 0.55)
        self.assertAlmostEqual(b.gap(2), 0.0)

    def test_empirical_mean_converges(self):
        b = BernoulliBandit([0.0, 0.7], seed="m")
        pol = Greedy(2)
        for _ in range(2000):
            pol.update(1, b.pull(1))
        self.assertAlmostEqual(pol.values[1], 0.7, delta=0.05)


class TestPolicies(unittest.TestCase):
    def test_ucb1_pulls_each_arm_once_first(self):
        pol = UCB1(len(PROBS))
        firsts = []
        for t in range(1, len(PROBS) + 1):
            arm = pol.select(t)
            firsts.append(arm)
            pol.update(arm, 0.0)
        self.assertEqual(sorted(firsts), list(range(len(PROBS))))

    def test_thompson_updates_posterior(self):
        pol = Thompson(2)
        pol.update(0, 1.0)
        pol.update(1, 0.0)
        self.assertEqual(pol.alpha[0], 2.0)
        self.assertEqual(pol.beta[1], 2.0)

    def test_argmax_breaks_ties_within_arms(self):
        pol = Random(3)
        self.assertIn(pol._argmax([1.0, 1.0, 1.0]), (0, 1, 2))
        self.assertEqual(pol._argmax([0.1, 0.9, 0.2]), 1)


class TestRegret(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.avg, cls.pct = evaluate(PROBS, horizon=600, runs=20)

    def _ratio(self, name):
        c = self.avg[name]
        first = c[len(c) // 2]
        second = c[-1] - c[len(c) // 2]
        return second / first

    def test_dumb_policies_are_linear(self):
        # regret keeps accruing at the same rate → second half ≈ first half.
        self.assertGreater(self._ratio("greedy"), 0.85)
        self.assertGreater(self._ratio("random"), 0.85)

    def test_thompson_is_sublinear(self):
        # a smart policy explores less over time → second half << first half.
        self.assertLess(self._ratio("Thompson"), 0.5)

    def test_learning_beats_not_learning(self):
        # every learning policy pulls the best arm far more than the dumb ones.
        learners = min(self.pct[n] for n in ("ε-greedy(.1)", "UCB1", "Thompson"))
        dumb = max(self.pct[n] for n in ("greedy", "random"))
        self.assertGreater(learners, dumb + 0.2)

    def test_thompson_is_best(self):
        final = {n: self.avg[n][-1] for n in self.avg}
        self.assertEqual(min(final, key=final.get), "Thompson")
        self.assertLess(final["Thompson"], final["greedy"] / 3)

    def test_optimal_pull_rates(self):
        self.assertGreater(self.pct["Thompson"], 0.8)
        self.assertLess(self.pct["random"], 0.3)        # ≈ 1/K = 0.2

    def test_deterministic(self):
        avg2, pct2 = evaluate(PROBS, horizon=600, runs=20)
        self.assertEqual(self.avg["Thompson"], avg2["Thompson"])
        self.assertEqual(self.pct, pct2)


if __name__ == "__main__":
    unittest.main()
