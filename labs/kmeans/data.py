"""Gaussian blobs with ground-truth labels — a dataset clustering should recover."""
from __future__ import annotations

from .._kernel import rng


def blobs(n=300, k=4, dim=2, spread=0.45, seed="blobs", span=6.0):
    """Return ``(points, true_labels, centers)``."""
    r = rng("kmeans-data", seed, n, k, dim)
    centers = [[r.uniform(-span, span) for _ in range(dim)] for _ in range(k)]
    pts, labels = [], []
    for _ in range(n):
        c = r.randrange(k)
        pts.append([centers[c][d] + r.gauss(0, spread) for d in range(dim)])
        labels.append(c)
    return pts, labels, centers
