"""1-D regression targets that are hard for a single shallow tree."""
from __future__ import annotations

import math

from .._kernel import rng


def make(kind="step", n=200, noise=0.1, lo=-3.0, hi=3.0, seed="gb"):
    """Return (X, y). X is a list of 1-element points."""
    r = rng("boosting-data", seed, n, kind)
    fns = {
        "step": lambda x: (1.0 if x > 0 else -1.0) + (0.5 if x > 1.5 else 0.0),
        "sine": lambda x: math.sin(1.5 * x),
        "wiggle": lambda x: math.sin(2 * x) + 0.4 * x,
    }
    f = fns[kind]
    X, y, truth = [], [], []
    for _ in range(n):
        x = r.uniform(lo, hi)
        X.append([x])
        truth.append(f(x))
        y.append(f(x) + r.gauss(0, noise))
    return X, y, truth


def split(X, y, frac=0.7, seed="s"):
    r = rng("boosting-split", seed, len(X))
    idx = list(range(len(X)))
    r.shuffle(idx)
    cut = int(len(X) * frac)
    tr, te = idx[:cut], idx[cut:]
    return ([X[i] for i in tr], [y[i] for i in tr],
            [X[i] for i in te], [y[i] for i in te])
