"""2-D binary datasets: a linearly-separable one, and the non-linear moons/XOR."""
from __future__ import annotations

import math

from .._kernel import rng


def linear(n=300, gap=1.2, seed="lin"):
    """Two Gaussian classes either side of a slanted line — linearly separable."""
    r = rng("logreg-linear", seed, n)
    X, y = [], []
    for _ in range(n):
        c = r.randrange(2)
        cx, cy = (-gap, -gap) if c == 0 else (gap, gap)
        X.append([cx + r.gauss(0, 1.0), cy + r.gauss(0, 1.0)])
        y.append(c)
    return X, y


def moons(n=300, seed="m"):
    r = rng("logreg-moons", seed, n)
    X, y = [], []
    for _ in range(n):
        if r.random() < 0.5:
            t = r.uniform(0, math.pi)
            X.append([math.cos(t) + r.gauss(0, 0.15), math.sin(t) + r.gauss(0, 0.15)])
            y.append(0)
        else:
            t = r.uniform(0, math.pi)
            X.append([1 - math.cos(t) + r.gauss(0, 0.15),
                      0.5 - math.sin(t) + r.gauss(0, 0.15)])
            y.append(1)
    return X, y


def split(X, y, frac=0.7, seed="s"):
    r = rng("logreg-split", seed, len(X))
    idx = list(range(len(X)))
    r.shuffle(idx)
    cut = int(len(X) * frac)
    tr, te = idx[:cut], idx[cut:]
    return ([X[i] for i in tr], [y[i] for i in tr],
            [X[i] for i in te], [y[i] for i in te])
