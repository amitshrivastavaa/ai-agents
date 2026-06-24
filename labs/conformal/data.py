"""A 1-D regression dataset with *heteroscedastic* noise (spread grows with x)."""
from __future__ import annotations

import math

from .._kernel import rng


def heteroscedastic(n=600, lo=-3.0, hi=3.0, seed="cp"):
    """y = sin(x)·1.5 + noise whose std grows with x. Returns (X, y)."""
    r = rng("conformal-data", seed, n)
    X, y = [], []
    for _ in range(n):
        x = r.uniform(lo, hi)
        sigma = 0.15 + 0.35 * (x - lo) / (hi - lo)      # noise widens left→right
        X.append(x)
        y.append(1.5 * math.sin(x) + r.gauss(0, sigma))
    return X, y


def split(X, y, frac_train=0.4, frac_cal=0.4, seed="split"):
    """Shuffle and split into train / calibration / test."""
    r = rng("conformal-split", seed, len(X))
    idx = list(range(len(X)))
    r.shuffle(idx)
    n = len(X)
    a = int(n * frac_train)
    b = a + int(n * frac_cal)
    tr, cal, te = idx[:a], idx[a:b], idx[b:]
    pick = lambda ids: ([X[i] for i in ids], [y[i] for i in ids])
    return pick(tr), pick(cal), pick(te)
