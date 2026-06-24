"""A 2-D constant-velocity tracking model and a noisy trajectory simulator."""
from __future__ import annotations

import math

from .._kernel import rng


def constant_velocity(dt=1.0, q=0.02, r=9.0):
    """State = [x, y, vx, vy]; we measure position only.

    ``q`` is the process-noise intensity (how much we let velocity drift),
    ``r`` the measurement-noise variance (σ²).
    """
    F = [[1, 0, dt, 0],
         [0, 1, 0, dt],
         [0, 0, 1, 0],
         [0, 0, 0, 1]]
    H = [[1, 0, 0, 0],
         [0, 1, 0, 0]]
    # discrete white-noise-acceleration process covariance
    q3, q2, q1 = q * dt ** 3 / 3.0, q * dt ** 2 / 2.0, q * dt
    Q = [[q3, 0, q2, 0],
         [0, q3, 0, q2],
         [q2, 0, q1, 0],
         [0, q2, 0, q1]]
    R = [[r, 0], [0, r]]
    return F, H, Q, R


def simulate(steps=60, dt=1.0, meas_std=3.0, kind="sine", seed="kal"):
    """Return ``(truth, measurements)`` as lists of (x, y) tuples."""
    r = rng("kalman-sim", seed, kind, steps)
    truth, meas = [], []
    for k in range(steps):
        t = k * dt
        if kind == "line":
            px, py = 1.0 * t, 0.5 * t
        elif kind == "sine":
            px, py = 1.0 * t, 6.0 * math.sin(0.12 * t)
        elif kind == "turn":                       # constant-speed circular arc
            ang = 0.06 * t
            px, py = 18.0 * math.sin(ang), 18.0 * (1 - math.cos(ang))
        else:
            raise ValueError(f"unknown trajectory {kind!r}")
        truth.append((px, py))
        meas.append((px + r.gauss(0.0, meas_std), py + r.gauss(0.0, meas_std)))
    return truth, meas
