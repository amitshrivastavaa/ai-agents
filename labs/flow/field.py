"""The analytic flow-matching velocity field for an empirical target.

Rectified flow / conditional flow matching transports a simple base
distribution ``p₀ = N(0, I)`` to a data distribution ``p₁`` along the straight
interpolation ``x_t = (1−t)·x₀ + t·x₁`` (``t: 0→1``). The conditional velocity of
that line is ``x₁ − x₀``; the field that actually generates the marginal path is
its posterior expectation

    v(x, t) = E[x₁ − x₀ | x_t = x].

For a target supported on a finite data set ``{yₖ}`` (with base ``N(0,I)``) this
expectation is *analytic*, exactly like the score in the lab's diffusion MVP.
Given ``x_t = x``:

    x_t | yₖ ~ N(t·yₖ, (1−t)²·I)
    wₖ(x,t) ∝ exp( −‖x − t·yₖ‖² / (2(1−t)²) )      (posterior over which yₖ)
    ŷ(x,t)  = Σₖ wₖ·yₖ                              (the "denoiser": posterior mean)
    v(x,t)  = (ŷ(x,t) − x) / (1 − t)

Integrating ``dx/dt = v(x,t)`` from ``x₀ ~ N(0,I)`` carries noise onto the data —
deterministically, no noise injected along the way (unlike diffusion's Langevin).
"""
from __future__ import annotations

import math

from .._kernel import rng


def base_sample(n: int, dim: int = 2, seed="flow"):
    """Draw ``n`` points from the base distribution N(0, I)."""
    r = rng("flow-base", seed)
    return [[r.gauss(0.0, 1.0) for _ in range(dim)] for _ in range(n)]


def weights(x, t: float, data):
    """Posterior ``wₖ(x,t)`` over which data point generated ``x`` at time ``t``."""
    s = 1.0 - t
    var = s * s
    logits = [-sum((xi - t * yi) ** 2 for xi, yi in zip(x, y)) / (2.0 * var)
              for y in data]
    m = max(logits)
    exps = [math.exp(l - m) for l in logits]
    z = sum(exps)
    return [e / z for e in exps]


def denoiser(x, t: float, data):
    """ŷ(x,t) — the posterior-mean data point given the current state."""
    w = weights(x, t, data)
    dim = len(x)
    return [sum(wk * y[d] for wk, y in zip(w, data)) for d in range(dim)]


def velocity(x, t: float, data):
    """v(x,t) = (ŷ(x,t) − x)/(1−t)."""
    s = 1.0 - t
    yhat = denoiser(x, t, data)
    return [(yh - xi) / s for yh, xi in zip(yhat, x)]
