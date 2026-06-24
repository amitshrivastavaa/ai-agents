"""A k-nearest-neighbours regressor — a simple, deterministic base predictor.

Conformal prediction wraps *any* model; we use k-NN so the focus stays on the
calibration, not the training. ``difficulty`` gives a per-point spread estimate
(the local neighbour disagreement) for normalized/adaptive conformal.
"""
from __future__ import annotations


def _dist(a, b):
    return abs(a - b)


def knn_predict(x, Xtr, ytr, k=7):
    order = sorted(range(len(Xtr)), key=lambda i: _dist(x, Xtr[i]))[:k]
    return sum(ytr[i] for i in order) / k


def knn_difficulty(x, Xtr, ytr, k=7):
    """Local std of neighbour targets — a cheap 'how hard is here' estimate."""
    order = sorted(range(len(Xtr)), key=lambda i: _dist(x, Xtr[i]))[:k]
    ys = [ytr[i] for i in order]
    mu = sum(ys) / len(ys)
    var = sum((y - mu) ** 2 for y in ys) / len(ys)
    return var ** 0.5
