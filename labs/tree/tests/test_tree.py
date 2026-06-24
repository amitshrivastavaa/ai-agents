import unittest

from labs.tree.tree import DecisionTree, gini, entropy
from labs.tree.data import blobs, xor, moons, train_test_split
from labs.tree.metrics import accuracy, depth_sweep


class TestImpurity(unittest.TestCase):
    def test_gini(self):
        self.assertEqual(gini([0, 0, 0]), 0.0)
        self.assertAlmostEqual(gini([0, 0, 1, 1]), 0.5)
        self.assertAlmostEqual(gini([0, 1, 2, 3]), 0.75)

    def test_entropy(self):
        self.assertEqual(entropy([1, 1]), 0.0)
        self.assertAlmostEqual(entropy([0, 1]), 1.0)


class TestTree(unittest.TestCase):
    def test_separable_blobs_perfect(self):
        X, y = blobs(n=300, seed="t")
        t = DecisionTree(max_depth=6).fit(X, y)
        self.assertGreater(accuracy(t.predict(X), y), 0.99)

    def test_pure_node_is_single_leaf(self):
        t = DecisionTree(max_depth=5).fit([[0.0], [1.0], [2.0]], [1, 1, 1])
        self.assertEqual(t.n_leaves(), 1)
        self.assertEqual(t.predict([[9.0]]), [1])

    def test_moons_generalizes(self):
        X, y = moons(n=400, seed="t")
        Xtr, ytr, Xte, yte = train_test_split(X, y, seed="t")
        t = DecisionTree(max_depth=8).fit(Xtr, ytr)
        self.assertGreater(accuracy(t.predict(Xte), yte), 0.85)

    def test_deeper_fits_training_better(self):
        X, y = moons(n=300, seed="t")
        Xtr, ytr, Xte, yte = train_test_split(X, y, seed="t")
        accs = [tr for _, tr, _ in depth_sweep(Xtr, ytr, Xte, yte, depths=range(1, 9))]
        for a, b in zip(accs, accs[1:]):
            self.assertGreaterEqual(b, a - 1e-9)        # monotone non-decreasing

    def test_solves_xor_with_depth(self):
        """A linear model gets ~50% on XOR; the tree solves it given depth."""
        X, y = xor(n=400, seed="t")
        Xtr, ytr, Xte, yte = train_test_split(X, y, seed="t")
        shallow = DecisionTree(max_depth=1).fit(Xtr, ytr)
        deep = DecisionTree(max_depth=6).fit(Xtr, ytr)
        self.assertLess(accuracy(shallow.predict(Xte), yte), 0.65)   # ~chance
        self.assertGreater(accuracy(deep.predict(Xte), yte), 0.9)    # solved

    def test_predict_length(self):
        X, y = blobs(n=100, seed="t")
        self.assertEqual(len(DecisionTree().fit(X, y).predict(X)), 100)

    def test_deterministic(self):
        X, y = moons(n=200, seed="z")
        a = DecisionTree(max_depth=6).fit(X, y).predict(X)
        b = DecisionTree(max_depth=6).fit(X, y).predict(X)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
