"""Scalar state-space models (SSM) — the recurrent core of S4 / Mamba.

A single-channel SSM is the linear recurrence

    h_t = a_t * h_{t-1} + b_t * x_t
    y_t = c_t * h_t     + d * x_t          (h_{-1} = 0)

When the parameters are constant (a_t = a, …) the model is **linear and
time-invariant** (LTI), and the recurrence is *exactly* a causal convolution
with the kernel ``K[k] = c * b * a**k`` — the "SSM duality" that lets S4 train in
parallel as a convolution and run as a fast recurrence. Mamba's twist is to make
``a_t, b_t`` depend on the input (selectivity); the duality then breaks, but the
model gains the power to *choose what to remember* (see ``selective.py``).

Pure stdlib, no numpy — single channel keeps the arithmetic readable.
"""
from __future__ import annotations


def _as_seq(v, n: int) -> list[float]:
    """Broadcast a scalar to length ``n``; pass a length-``n`` sequence through."""
    if isinstance(v, (int, float)):
        return [float(v)] * n
    out = [float(x) for x in v]
    if len(out) != n:
        raise ValueError(f"expected {n} per-step params, got {len(out)}")
    return out


def ssm_scan(x, a, b, c=1.0, d=0.0):
    """Sequential recurrence. ``a``/``b``/``c`` may be scalars (LTI) or per-step
    sequences (time-varying / selective). Returns ``(y, h)`` as length-``len(x)``
    lists."""
    n = len(x)
    a_, b_, c_ = _as_seq(a, n), _as_seq(b, n), _as_seq(c, n)
    y: list[float] = []
    h: list[float] = []
    prev = 0.0
    for t in range(n):
        cur = a_[t] * prev + b_[t] * x[t]
        h.append(cur)
        y.append(c_[t] * cur + d * x[t])
        prev = cur
    return y, h


def ssm_kernel(a, b, c, length: int) -> list[float]:
    """The LTI convolution kernel ``K[k] = c * b * a**k`` for ``k = 0..length-1``.

    This is the SSM's impulse response: feed a unit impulse and the output *is*
    the kernel.
    """
    out: list[float] = []
    ak = 1.0
    for _ in range(length):
        out.append(c * b * ak)
        ak *= a
    return out


def ssm_conv(x, a, b, c=1.0, d=0.0) -> list[float]:
    """LTI SSM as a causal convolution — equals :func:`ssm_scan` for constant
    params (the duality). ``O(n^2)`` here for clarity; FFT makes it ``O(n log n)``."""
    n = len(x)
    k = ssm_kernel(a, b, c, n)
    y: list[float] = []
    for t in range(n):
        acc = d * x[t]
        for j in range(t + 1):
            acc += k[t - j] * x[j]
        y.append(acc)
    return y
