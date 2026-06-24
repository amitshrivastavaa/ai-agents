"""Bandit policies — five ways to trade off exploration and exploitation.

* **Random**         — pull uniformly at random. The do-nothing baseline.
* **Greedy**         — always exploit the best-looking arm. Often locks onto a
                       wrong arm forever (linear regret).
* **EpsilonGreedy**  — exploit, but explore a random arm an ε fraction of the
                       time. Fixed ε never stops exploring → still linear regret,
                       just a shallower slope.
* **UCB1**           — optimism under uncertainty: pull the arm with the best
                       *upper confidence bound* ``mean + sqrt(2·ln t / n)``.
                       Provably **logarithmic** regret (Auer et al. 2002).
* **Thompson**       — Bayesian: keep a Beta posterior per arm, sample from each,
                       pull the winner. Matches UCB's logarithmic regret, usually
                       with a better constant.
"""
from __future__ import annotations

import math

from .._kernel import rng


class Policy:
    def __init__(self, n: int, seed="pol"):
        self.n = n
        self.counts = [0] * n
        self.values = [0.0] * n          # running empirical mean reward per arm
        self._r = rng("policy", seed, n)

    def _argmax(self, scores) -> int:
        best = max(scores)
        cands = [i for i, s in enumerate(scores) if s >= best - 1e-12]
        return cands[0] if len(cands) == 1 else self._r.choice(cands)

    def update(self, arm: int, reward: float) -> None:
        self.counts[arm] += 1
        n = self.counts[arm]
        self.values[arm] += (reward - self.values[arm]) / n      # incremental mean

    def select(self, t: int) -> int:                              # pragma: no cover
        raise NotImplementedError


class Random(Policy):
    def select(self, t: int) -> int:
        return self._r.randrange(self.n)


class EpsilonGreedy(Policy):
    def __init__(self, n: int, epsilon=0.1, seed="eg"):
        super().__init__(n, seed=(seed, epsilon))
        self.epsilon = epsilon

    def select(self, t: int) -> int:
        if self._r.random() < self.epsilon:
            return self._r.randrange(self.n)
        return self._argmax(self.values)


class Greedy(EpsilonGreedy):
    def __init__(self, n: int, seed="greedy"):
        super().__init__(n, epsilon=0.0, seed=seed)


class UCB1(Policy):
    def select(self, t: int) -> int:
        for i in range(self.n):
            if self.counts[i] == 0:          # try every arm once first
                return i
        scores = [self.values[i] + math.sqrt(2.0 * math.log(t) / self.counts[i])
                  for i in range(self.n)]
        return self._argmax(scores)


class Thompson(Policy):
    def __init__(self, n: int, seed="ts"):
        super().__init__(n, seed=seed)
        self.alpha = [1.0] * n               # Beta(1,1) = uniform prior
        self.beta = [1.0] * n

    def select(self, t: int) -> int:
        samples = [self._r.betavariate(self.alpha[i], self.beta[i])
                   for i in range(self.n)]
        return self._argmax(samples)

    def update(self, arm: int, reward: float) -> None:
        super().update(arm, reward)
        if reward >= 0.5:
            self.alpha[arm] += 1.0
        else:
            self.beta[arm] += 1.0
