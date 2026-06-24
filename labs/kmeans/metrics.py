"""Cluster-quality metrics: inertia trace, purity vs ground truth, the elbow."""
from __future__ import annotations

from .kmeans import KMeans, _nearest


def purity(labels, true_labels, k):
    """Fraction of points whose cluster's majority true-label they share."""
    n = len(labels)
    total = 0
    for c in range(k):
        members = [t for lab, t in zip(labels, true_labels) if lab == c]
        if members:
            total += max(members.count(t) for t in set(members))
    return total / n


def best_of(X, k, init="kmeans++", restarts=5, seed="m"):
    """Best (lowest-inertia) clustering over several random restarts."""
    best = None
    for s in range(restarts):
        km = KMeans(k=k, init=init, seed=(seed, s)).fit(X)
        if best is None or km.inertia < best.inertia:
            best = km
    return best


def elbow(X, ks=range(1, 8), init="kmeans++", restarts=4, seed="e"):
    """Inertia for each k — the 'elbow' marks the natural number of clusters."""
    return [(k, best_of(X, k, init=init, restarts=restarts, seed=(seed, k)).inertia)
            for k in ks]
