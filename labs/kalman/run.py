"""Run the filter over a trajectory and compare it to the raw measurements."""
from __future__ import annotations

import math

from .filter import KalmanFilter
from .models import constant_velocity, simulate
from .linalg import eye


def rmse(a, b) -> float:
    return math.sqrt(sum((ax - bx) ** 2 + (ay - by) ** 2
                         for (ax, ay), (bx, by) in zip(a, b)) / len(a))


def moving_average(meas, window=5):
    out = []
    for i in range(len(meas)):
        lo = max(0, i - window + 1)
        chunk = meas[lo:i + 1]
        out.append((sum(p[0] for p in chunk) / len(chunk),
                    sum(p[1] for p in chunk) / len(chunk)))
    return out


def track(steps=60, dt=1.0, meas_std=3.0, kind="sine", q=0.05, seed="kal"):
    """Filter a simulated noisy trajectory. Returns a dict of series + RMSEs."""
    truth, meas = simulate(steps, dt, meas_std, kind, seed)
    F, H, Q, R = constant_velocity(dt, q, meas_std ** 2)

    P0 = [[r * c for c in row] for r, row in zip([10, 10, 100, 100], eye(4))]
    x0 = [meas[0][0], meas[0][1], 0.0, 0.0]
    kf = KalmanFilter(F, H, Q, R, x0, P0)

    est, vel, gains = [], [], []
    for z in meas:
        x, K = kf.step(list(z))
        est.append((x[0], x[1]))
        vel.append((x[2], x[3]))
        gains.append(K[0][0])
    return {
        "truth": truth, "meas": meas, "est": est, "vel": vel, "gains": gains,
        "rmse_meas": rmse(meas, truth),
        "rmse_filt": rmse(est, truth),
        "rmse_ma": rmse(moving_average(meas), truth),
    }
