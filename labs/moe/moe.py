"""The mixture-of-experts model: a soft router over specializing experts.

Proper MoE expectation-maximization with an input-space (Gaussian) gate:

* **E-step** — each point's *responsibility* for an expert combines how much the
  gate likes that expert at this input with how well the expert predicts the
  target: ``r ∝ gate_e(x) · 𝒩(y; expert_e(x), σ)``.
* **M-step** — every expert refits by **weighted** least squares (weighted by its
  responsibilities) and recentres its gate on the inputs it now owns.

Experts localize onto different regimes, the gate learns where each applies, and
the soft mixture fits a piecewise problem a single model can't. At inference the
gate sees only ``x`` (top-1 routing = the highest-gate expert).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .data import Dataset
from .experts import LinearExpert


def _mse(fn, X, y) -> float:
    return sum((fn(x) - t) ** 2 for x, t in zip(X, y)) / len(X)


def single_model_error(data: Dataset) -> float:
    """MSE of one global linear model — what a single expert achieves."""
    e = LinearExpert().fit(data.X, data.y)
    return _mse(e.predict, data.X, data.y)


@dataclass
class MixtureOfExperts:
    k: int = 3
    iters: int = 40
    sigma: float = 0.06        # expert noise scale (target likelihood)
    width: float = 0.13        # gate width in input space
    experts: list[LinearExpert] = field(default_factory=list)
    history: list[float] = field(default_factory=list)
    responsibilities: list[list[float]] = field(default_factory=list)

    def gate(self, x: float) -> list[float]:
        gs = [math.exp(-((x - e.centroid) ** 2) / (2 * self.width ** 2)) for e in self.experts]
        s = sum(gs) or 1.0
        return [g / s for g in gs]

    def predict(self, x: float) -> float:
        gs = self.gate(x)
        return sum(g * e.predict(x) for g, e in zip(gs, self.experts))

    def route(self, x: float) -> int:
        gs = self.gate(x)
        return max(range(self.k), key=lambda e: gs[e])

    def predict_top1(self, x: float) -> float:
        return self.experts[self.route(x)].predict(x)

    def train(self, data: Dataset) -> "MixtureOfExperts":
        X, y = data.X, data.y
        n = len(X)
        xmin, xmax = min(X), max(X)
        # init: gate centres spread evenly across the input range (breaks the
        # symmetry that lets two experts collapse onto the same region), each a
        # flat line at the mean y of its starting neighbourhood
        self.experts = []
        for j in range(self.k):
            c = xmin + (j + 0.5) / self.k * (xmax - xmin)
            near = [y[i] for i in range(n) if abs(X[i] - c) < (xmax - xmin) / (2 * self.k)]
            self.experts.append(LinearExpert(0.0, sum(near) / len(near) if near else 0.0, c, 0))

        self.history = []
        R = [[0.0] * self.k for _ in range(n)]
        for _ in range(self.iters):
            # E-step: responsibilities = gate × target-likelihood
            for i in range(n):
                gs = self.gate(X[i])
                w = []
                for e in range(self.k):
                    resid = y[i] - self.experts[e].predict(X[i])
                    w.append(gs[e] * math.exp(-0.5 * (resid / self.sigma) ** 2))
                tot = sum(w) or 1.0
                R[i] = [wi / tot for wi in w]
            # M-step: weighted refit + recentre each expert's gate
            for e in range(self.k):
                ws = [R[i][e] for i in range(n)]
                self.experts[e].fit_weighted(X, y, ws)
                wsum = sum(ws) or 1e-9
                self.experts[e].centroid = sum(ws[i] * X[i] for i in range(n)) / wsum
                self.experts[e].n_owned = sum(1 for i in range(n) if max(range(self.k),
                                              key=lambda z: R[i][z]) == e)
            self.history.append(_mse(self.predict, X, y))
        self.responsibilities = R
        return self

    # -- metrics --
    def train_error(self, data: Dataset) -> float:
        return _mse(self.predict, data.X, data.y)

    def assignment(self) -> list[int]:
        return [max(range(self.k), key=lambda e: r[e]) for r in self.responsibilities]

    def load(self) -> list[int]:
        counts = [0] * self.k
        for a in self.assignment():
            counts[a] += 1
        return counts

    def regions(self) -> list[tuple[float, int]]:
        return sorted((e.centroid, i) for i, e in enumerate(self.experts))
