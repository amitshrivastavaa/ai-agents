import statistics
import unittest

from labs.forest.forest import RandomForest
from labs.tree.tree import DecisionTree
from labs.tree.data import moons, blobs, xor, train_test_split
from labs.tree.metrics import accuracy


class TestForest(unittest.TestCase):
    def test_separable_blobs_perfect(self):
        X, y = blobs(n=300, seed="t")
        f = RandomForest(n_trees=15, seed="t").fit(X, y)
        self.assertGreater(accuracy(f.predict(X), y), 0.97)

    def test_beats_single_tree_on_average(self):
        """The ensemble's whole point: lower variance → better test accuracy."""
        f_acc, t_acc = [], []
        for s in range(12):
            X, y = moons(n=400, seed=("m", s))
            Xtr, ytr, Xte, yte = train_test_split(X, y, seed=("m", s))
            f = RandomForest(n_trees=25, max_depth=8, seed=s).fit(Xtr, ytr)
            t = DecisionTree(max_depth=8).fit(Xtr, ytr)
            f_acc.append(accuracy(f.predict(Xte), yte))
            t_acc.append(accuracy(t.predict(Xte), yte))
        self.assertGreater(sum(f_acc) / len(f_acc), sum(t_acc) / len(t_acc))

    def test_more_trees_reduce_variance(self):
        def std_over_splits(nt):
            accs = []
            for s in range(10):
                X, y = moons(n=400, seed=("v", s))
                Xtr, ytr, Xte, yte = train_test_split(X, y, seed=("v", s))
                f = RandomForest(n_trees=nt, max_depth=8, seed=("v", s)).fit(Xtr, ytr)
                accs.append(accuracy(f.predict(Xte), yte))
            return statistics.pstdev(accs)
        self.assertLess(std_over_splits(25), std_over_splits(1))

    def test_oob_tracks_test_accuracy(self):
        X, y = moons(n=400, seed="o")
        Xtr, ytr, Xte, yte = train_test_split(X, y, seed="o")
        f = RandomForest(n_trees=30, max_depth=8, seed="o").fit(Xtr, ytr)
        self.assertLess(abs(f.oob_score(Xtr, ytr) - accuracy(f.predict(Xte), yte)), 0.07)

    def test_solves_xor(self):
        X, y = xor(n=400, seed="x")
        Xtr, ytr, Xte, yte = train_test_split(X, y, seed="x")
        f = RandomForest(n_trees=25, max_depth=8, seed="x").fit(Xtr, ytr)
        self.assertGreater(accuracy(f.predict(Xte), yte), 0.9)

    def test_predict_length(self):
        X, y = blobs(n=100, seed="t")
        self.assertEqual(len(RandomForest(n_trees=5, seed="t").fit(X, y).predict(X)), 100)

    def test_deterministic(self):
        X, y = moons(n=200, seed="z")
        a = RandomForest(n_trees=10, seed="z").fit(X, y).predict(X)
        b = RandomForest(n_trees=10, seed="z").fit(X, y).predict(X)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
