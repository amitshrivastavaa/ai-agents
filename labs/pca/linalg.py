"""Just enough linear algebra for PCA: covariance + power iteration.

Power iteration finds the top eigenvector of a symmetric matrix (repeatedly
multiply and renormalize); **deflation** subtracts it off so the next iteration
finds the second, and so on — that's the whole eigen-decomposition PCA needs.
"""
from __future__ import annotations

import math

from .._kernel import rng


def mean_vector(X):
    n, d = len(X), len(X[0])
    return [sum(x[i] for x in X) / n for i in range(d)]


def covariance(X, mean=None):
    """Sample covariance matrix (d×d)."""
    n, d = len(X), len(X[0])
    mu = mean if mean is not None else mean_vector(X)
    C = [[0.0] * d for _ in range(d)]
    for x in X:
        c = [x[i] - mu[i] for i in range(d)]
        for i in range(d):
            ci = c[i]
            row = C[i]
            for j in range(i, d):
                row[j] += ci * c[j]
    denom = n - 1 if n > 1 else 1
    for i in range(d):
        for j in range(i, d):
            C[i][j] /= denom
            C[j][i] = C[i][j]
    return C


def _matvec(C, v):
    return [sum(row[j] * v[j] for j in range(len(v))) for row in C]


def _norm(v):
    return math.sqrt(sum(x * x for x in v))


def _normalize(v):
    n = _norm(v) or 1.0
    return [x / n for x in v]


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def power_iteration(C, iters=300, tol=1e-12, seed="pca"):
    """Top (eigenvector, eigenvalue) of symmetric ``C`` via power iteration."""
    d = len(C)
    r = rng("pca-power", seed, d)
    v = _normalize([r.gauss(0, 1) for _ in range(d)])
    last = 0.0
    for _ in range(iters):
        w = _matvec(C, v)
        nv = _normalize(w)
        lam = dot(nv, _matvec(C, nv))
        if abs(lam - last) < tol:
            v = nv
            break
        v, last = nv, lam
    return v, dot(v, _matvec(C, v))


def deflate(C, v, lam):
    """Remove the eigen-component ``lam·vvᵀ`` from ``C``."""
    d = len(C)
    return [[C[i][j] - lam * v[i] * v[j] for j in range(d)] for i in range(d)]


def trace(C):
    return sum(C[i][i] for i in range(len(C)))
