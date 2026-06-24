"""A tabular softmax policy π(a|s) — one logit vector per context.

Stands in for an LLM's per-prompt distribution over responses, stripped to its
essence so the GRPO update is visible: the gradient of ``log π(a|s)`` w.r.t. the
logits is simply ``onehot(a) − π(·|s)``.
"""
from __future__ import annotations

import math

from .._kernel import rng


def softmax(logits) -> list[float]:
    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    s = sum(exps)
    return [e / s for e in exps]


class SoftmaxPolicy:
    def __init__(self, n_contexts: int, n_actions: int, seed="grpo"):
        self.S = n_contexts
        self.A = n_actions
        self.theta = [[0.0] * n_actions for _ in range(n_contexts)]
        self._r = rng("grpo-policy", seed)

    def probs(self, s: int) -> list[float]:
        return softmax(self.theta[s])

    def sample(self, s: int) -> int:
        p = self.probs(s)
        x = self._r.random()
        c = 0.0
        for a, pa in enumerate(p):
            c += pa
            if x < c:
                return a
        return self.A - 1

    def greedy(self, s: int) -> int:
        p = self.probs(s)
        return max(range(self.A), key=lambda a: p[a])

    def entropy(self, s: int) -> float:
        return -sum(pa * math.log(pa + 1e-12) for pa in self.probs(s))
