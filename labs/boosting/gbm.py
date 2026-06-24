"""Gradient boosting for regression — the engine behind XGBoost / LightGBM.

Start from a constant prediction (the mean). Then, again and again, look at where
the ensemble is *wrong* — the residuals `y − F(x)` — and fit a small tree to those
residuals, adding a shrunk version of it to `F`. For squared loss the residual is
exactly the negative gradient of the loss, so each tree is one step of **gradient
descent in function space**. Many shallow trees, each fixing the last one's
mistakes, compose into a sharp non-linear fit a single weak learner can't reach.
"""
from __future__ import annotations

from .regtree import RegTree


def mse(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)


class GradientBoosting:
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3, min_samples=5):
        self.n_estimators = n_estimators
        self.lr = learning_rate
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.base = 0.0
        self.trees = []
        self.train_loss = []          # train MSE after each tree (monotone ↓)

    def fit(self, X, y):
        self.base = sum(y) / len(y)
        F = [self.base] * len(y)
        self.trees, self.train_loss = [], []
        for _ in range(self.n_estimators):
            residual = [yi - fi for yi, fi in zip(y, F)]      # = −∂(½(y−F)²)/∂F
            tree = RegTree(max_depth=self.max_depth, min_samples=self.min_samples)
            tree.fit(X, residual)
            step = tree.predict(X)
            F = [fi + self.lr * si for fi, si in zip(F, step)]
            self.trees.append(tree)
            self.train_loss.append(mse(F, y))
        return self

    def predict(self, X):
        F = [self.base] * len(X)
        for tree in self.trees:
            step = tree.predict(X)
            F = [fi + self.lr * si for fi, si in zip(F, step)]
        return F

    def staged_predict(self, X, stages):
        """Predictions using only the first k trees, for each k in ``stages``."""
        want = set(stages)
        out = {}
        F = [self.base] * len(X)
        if 0 in want:
            out[0] = list(F)
        for m, tree in enumerate(self.trees, 1):
            step = tree.predict(X)
            F = [fi + self.lr * si for fi, si in zip(F, step)]
            if m in want:
                out[m] = list(F)
        return out
