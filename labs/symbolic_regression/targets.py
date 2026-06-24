"""Hidden functions to rediscover from sampled points."""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Target:
    name: str
    formula: str            # the ground-truth formula (for the reveal)
    X: list[float]
    y: list[float]


def _make(name: str, fn, formula: str, *, lo=-3.0, hi=3.0, n=21) -> Target:
    X = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    return Target(name, formula, X, [fn(x) for x in X])


TARGETS = {
    "linear": _make("linear", lambda x: 2 * x + 1, "2*x + 1"),
    "quadratic": _make("quadratic", lambda x: x * x - 2, "x*x - 2"),
    "cubic": _make("cubic", lambda x: x ** 3 - x, "x*x*x - x"),
    "damped": _make("damped", lambda x: x * math.sin(x), "x*sin(x)"),
}


def get_target(name: str) -> Target:
    try:
        return TARGETS[name]
    except KeyError:
        raise KeyError(f"unknown target {name!r}; choose from {sorted(TARGETS)}") from None
