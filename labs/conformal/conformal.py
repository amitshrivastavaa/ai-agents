"""Split conformal prediction — prediction intervals with a coverage guarantee.

The whole idea in three steps:

1. fit any model on a training split;
2. on a held-out **calibration** split, score how wrong it is (the nonconformity
   score — here ``|y − ŷ|``);
3. take the ``⌈(n+1)(1−α)⌉ / n`` empirical quantile ``q`` of those scores.

Then ``[ŷ(x) − q, ŷ(x) + q]`` contains the true ``y`` with probability **at least
``1 − α``** — for *any* underlying distribution, *any* model, with no assumption
but exchangeability. That distribution-free guarantee is the magic, and it's
exactly what the demo measures.
"""
from __future__ import annotations

import math

from .model import knn_predict, knn_difficulty


def conformal_quantile(scores, alpha):
    """The conformal ``(1−α)`` quantile of nonconformity ``scores``."""
    n = len(scores)
    s = sorted(scores)
    rank = math.ceil((n + 1) * (1 - alpha))
    if rank > n:                       # not enough calibration points → unbounded
        return float("inf")
    return s[rank - 1]                  # 1-indexed rank → 0-indexed


def calibrate(Xtr, ytr, Xcal, ycal, alpha=0.1, k=7, normalized=False):
    """Return a ``predict(x) -> (lo, hi)`` interval function with ≥1−α coverage."""
    if normalized:
        scores = [abs(y - knn_predict(x, Xtr, ytr, k)) /
                  (knn_difficulty(x, Xtr, ytr, k) + 1e-6)
                  for x, y in zip(Xcal, ycal)]
    else:
        scores = [abs(y - knn_predict(x, Xtr, ytr, k)) for x, y in zip(Xcal, ycal)]
    q = conformal_quantile(scores, alpha)

    def predict(x):
        yhat = knn_predict(x, Xtr, ytr, k)
        half = q * (knn_difficulty(x, Xtr, ytr, k) + 1e-6) if normalized else q
        return yhat - half, yhat + half

    predict.q = q
    return predict


def coverage(predict, Xte, yte):
    """Fraction of test points whose interval contains the true value."""
    hit = sum(1 for x, y in zip(Xte, yte) if predict(x)[0] <= y <= predict(x)[1])
    return hit / len(Xte)


def mean_width(predict, Xte):
    return sum(predict(x)[1] - predict(x)[0] for x in Xte) / len(Xte)
