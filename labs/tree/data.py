"""2-D labeled datasets — including XOR, which no linear model can separate."""
from __future__ import annotations

import math

from .._kernel import rng


def blobs(n=300, seed="b"):
    r = rng("tree-blobs", seed, n)
    centers = [(-2.5, -2.5, 0), (2.5, 2.5, 1), (-2.5, 2.5, 2)]
    X, y = [], []
    for _ in range(n):
        cx, cy, c = centers[r.randrange(len(centers))]
        X.append([cx + r.gauss(0, 0.7), cy + r.gauss(0, 0.7)])
        y.append(c)
    return X, y


def xor(n=300, seed="x"):
    """Class = (x>0) XOR (y>0) — the classic non-linearly-separable problem."""
    r = rng("tree-xor", seed, n)
    X, y = [], []
    for _ in range(n):
        x = r.uniform(-3, 3)
        yy = r.uniform(-3, 3)
        X.append([x, yy])
        y.append(int((x > 0) ^ (yy > 0)))
    return X, y


def moons(n=300, seed="m"):
    r = rng("tree-moons", seed, n)
    X, y = [], []
    for _ in range(n):
        if r.random() < 0.5:
            t = r.uniform(0, math.pi)
            X.append([math.cos(t) + r.gauss(0, 0.15),
                      math.sin(t) + r.gauss(0, 0.15)])
            y.append(0)
        else:
            t = r.uniform(0, math.pi)
            X.append([1 - math.cos(t) + r.gauss(0, 0.15),
                      0.5 - math.sin(t) + r.gauss(0, 0.15)])
            y.append(1)
    return X, y


def train_test_split(X, y, frac=0.7, seed="s"):
    r = rng("tree-split", seed, len(X))
    idx = list(range(len(X)))
    r.shuffle(idx)
    cut = int(len(X) * frac)
    tr, te = idx[:cut], idx[cut:]
    return ([X[i] for i in tr], [y[i] for i in tr],
            [X[i] for i in te], [y[i] for i in te])


DATASETS = {"blobs": blobs, "xor": xor, "moons": moons}
