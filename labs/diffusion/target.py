"""Target distributions as mixtures of Gaussian modes (so the score is analytic)."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Target:
    name: str
    modes: list[tuple[float, float]]   # the Gaussian means the data clusters at
    sigma0: float = 0.45               # per-mode spread


def _ring(k: int = 10, r: float = 7.0) -> Target:
    modes = [(r * math.cos(2 * math.pi * i / k), r * math.sin(2 * math.pi * i / k))
             for i in range(k)]
    return Target("ring", modes)


def _blobs() -> Target:
    return Target("blobs", [(-6, -6), (6, 6), (-6, 6), (6, -6), (0, 0)], sigma0=0.6)


def _spiral(k: int = 16) -> Target:
    modes = []
    for i in range(k):
        t = 1.4 * math.pi * i / k
        rr = 0.7 + 6.5 * i / k
        modes.append((rr * math.cos(t), rr * math.sin(t)))
    return Target("spiral", modes)


def _grid() -> Target:
    pts = [(gx, gy) for gx in (-6, -2, 2, 6) for gy in (-6, -2, 2, 6)]
    return Target("grid", pts, sigma0=0.4)


TARGETS = {"ring": _ring(), "blobs": _blobs(), "spiral": _spiral(), "grid": _grid()}


def get_target(name: str) -> Target:
    try:
        return TARGETS[name]
    except KeyError:
        raise KeyError(f"unknown target {name!r}; choose from {sorted(TARGETS)}") from None
