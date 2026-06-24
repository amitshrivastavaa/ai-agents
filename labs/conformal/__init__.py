"""conformal — distribution-free prediction intervals with a coverage guarantee.

Split conformal prediction wraps *any* regressor: fit on a training split, measure
its errors on a held-out **calibration** split, and take the ``(1−α)`` quantile of
those errors as the interval half-width. The result — ``ŷ(x) ± q`` — contains the
true value with probability **at least ``1 − α``**, for any data distribution and
any model, assuming only exchangeability. No Gaussian assumption, no asymptotics.

This MVP demonstrates that guarantee (coverage lands on ``1−α`` across many random
splits) and a **normalized** variant whose intervals adapt to local noise. The
agnostic cousin of the lab's `gp` (model-specific Bayesian uncertainty).
"""
from .model import knn_predict, knn_difficulty
from .conformal import (conformal_quantile, calibrate, coverage, mean_width)
from .data import heteroscedastic, split

__all__ = [
    "knn_predict", "knn_difficulty",
    "conformal_quantile", "calibrate", "coverage", "mean_width",
    "heteroscedastic", "split",
]
