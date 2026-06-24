"""The Kalman filter — optimal recursive estimation for a linear-Gaussian system.

The system is

    xₖ = F·xₖ₋₁ + process noise (cov Q)        # how the state evolves
    zₖ = H·xₖ   + measurement noise (cov R)     # what we get to observe

The filter keeps a Gaussian belief over the hidden state — mean ``x`` and
covariance ``P`` — and alternates:

* **predict**: push the belief through the dynamics (``x←Fx``, ``P←FPFᵀ+Q``);
  uncertainty grows.
* **update**: fold in a measurement. The **Kalman gain** ``K = P Hᵀ (H P Hᵀ + R)⁻¹``
  optimally blends prediction and measurement by their relative certainty;
  uncertainty shrinks.

It is the *minimum-variance* estimator for this model — no estimator does better.
"""
from __future__ import annotations

from .linalg import (matmul, transpose, matadd, matsub, matvec, vecadd, vecsub,
                     eye, inv)


class KalmanFilter:
    def __init__(self, F, H, Q, R, x0, P0):
        self.F, self.H, self.Q, self.R = F, H, Q, R
        self.x = list(x0)
        self.P = [row[:] for row in P0]

    def predict(self):
        self.x = matvec(self.F, self.x)
        self.P = matadd(matmul(matmul(self.F, self.P), transpose(self.F)), self.Q)
        return self.x

    def update(self, z):
        H, P, R = self.H, self.P, self.R
        Ht = transpose(H)
        y = vecsub(z, matvec(H, self.x))                       # innovation
        S = matadd(matmul(matmul(H, P), Ht), R)                # innovation cov
        K = matmul(matmul(P, Ht), inv(S))                      # Kalman gain
        self.x = vecadd(self.x, matvec(K, y))
        n = len(self.x)
        self.P = matmul(matsub(eye(n), matmul(K, H)), P)
        return self.x, K

    def step(self, z):
        """One predict→update cycle for measurement ``z``."""
        self.predict()
        return self.update(z)
