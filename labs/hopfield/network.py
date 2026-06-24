"""Two associative memories: the classic Hopfield net and a modern dense one."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .._kernel import rng


def overlap(a: list[int], b: list[int]) -> float:
    """Fraction of neurons that agree (1.0 == identical)."""
    return sum(1 for x, y in zip(a, b) if x == y) / len(a)


def _sign(x: float) -> int:
    return 1 if x >= 0 else -1


@dataclass
class RecallResult:
    pattern: list[int]
    sweeps: int
    energy_history: list[float]
    label: str | None = None


@dataclass
class ClassicHopfield:
    """Hebbian Hopfield network: W = Σ pₖpₖᵀ (zero diagonal), sign-update recall."""

    n: int = 0
    W: list[list[float]] = field(default_factory=list)
    stored: dict[str, list[int]] = field(default_factory=dict)

    def store(self, patterns: dict[str, list[int]]) -> "ClassicHopfield":
        self.stored = dict(patterns)
        self.n = len(next(iter(patterns.values())))
        W = [[0.0] * self.n for _ in range(self.n)]
        for vec in patterns.values():
            for i in range(self.n):
                vi = vec[i]
                row = W[i]
                for j in range(self.n):
                    if i != j:
                        row[j] += vi * vec[j]
        scale = 1.0 / self.n
        self.W = [[w * scale for w in row] for row in W]
        return self

    def energy(self, s: list[int]) -> float:
        total = 0.0
        for i in range(self.n):
            row = self.W[i]
            si = s[i]
            for j in range(self.n):
                total += row[j] * si * s[j]
        return -0.5 * total

    def recall(self, cue: list[int], *, max_sweeps: int = 20, seed: str = "recall") -> RecallResult:
        s = list(cue)
        energies = [self.energy(s)]
        sweeps = 0
        for sweep in range(max_sweeps):
            order = list(range(self.n))
            rng(seed, sweep).shuffle(order)  # asynchronous updates converge cleanly
            changed = False
            for i in order:
                net = sum(self.W[i][j] * s[j] for j in range(self.n))
                new = _sign(net)
                if new != s[i]:
                    s[i] = new
                    changed = True
            energies.append(self.energy(s))
            sweeps = sweep + 1
            if not changed:
                break
        return RecallResult(s, sweeps, energies, self.classify(s))

    def classify(self, s: list[int]) -> str | None:
        best, best_ov = None, -1.0
        for name, vec in self.stored.items():
            ov = overlap(s, vec)
            if ov > best_ov:
                best, best_ov = name, ov
        return best


@dataclass
class ModernHopfield:
    """Dense associative memory: softmax retrieval over stored patterns.

    out = Σ softmax(β · ⟨pₖ, query⟩) pₖ, then binarized. With large β this snaps
    to the single nearest pattern even when many are stored — the high-capacity,
    "Hopfield ≈ attention" formulation.
    """

    beta: float = 8.0
    stored: dict[str, list[int]] = field(default_factory=dict)

    def store(self, patterns: dict[str, list[int]]) -> "ModernHopfield":
        self.stored = dict(patterns)
        return self

    def recall(self, cue: list[int], *, steps: int = 3) -> RecallResult:
        names = list(self.stored)
        mats = [self.stored[n] for n in names]
        n = len(cue)
        s = list(cue)
        for _ in range(steps):
            scores = [self.beta * sum(p[i] * s[i] for i in range(n)) / n for p in mats]
            m = max(scores)
            exps = [math.exp(sc - m) for sc in scores]
            z = sum(exps) or 1.0
            weights = [e / z for e in exps]
            out = [sum(weights[k] * mats[k][i] for k in range(len(mats))) for i in range(n)]
            new = [_sign(o) for o in out]
            if new == s:
                break
            s = new
        return RecallResult(s, steps, [], self.classify(s))

    def classify(self, s: list[int]) -> str | None:
        best, best_ov = None, -1.0
        for name, vec in self.stored.items():
            ov = overlap(s, vec)
            if ov > best_ov:
                best, best_ov = name, ov
        return best
