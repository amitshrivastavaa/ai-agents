import unittest

from labs.boosting.gbm import GradientBoosting, mse
from labs.boosting.regtree import RegTree
from labs.boosting.data import make, split


class TestRegTree(unittest.TestCase):
    def test_constant_target(self):
        t = RegTree(max_depth=3).fit([[0.0], [1.0], [2.0], [3.0]], [5.0] * 4)
        self.assertEqual(t.predict([[9.0]]), [5.0])

    def test_reduces_variance(self):
        X = [[x] for x in range(20)]
        y = [0.0] * 10 + [10.0] * 10                 # a clean step
        t = RegTree(max_depth=1).fit(X, y)
        self.assertLess(mse(t.predict(X), y), 1.0)   # one split captures it


class TestBoosting(unittest.TestCase):
    def setUp(self):
        self.X, self.y, _ = make("sine", n=240, noise=0.08, seed="t")
        self.Xtr, self.ytr, self.Xte, self.yte = split(self.X, self.y, seed="t")

    def test_train_loss_monotone(self):
        """Each tree is a gradient step → training loss never goes up."""
        gb = GradientBoosting(n_estimators=80, learning_rate=0.1, max_depth=2).fit(
            self.Xtr, self.ytr)
        tl = gb.train_loss
        for a, b in zip(tl, tl[1:]):
            self.assertLessEqual(b, a + 1e-12)

    def test_beats_single_weak_learner(self):
        stump = RegTree(max_depth=2).fit(self.Xtr, self.ytr)
        gb = GradientBoosting(n_estimators=150, learning_rate=0.1, max_depth=2).fit(
            self.Xtr, self.ytr)
        single = mse(stump.predict(self.Xte), self.yte)
        boosted = mse(gb.predict(self.Xte), self.yte)
        self.assertLess(boosted, single / 3)         # dramatically better

    def test_more_trees_lower_train_error(self):
        gb = GradientBoosting(n_estimators=100, learning_rate=0.1, max_depth=2).fit(
            self.Xtr, self.ytr)
        self.assertLess(gb.train_loss[-1], gb.train_loss[4])

    def test_fits_noisy_function_well(self):
        gb = GradientBoosting(n_estimators=150, learning_rate=0.1, max_depth=2).fit(
            self.Xtr, self.ytr)
        self.assertLess(mse(gb.predict(self.Xte), self.yte), 0.05)   # ≈ noise floor

    def test_staged_predict(self):
        gb = GradientBoosting(n_estimators=20, learning_rate=0.1, max_depth=2).fit(
            self.Xtr, self.ytr)
        staged = gb.staged_predict(self.Xte, [1, 10, 20])
        self.assertEqual(set(staged), {1, 10, 20})
        # later stages fit the training trend better → lower test error here
        self.assertLess(mse(staged[20], self.yte), mse(staged[1], self.yte))

    def test_deterministic(self):
        a = GradientBoosting(30, 0.1, 2).fit(self.Xtr, self.ytr).predict(self.Xte)
        b = GradientBoosting(30, 0.1, 2).fit(self.Xtr, self.ytr).predict(self.Xte)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
