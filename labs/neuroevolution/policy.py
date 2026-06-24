"""The controller: a tiny [4 → hidden → 1] MLP, evaluated numerically.

Evolution is gradient-free, so the policy only ever does a forward pass — plain
float arithmetic (no autograd graph), which keeps the many rollouts fast. The
whole network is a flat parameter vector the evolution strategy mutates.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .._kernel import rng

N_IN = 4


def param_count(hidden: int) -> int:
    # W1 (hidden×4) + b1 (hidden) + W2 (1×hidden) + b2 (1)
    return hidden * N_IN + hidden + hidden + 1


@dataclass
class Policy:
    params: list[float]
    hidden: int = 6

    @classmethod
    def random(cls, hidden: int = 6, *, seed: str = "pol") -> "Policy":
        r = rng(seed, hidden)
        return cls([r.gauss(0.0, 0.5) for _ in range(param_count(hidden))], hidden)

    def forward(self, state: list[float]) -> float:
        h = self.hidden
        p = self.params
        i = 0
        hid = []
        for j in range(h):                      # hidden layer (tanh)
            acc = p[i + N_IN]                    # bias b1[j] sits after the 4 weights
            for kk in range(N_IN):
                acc += p[i + kk] * state[kk]
            hid.append(math.tanh(acc))
            i += N_IN
        i = h * N_IN + h                         # past W1 and b1
        out = p[i + h]                           # bias b2
        for j in range(h):                       # output layer (linear)
            out += p[i + j] * hid[j]
        return out

    def act(self, state: list[float]) -> int:
        return 1 if self.forward(state) > 0 else 0
