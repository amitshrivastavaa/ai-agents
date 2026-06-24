"""Datasets for PCA: a 2-D correlated cloud, and structured low-rank vectors."""
from __future__ import annotations

import math

from .._kernel import rng


def correlated_2d(n=300, angle=0.5, sx=3.0, sy=0.6, seed="2d"):
    """A 2-D Gaussian cloud stretched along a known direction — PC1 should
    recover that axis. Returns ``(points, true_axis)``."""
    r = rng("pca-2d", seed, n)
    ca, sa = math.cos(angle), math.sin(angle)
    pts = []
    for _ in range(n):
        u, v = r.gauss(0, sx), r.gauss(0, sy)        # stretched, then rotated
        pts.append([ca * u - sa * v, sa * u + ca * v])
    return pts, [ca, sa]


def low_rank(n=200, dim=40, rank=3, noise=0.05, seed="lr"):
    """Vectors that truly live in a ``rank``-dim subspace (+ small noise), so a
    few principal components should capture nearly all the variance."""
    r = rng("pca-lowrank", seed, n, dim, rank)
    basis = []
    for _ in range(rank):
        b = [r.gauss(0, 1) for _ in range(dim)]
        nrm = math.sqrt(sum(x * x for x in b)) or 1.0
        basis.append([x / nrm for x in b])
    data = []
    for _ in range(n):
        coef = [r.gauss(0, 1) for _ in range(rank)]
        x = [sum(coef[k] * basis[k][i] for k in range(rank)) + r.gauss(0, noise)
             for i in range(dim)]
        data.append(x)
    return data
