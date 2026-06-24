"""Clustered unit vectors — a dataset where nearest-neighbour structure exists."""
from __future__ import annotations

import math

from .._kernel import rng


def normalize(v):
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def cosine(a, b) -> float:
    """Cosine similarity. Assumes inputs are unit-normalized (they are here)."""
    return sum(x * y for x, y in zip(a, b))


def _centers(dim, clusters, seed):
    """Cluster centers — keyed only on (dim, clusters, seed) so the dataset and
    its held-out queries share the *same* centers regardless of how many points
    each draws."""
    r = rng("lsh-centers", seed, dim, clusters)
    return [normalize([r.gauss(0, 1) for _ in range(dim)]) for _ in range(clusters)]


def make_dataset(n=600, dim=24, clusters=12, spread=0.12, seed="lsh"):
    """Return ``(vectors, labels)`` — points drawn around shared cluster centers."""
    centers = _centers(dim, clusters, seed)
    r = rng("lsh-data", seed, n, dim, clusters)
    data, labels = [], []
    for _ in range(n):
        ci = r.randrange(clusters)
        data.append(normalize([centers[ci][d] + r.gauss(0, spread) for d in range(dim)]))
        labels.append(ci)
    return data, labels


def make_queries(n=120, dim=24, clusters=12, spread=0.12, seed="lsh-q",
                 base_seed="lsh"):
    """Held-out query points drawn from the *same* centers as ``make_dataset``."""
    centers = _centers(dim, clusters, base_seed)
    r = rng("lsh-query", seed, n, dim)
    out = []
    for _ in range(n):
        ci = r.randrange(clusters)
        out.append(normalize([centers[ci][d] + r.gauss(0, spread) for d in range(dim)]))
    return out
