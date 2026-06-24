"""Random-hyperplane LSH (SimHash) — the hash that makes cosine search sublinear.

Each bit of the signature is the side of a random hyperplane the vector falls on:
``bit = 1 if v·r ≥ 0 else 0`` for a random Gaussian normal ``r``. The magic
property: for two vectors at angle θ, a single random hyperplane separates them
with probability exactly ``θ/π``, so they **share a bit with probability
``1 − θ/π``**. Similar vectors (small θ) collide often; dissimilar ones rarely —
which is exactly what a nearest-neighbour index wants.
"""
from __future__ import annotations

import math

from .._kernel import rng


class SimHash:
    def __init__(self, dim: int, n_bits: int, seed="h"):
        r = rng("lsh-hash", seed, dim, n_bits)
        self.planes = [[r.gauss(0, 1) for _ in range(dim)] for _ in range(n_bits)]

    def signature(self, v):
        return tuple(1 if sum(p * x for p, x in zip(plane, v)) >= 0 else 0
                     for plane in self.planes)


def angle(a, b) -> float:
    """Angle (radians) between two unit vectors."""
    d = max(-1.0, min(1.0, sum(x * y for x, y in zip(a, b))))
    return math.acos(d)


def collision_prob(theta: float, n_bits: int = 1) -> float:
    """Probability two vectors at angle θ match on all ``n_bits`` SimHash bits."""
    return (1.0 - theta / math.pi) ** n_bits
