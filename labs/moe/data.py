"""Piecewise datasets where different regions need different experts."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .._kernel import rng


@dataclass
class Dataset:
    name: str
    X: list[float]
    y: list[float]
    region: list[int]      # ground-truth regime index, for evaluation


def _piecewise(n: int = 120, seed: str = "pw") -> Dataset:
    # three linear regimes with very different slopes
    pieces = [(0.00, 0.33, 2.4, 0.1),
              (0.33, 0.66, -1.8, 1.4),
              (0.66, 1.01, 1.2, -0.6)]
    r = rng(seed)
    X, y, region = [], [], []
    for _ in range(n):
        x = r.random()
        for idx, (lo, hi, m, b) in enumerate(pieces):
            if lo <= x < hi:
                X.append(x)
                y.append(m * x + b + r.gauss(0, 0.03))
                region.append(idx)
                break
    return Dataset("piecewise", X, y, region)


def _fan(n: int = 160, seed: str = "fan") -> Dataset:
    # four regimes with distinct slopes AND intercepts (asymmetric → no collapse)
    pieces = [(0.00, 0.25, 1.6, 0.10),
              (0.25, 0.50, -1.2, 0.95),
              (0.50, 0.75, 2.0, -0.70),
              (0.75, 1.01, -0.8, 1.30)]
    r = rng(seed)
    X, y, region = [], [], []
    for _ in range(n):
        x = r.random()
        for idx, (lo, hi, m, b) in enumerate(pieces):
            if lo <= x < hi:
                X.append(x)
                y.append(m * x + b + r.gauss(0, 0.03))
                region.append(idx)
                break
    return Dataset("fan", X, y, region)


DATASETS = {"piecewise": _piecewise, "fan": _fan}


def get_dataset(name: str) -> Dataset:
    try:
        return DATASETS[name]()
    except KeyError:
        raise KeyError(f"unknown dataset {name!r}; choose from {sorted(DATASETS)}") from None
