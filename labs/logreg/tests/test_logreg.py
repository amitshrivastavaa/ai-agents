import unittest

from labs.logreg.logreg import LogisticRegression, sigmoid
from labs.logreg.data import linear, moons, split


def _acc(yh, y):
    return sum(1 for a, b in zip(yh, y) if a == b) / len(y)


class TestLogReg(unittest.TestCase):
    def setUp(self):
        self.X, self.y = linear(n=400, gap=1.4, seed="t")
        self.Xtr, self.ytr, self.Xte, self.yte = split(self.X, self.y, seed="t")
        self.m = LogisticRegression(lr=0.5, epochs=300).fit(self.Xtr, self.ytr)

    def test_sigmoid(self):
        self.assertAlmostEqual(sigmoid(0.0), 0.5)
        self.assertGreater(sigmoid(10), 0.99)
        self.assertLess(sigmoid(-10), 0.01)

    def test_separates_linear_data(self):
        self.assertGreater(_acc(self.m.predict(self.Xte), self.yte), 0.9)

    def test_loss_is_monotone_convex(self):
        lh = self.m.loss_history
        for a, b in zip(lh, lh[1:]):
            self.assertLessEqual(b, a + 1e-9)        # convex + GD → never rises
        self.assertLess(lh[-1], lh[0] / 2)           # and it actually descends

    def test_probabilities_in_range_and_calibrated(self):
        probs = self.m.predict_proba(self.Xte)
        self.assertTrue(all(0.0 <= p <= 1.0 for p in probs))
        confident_pos = [t for p, t in zip(probs, self.yte) if p > 0.8]
        if confident_pos:
            self.assertGreater(sum(confident_pos) / len(confident_pos), 0.8)

    def test_linear_underfits_moons(self):
        Xm, ym = moons(n=400, seed="t")
        xtr, ytr, xte, yte = split(Xm, ym, seed="t")
        acc = _acc(LogisticRegression(lr=0.5, epochs=300).fit(xtr, ytr).predict(xte), yte)
        self.assertLess(acc, 0.92)                   # one line can't carve moons
        self.assertGreater(acc, 0.6)                 # but beats chance

    def test_l2_shrinks_weights(self):
        norm = lambda w: sum(v * v for v in w) ** 0.5
        w0 = LogisticRegression(lr=0.5, epochs=300, l2=0.0).fit(self.Xtr, self.ytr).w
        w1 = LogisticRegression(lr=0.5, epochs=300, l2=0.5).fit(self.Xtr, self.ytr).w
        self.assertLess(norm(w1), norm(w0))

    def test_deterministic(self):
        a = LogisticRegression(lr=0.5, epochs=100).fit(self.Xtr, self.ytr).w
        b = LogisticRegression(lr=0.5, epochs=100).fit(self.Xtr, self.ytr).w
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
