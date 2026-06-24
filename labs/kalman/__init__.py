"""kalman — the Kalman filter, optimal recursive state estimation.

The algorithm that flies planes, lands rockets, and fuses every phone's GPS:
given a linear-Gaussian system

    xₖ = F·xₖ₋₁ + noise(Q),     zₖ = H·xₖ + noise(R),

it maintains a Gaussian belief (mean ``x``, covariance ``P``) and alternates
**predict** (push through the dynamics, uncertainty grows) and **update** (fuse a
measurement via the **Kalman gain**, uncertainty shrinks). It is the
minimum-variance estimator for this model.

This MVP tracks a noisy 2-D object with a constant-velocity model and shows the
payoff: ~50% lower position error than the raw sensor, beating a moving-average
smoother, while also recovering the **unmeasured velocity** — and the gain
settling to its optimal steady state. Pure stdlib, deterministic.
"""
from .linalg import inv, matmul, transpose, eye
from .filter import KalmanFilter
from .models import constant_velocity, simulate
from .run import track, rmse, moving_average

__all__ = [
    "KalmanFilter", "constant_velocity", "simulate",
    "track", "rmse", "moving_average",
    "inv", "matmul", "transpose", "eye",
]
