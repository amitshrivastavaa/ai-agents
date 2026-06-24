"""Expert models: simple 1-D linear regressors fit by least squares."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LinearExpert:
    slope: float = 0.0
    intercept: float = 0.0
    centroid: float = 0.0     # mean x of the points it owns — used for routing
    n_owned: int = 0

    def fit(self, xs: list[float], ys: list[float]) -> "LinearExpert":
        n = len(xs)
        self.n_owned = n
        if n == 0:
            return self
        mx = sum(xs) / n
        my = sum(ys) / n
        self.centroid = mx
        if n == 1:
            self.slope, self.intercept = 0.0, ys[0]
            return self
        var = sum((x - mx) ** 2 for x in xs)
        if var < 1e-12:                      # all x identical → predict the mean
            self.slope, self.intercept = 0.0, my
            return self
        cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        self.slope = cov / var
        self.intercept = my - self.slope * mx
        return self

    def fit_weighted(self, xs: list[float], ys: list[float],
                     ws: list[float]) -> "LinearExpert":
        """Weighted least squares — the M-step of mixture-of-experts EM."""
        W = sum(ws)
        if W < 1e-9:
            return self
        mx = sum(w * x for w, x in zip(ws, xs)) / W
        my = sum(w * y for w, y in zip(ws, ys)) / W
        var = sum(w * (x - mx) ** 2 for w, x in zip(ws, xs))
        if var < 1e-12:
            self.slope, self.intercept = 0.0, my
            return self
        cov = sum(w * (x - mx) * (y - my) for w, x, y in zip(ws, xs, ys))
        self.slope = cov / var
        self.intercept = my - self.slope * mx
        return self

    def predict(self, x: float) -> float:
        return self.slope * x + self.intercept
