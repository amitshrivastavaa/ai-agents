"""Gaussian Process regression — Bayesian curve fitting with calibrated error bars.

A GP places a prior over *functions* and conditions it on the data. With an RBF
(squared-exponential) kernel `k(x,x') = σ²·exp(−(x−x')²/2ℓ²)`, the posterior at a
test point is closed-form:

    mean(x*) = k*ᵀ K⁻¹ y
    var(x*)  = k(x*,x*) − k*ᵀ K⁻¹ k*          (K = k(X,X) + σ_n²·I)

The magic is the variance: it collapses to the noise floor *at* the data and
swells back to the prior *away* from it — the model knows what it doesn't know.
Everything is solved through a Cholesky factor of `K`; no training loop, no
randomness.
"""
from __future__ import annotations

import math

from .linalg import cholesky, solve_lower, chol_solve


def rbf(length=1.0, var=1.0):
    """Squared-exponential kernel as a closure ``k(a, b)``."""
    inv = 1.0 / (2.0 * length * length)

    def k(a, b):
        d = a - b
        return var * math.exp(-d * d * inv)
    return k


class GP:
    def __init__(self, kernel, noise=1e-2, prior_var=1.0):
        self.kernel = kernel
        self.noise = noise
        self.prior_var = prior_var
        self.X = []
        self.L = None
        self.alpha = None

    def fit(self, X, y):
        self.X = list(X)
        K = [[self.kernel(xi, xj) for xj in X] for xi in X]
        for i in range(len(X)):
            K[i][i] += self.noise
        self.L = cholesky(K)
        self.alpha = chol_solve(self.L, list(y))
        return self

    def predict(self, x):
        """Posterior ``(mean, variance)`` at a single test point ``x``."""
        kstar = [self.kernel(xi, x) for xi in self.X]
        mean = sum(a * ks for a, ks in zip(self.alpha, kstar))
        v = solve_lower(self.L, kstar)              # v = L⁻¹ k*
        var = self.prior_var - sum(vi * vi for vi in v)
        return mean, max(var, 0.0)

    def predict_many(self, xs):
        return [self.predict(x) for x in xs]
