"""A small CART regression tree — the weak learner gradient boosting stacks.

Splits to minimize the children's summed squared error (equivalently, maximize
variance reduction); each leaf predicts the mean of its targets. Kept shallow on
purpose — boosting wants *weak* learners.
"""
from __future__ import annotations


def _stats(y):
    n = len(y)
    s = sum(y)
    return n, s, sum(v * v for v in y)          # count, sum, sum of squares


def _sse(n, s, ss):
    return ss - (s * s / n) if n else 0.0       # Σ(y-ȳ)²


class RegTree:
    def __init__(self, max_depth=3, min_samples=5):
        self.max_depth = max_depth
        self.min_samples = min_samples
        self.root = None
        self.n_features = 0

    def fit(self, X, y):
        self.n_features = len(X[0])
        self.root = self._build(list(X), list(y), 0)
        return self

    def _build(self, X, y, depth):
        mean = sum(y) / len(y)
        node = {"leaf": mean}
        if depth >= self.max_depth or len(y) < 2 * self.min_samples:
            return node
        best = None
        for f in range(self.n_features):
            order = sorted(range(len(y)), key=lambda i: X[i][f])
            xs = [X[i][f] for i in order]
            ys = [y[i] for i in order]
            ln, ls, lss = 0, 0.0, 0.0
            rn, rs, rss = _stats(ys)
            for k in range(1, len(ys)):
                v = ys[k - 1]
                ln += 1; ls += v; lss += v * v
                rn -= 1; rs -= v; rss -= v * v
                if xs[k] == xs[k - 1] or ln < self.min_samples or rn < self.min_samples:
                    continue
                sse = _sse(ln, ls, lss) + _sse(rn, rs, rss)
                if best is None or sse < best[0]:
                    best = (sse, f, (xs[k] + xs[k - 1]) / 2.0)
        if best is None:
            return node
        _, f, thr = best
        li = [i for i in range(len(y)) if X[i][f] <= thr]
        ri = [i for i in range(len(y)) if X[i][f] > thr]
        if not li or not ri:
            return node
        node = {"feature": f, "threshold": thr,
                "left": self._build([X[i] for i in li], [y[i] for i in li], depth + 1),
                "right": self._build([X[i] for i in ri], [y[i] for i in ri], depth + 1)}
        return node

    def _predict_one(self, x, node):
        while "leaf" not in node:
            node = node["left"] if x[node["feature"]] <= node["threshold"] else node["right"]
        return node["leaf"]

    def predict(self, X):
        return [self._predict_one(x, self.root) for x in X]
