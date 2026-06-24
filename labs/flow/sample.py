"""Integrate the flow ODE to turn noise into data, and measure the result."""
from __future__ import annotations

import math

from .field import base_sample, velocity, denoiser


def integrate(x0, data, steps: int, method: str = "euler"):
    """Solve dx/dt = v(x,t) from t=0 to t=1 in ``steps`` steps. Returns the final
    point and the full trajectory (steps+1 states)."""
    x = list(x0)
    traj = [list(x)]
    dt = 1.0 / steps
    for i in range(steps):
        t = i * dt
        if method == "euler":
            v = velocity(x, t, data)
            x = [xi + dt * vi for xi, vi in zip(x, v)]
        elif method == "midpoint":          # RK2
            v1 = velocity(x, t, data)
            xm = [xi + 0.5 * dt * vi for xi, vi in zip(x, v1)]
            v2 = velocity(xm, t + 0.5 * dt, data)
            x = [xi + dt * vi for xi, vi in zip(x, v2)]
        else:
            raise ValueError(f"unknown method {method!r}")
        traj.append(list(x))
    return x, traj


def generate(data, n: int, steps: int = 16, method: str = "euler", seed="flow"):
    """Generate ``n`` samples by flowing base noise through the field."""
    return [integrate(x0, data, steps, method)[0]
            for x0 in base_sample(n, len(data[0]), seed=seed)]


def _dist(a, b) -> float:
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))


def nearest_data_rmse(samples, data) -> float:
    """RMS distance from each sample to its nearest data point (on-manifold-ness)."""
    sq = 0.0
    for s in samples:
        sq += min(_dist(s, y) for y in data) ** 2
    return math.sqrt(sq / len(samples))


def mode_coverage(samples, data) -> float:
    """Fraction of data points that are the nearest neighbour of ≥1 sample."""
    hit = set()
    for s in samples:
        k = min(range(len(data)), key=lambda i: _dist(s, data[i]))
        hit.add(k)
    return len(hit) / len(data)


def straightness(traj) -> float:
    """Path length / straight-line displacement (1.0 = perfectly straight)."""
    total = sum(_dist(traj[i], traj[i + 1]) for i in range(len(traj) - 1))
    direct = _dist(traj[0], traj[-1])
    return total / direct if direct > 1e-9 else 1.0
