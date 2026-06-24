"""A random forest — many decorrelated decision trees that vote.

Two sources of randomness turn one high-variance tree into a low-variance
ensemble: **bagging** (each tree trains on a bootstrap resample of the data) and
**feature subsampling** (each split considers only a random subset of features).
The trees overfit in *different* directions, so averaging their votes cancels the
noise — better, more stable test accuracy than any single tree. Plus a free
validation score: each point's **out-of-bag** prediction uses only the trees that
never saw it.

Reuses the lab's `tree.DecisionTree` (now with `max_features`) — a forest is
literally an ensemble of them.
"""
from __future__ import annotations

from .._kernel import rng
from ..tree.tree import DecisionTree


def _majority(votes):
    counts = {}
    for v in votes:
        counts[v] = counts.get(v, 0) + 1
    return max(counts.items(), key=lambda kv: (kv[1], -kv[0]))[0]


class RandomForest:
    def __init__(self, n_trees=25, max_depth=8, max_features="sqrt", seed="rf"):
        self.n_trees = n_trees
        self.max_depth = max_depth
        self.max_features = max_features
        self.seed = seed
        self.trees = []
        self.oob = []          # per-tree list of indices NOT in its bootstrap

    def fit(self, X, y):
        n = len(X)
        self.trees, self.oob = [], []
        for t in range(self.n_trees):
            r = rng("forest-bag", self.seed, t, n)
            idx = [r.randrange(n) for _ in range(n)]           # bootstrap sample
            inbag = set(idx)
            tree = DecisionTree(max_depth=self.max_depth, max_features=self.max_features,
                                seed=("rf", self.seed, t))
            tree.fit([X[i] for i in idx], [y[i] for i in idx])
            self.trees.append(tree)
            self.oob.append([i for i in range(n) if i not in inbag])
        return self

    def predict(self, X):
        per_tree = [tree.predict(X) for tree in self.trees]
        return [_majority([per_tree[t][i] for t in range(self.n_trees)])
                for i in range(len(X))]

    def oob_score(self, X, y):
        """Out-of-bag accuracy — validation 'for free', no held-out set."""
        n = len(X)
        votes = [[] for _ in range(n)]
        for t, tree in enumerate(self.trees):
            oob_idx = self.oob[t]
            preds = tree.predict([X[i] for i in oob_idx])
            for i, p in zip(oob_idx, preds):
                votes[i].append(p)
        correct = total = 0
        for i in range(n):
            if votes[i]:
                total += 1
                if _majority(votes[i]) == y[i]:
                    correct += 1
        return correct / total if total else 0.0
