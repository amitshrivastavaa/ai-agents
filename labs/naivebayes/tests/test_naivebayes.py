import unittest
from collections import Counter

from labs.naivebayes.nb import MultinomialNB
from labs.naivebayes.data import corpus, split, tokenize, POS, NEG


def _acc(yh, y):
    return sum(1 for a, b in zip(yh, y) if a == b) / len(y)


class TestNaiveBayes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        docs, labels = corpus(n=500, seed="t")
        cls.Xtr, cls.ytr, cls.Xte, cls.yte = split(docs, labels, seed="t")
        cls.nb = MultinomialNB(alpha=1.0).fit(cls.Xtr, cls.ytr)

    def test_accuracy_beats_baseline(self):
        acc = _acc(self.nb.predict(self.Xte), self.yte)
        maj = Counter(self.ytr).most_common(1)[0][0]
        self.assertGreater(acc, 0.85)
        self.assertGreater(acc, _acc([maj] * len(self.yte), self.yte) + 0.2)

    def test_top_words_are_class_signal(self):
        pos = set(self.nb.top_words("pos", 10))
        neg = set(self.nb.top_words("neg", 10))
        self.assertGreaterEqual(len(pos & set(POS)), 6)     # mostly real pos words
        self.assertGreaterEqual(len(neg & set(NEG)), 6)
        self.assertEqual(pos & neg, set())                  # disjoint

    def test_smoothing_handles_unseen_words(self):
        pred = self.nb.predict([["zzz", "qqq", "neverseen"]])
        self.assertIn(pred[0], self.nb.classes)             # no crash, valid class
        s = self.nb.score(["totallynovel"])
        self.assertTrue(all(v == v and v != float("-inf") for v in s.values()))

    def test_signal_words_swing_prediction(self):
        self.assertEqual(self.nb.predict([["great", "excellent", "love", "best"]]), ["pos"])
        self.assertEqual(self.nb.predict([["terrible", "awful", "worst", "boring"]]), ["neg"])

    def test_more_data_helps(self):
        def acc_with(ntr):
            d, l = corpus(n=ntr + 150, seed="m")
            xt, yt, xv, yv = split(d, l, frac=ntr / (ntr + 150), seed="m")
            return _acc(MultinomialNB().fit(xt, yt).predict(xv), yv)
        self.assertGreaterEqual(acc_with(300), acc_with(30) - 0.02)

    def test_tokenize(self):
        self.assertEqual(tokenize("Great, AWFUL film!"), ["great", "awful", "film"])

    def test_deterministic(self):
        nb2 = MultinomialNB(alpha=1.0).fit(self.Xtr, self.ytr)
        self.assertEqual(nb2.predict(self.Xte), self.nb.predict(self.Xte))


if __name__ == "__main__":
    unittest.main()
