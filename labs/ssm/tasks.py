"""The selective-copy / sample-and-hold task — Mamba's motivating example.

A value stream carries numbers at every step, but only the **write** positions
(gate==1) should be captured; between writes the last captured value must be
*held*, ignoring whatever the stream says at the hold positions. A selective SSM
nails it; no time-invariant (constant-dynamics) SSM can — that is the point.
"""
from __future__ import annotations

from .._kernel import rng
from .ssm import ssm_scan


def make_task(n=24, writes=(0, 8, 16), seed="ssm"):
    """Return ``(values, gates, target)``.

    ``target`` is the exact sample-and-hold: the value from the most recent
    write position (0 before the first write).
    """
    r = rng(seed, n, tuple(writes))
    values = [round(r.uniform(-1.0, 1.0), 3) for _ in range(n)]
    write_set = set(writes)
    gates = [1 if t in write_set else 0 for t in range(n)]
    target: list[float] = []
    held = 0.0
    for t in range(n):
        if gates[t]:
            held = values[t]
        target.append(held)
    return values, gates, target


def mse(a, b) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) / len(a)


def best_lti(values, gates, target, *, grid=26):
    """The fairest possible time-invariant baseline.

    We even hand the LTI SSM the *gate-masked* input (``gate * value`` — a
    generous head start) and grid-search **both** of its constant parameters
    ``(a, b)``. It still can't reproduce sample-and-hold: holding needs ``a≈1``
    but capturing needs ``a≈0``, and a constant ``a`` can't be both.

    Returns ``(best_mse, best_a, best_b, best_y)``.
    """
    xg = [g * v for g, v in zip(gates, values)]
    best = None
    for i in range(grid):
        a = i / (grid - 1)              # 0 .. 1
        for j in range(grid):
            b = j / (grid - 1) * 2.0    # 0 .. 2
            y, _ = ssm_scan(xg, a, b, c=1.0, d=0.0)
            e = mse(y, target)
            if best is None or e < best[0]:
                best = (e, a, b, y)
    return best
