"""Scaled dot-product attention, in plain Python."""
from __future__ import annotations

import math


def softmax(xs: list[float]) -> list[float]:
    m = max(xs)
    exps = [math.exp(x - m) for x in xs]
    total = sum(exps) or 1.0
    return [e / total for e in exps]


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def attention(Q: list[list[float]], K: list[list[float]], V: list[list[float]],
              *, scale: float | None = None):
    """Return (output, weights).

    ``Q`` is m×d, ``K`` is n×d, ``V`` is n×dv. ``scale`` multiplies the scores
    before softmax (defaults to 1/√d, the standard temperature; raise it to make
    attention sharper, which is how a trained model concentrates on one key).
    """
    d = len(Q[0])
    scale = (1.0 / math.sqrt(d)) if scale is None else scale
    out: list[list[float]] = []
    weights: list[list[float]] = []
    for q in Q:
        scores = [_dot(q, k) * scale for k in K]
        w = softmax(scores)
        weights.append(w)
        dv = len(V[0])
        out.append([sum(w[i] * V[i][j] for i in range(len(V))) for j in range(dv)])
    return out, weights


def self_attention(X: list[list[float]], *, scale: float | None = None):
    """Self-attention: Q = K = V = X. Returns (output, n×n attention matrix)."""
    return attention(X, X, X, scale=scale)
