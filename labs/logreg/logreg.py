"""Logistic regression by gradient descent — the canonical linear classifier.

Model the probability of the positive class as a squashed linear score,
``P(y=1|x) = σ(w·x + b)``, and fit ``w, b`` by minimizing **cross-entropy**. That
loss is *convex*, so plain gradient descent slides straight to the global optimum
— no local minima, no restarts. The discriminative cousin of the lab's generative
``naivebayes``: it learns the boundary directly instead of modeling each class.
"""
from __future__ import annotations

import math


def sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


class LogisticRegression:
    def __init__(self, lr=0.5, epochs=300, l2=0.0):
        self.lr = lr
        self.epochs = epochs
        self.l2 = l2
        self.w = None
        self.b = 0.0
        self.mean = None
        self.std = None
        self.loss_history = []

    def _standardize(self, X, fit=False):
        if fit:
            d = len(X[0])
            self.mean = [sum(x[j] for x in X) / len(X) for j in range(d)]
            self.std = []
            for j in range(d):
                v = sum((x[j] - self.mean[j]) ** 2 for x in X) / len(X)
                self.std.append(math.sqrt(v) or 1.0)
        return [[(x[j] - self.mean[j]) / self.std[j] for j in range(len(x))] for x in X]

    def fit(self, X, y):
        Z = self._standardize(X, fit=True)
        n, d = len(Z), len(Z[0])
        self.w = [0.0] * d
        self.b = 0.0
        self.loss_history = []
        for _ in range(self.epochs):
            gw = [0.0] * d
            gb = 0.0
            loss = 0.0
            for x, yi in zip(Z, y):
                p = sigmoid(sum(wj * xj for wj, xj in zip(self.w, x)) + self.b)
                err = p - yi
                for j in range(d):
                    gw[j] += err * x[j]
                gb += err
                eps = 1e-12
                loss -= yi * math.log(p + eps) + (1 - yi) * math.log(1 - p + eps)
            self.w = [wj - self.lr * (gw[j] / n + self.l2 * wj)
                      for j, wj in enumerate(self.w)]
            self.b -= self.lr * gb / n
            reg = self.l2 / 2 * sum(wj * wj for wj in self.w)
            self.loss_history.append(loss / n + reg)
        return self

    def predict_proba(self, X):
        Z = self._standardize(X)
        return [sigmoid(sum(wj * xj for wj, xj in zip(self.w, x)) + self.b) for x in Z]

    def predict(self, X, threshold=0.5):
        return [1 if p >= threshold else 0 for p in self.predict_proba(X)]
