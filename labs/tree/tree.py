"""A CART decision tree for classification, from scratch.

Greedily split the data on the (feature, threshold) that most reduces impurity
(Gini or entropy), recurse on each side, and label leaves by majority vote. Each
split is an axis-aligned cut, so the tree carves feature space into rectangles —
which lets it model non-linear boundaries (even XOR) that a single linear
classifier cannot. The building block of random forests and gradient boosting.
"""
from __future__ import annotations

import math

from .._kernel import rng


def gini(y):
    n = len(y)
    if n == 0:
        return 0.0
    counts = {}
    for c in y:
        counts[c] = counts.get(c, 0) + 1
    return 1.0 - sum((v / n) ** 2 for v in counts.values())


def entropy(y):
    n = len(y)
    if n == 0:
        return 0.0
    counts = {}
    for c in y:
        counts[c] = counts.get(c, 0) + 1
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def _majority(y):
    counts = {}
    for c in y:
        counts[c] = counts.get(c, 0) + 1
    return max(counts.items(), key=lambda kv: (kv[1], -kv[0]))[0]


class Node:
    __slots__ = ("feature", "threshold", "left", "right", "label", "n")

    def __init__(self):
        self.feature = None
        self.threshold = None
        self.left = None
        self.right = None
        self.label = None
        self.n = 0


class DecisionTree:
    def __init__(self, max_depth=5, min_samples=2, criterion="gini",
                 max_features=None, seed="dt"):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.impurity = gini if criterion == "gini" else entropy
        self.max_features = max_features        # None=all; int; or "sqrt" (for forests)
        self.seed = seed
        self.root = None
        self.n_features = 0
        self._rng = None

    def fit(self, X, y):
        self.n_features = len(X[0])
        self._rng = rng("dtree", self.seed, len(X)) if self.max_features else None
        self.root = self._build(list(X), list(y), 0)
        return self

    def _feature_subset(self):
        if not self.max_features:
            return range(self.n_features)
        m = self.max_features
        if m == "sqrt":
            m = max(1, int(self.n_features ** 0.5))
        m = min(int(m), self.n_features)
        return self._rng.sample(range(self.n_features), m)

    def _best_split(self, X, y):
        best = None
        parent = self.impurity(y)
        n = len(y)
        for f in self._feature_subset():
            vals = sorted(set(x[f] for x in X))
            for a, b in zip(vals, vals[1:]):
                thr = (a + b) / 2.0
                ly = [y[i] for i in range(n) if X[i][f] <= thr]
                ry = [y[i] for i in range(n) if X[i][f] > thr]
                if not ly or not ry:
                    continue
                child = (len(ly) * self.impurity(ly) + len(ry) * self.impurity(ry)) / n
                gain = parent - child
                if best is None or gain > best[0]:
                    best = (gain, f, thr)
        return best

    def _build(self, X, y, depth):
        node = Node()
        node.n = len(y)
        node.label = _majority(y)
        if (depth >= self.max_depth or len(y) < self.min_samples
                or self.impurity(y) == 0.0):
            return node
        split = self._best_split(X, y)
        if split is None or split[0] <= 0:
            return node
        _, f, thr = split
        node.feature, node.threshold = f, thr
        li = [i for i in range(len(y)) if X[i][f] <= thr]
        ri = [i for i in range(len(y)) if X[i][f] > thr]
        node.left = self._build([X[i] for i in li], [y[i] for i in li], depth + 1)
        node.right = self._build([X[i] for i in ri], [y[i] for i in ri], depth + 1)
        return node

    def _predict_one(self, x):
        node = self.root
        while node.feature is not None:
            node = node.left if x[node.feature] <= node.threshold else node.right
        return node.label

    def predict(self, X):
        return [self._predict_one(x) for x in X]

    def depth(self):
        def d(node):
            if node is None or node.feature is None:
                return 1
            return 1 + max(d(node.left), d(node.right))
        return d(self.root)

    def n_leaves(self):
        def c(node):
            if node is None or node.feature is None:
                return 1
            return c(node.left) + c(node.right)
        return c(self.root)
