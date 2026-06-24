"""k-means clustering (Lloyd's algorithm) with k-means++ initialization.

Lloyd's alternates two steps that each can only *lower* the total within-cluster
squared distance (the **inertia**): assign every point to its nearest centroid,
then move each centroid to its cluster's mean. So inertia decreases monotonically
to a local optimum. The catch is the starting centroids — a bad random draw lands
in a bad optimum. **k-means++** seeds them spread out (each new centroid sampled
∝ squared distance to the nearest existing one), which provably and empirically
gives much better clusterings.
"""
from __future__ import annotations

from .._kernel import rng


def _dist2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def _nearest(point, centroids):
    best_i, best_d = 0, float("inf")
    for i, c in enumerate(centroids):
        d = _dist2(point, c)
        if d < best_d:
            best_i, best_d = i, d
    return best_i, best_d


def _kpp_init(X, k, r):
    centroids = [list(X[r.randrange(len(X))])]
    for _ in range(1, k):
        d2 = [_nearest(x, centroids)[1] for x in X]
        total = sum(d2)
        if total <= 0:
            centroids.append(list(X[r.randrange(len(X))]))
            continue
        threshold = r.random() * total          # sample ∝ squared distance
        acc = 0.0
        for x, d in zip(X, d2):
            acc += d
            if acc >= threshold:
                centroids.append(list(x))
                break
    return centroids


class KMeans:
    def __init__(self, k=4, init="kmeans++", max_iter=100, seed="km"):
        self.k = k
        self.init = init
        self.max_iter = max_iter
        self.seed = seed
        self.centroids = None
        self.labels = None
        self.inertia = None
        self.n_iter = 0
        self.history = []          # inertia after each iteration (monotone ↓)

    def fit(self, X):
        r = rng("kmeans", self.seed, self.k, self.init)
        if self.init == "random":
            idx = r.sample(range(len(X)), self.k)
            self.centroids = [list(X[i]) for i in idx]
        else:
            self.centroids = _kpp_init(X, self.k, r)

        labels = [-1] * len(X)
        for it in range(1, self.max_iter + 1):
            self.n_iter = it
            new_labels = [_nearest(x, self.centroids)[0] for x in X]
            if new_labels == labels:
                break
            labels = new_labels
            dim = len(X[0])
            sums = [[0.0] * dim for _ in range(self.k)]
            counts = [0] * self.k
            for x, c in zip(X, labels):
                counts[c] += 1
                for d in range(dim):
                    sums[c][d] += x[d]
            for c in range(self.k):
                if counts[c]:
                    self.centroids[c] = [sums[c][d] / counts[c] for d in range(dim)]
            self.history.append(sum(_nearest(x, self.centroids)[1] for x in X))
        self.labels = labels
        self.inertia = sum(_nearest(x, self.centroids)[1] for x in X)
        return self
