"""A discrete Hidden Markov Model with the three classic algorithms.

A HMM is a Markov chain over hidden **states** you can't see, each emitting an
**observation** you can. Given a sequence of observations, three exact
dynamic-programming algorithms answer three questions — all in log space so long
sequences don't underflow:

* **Viterbi** — the single most likely hidden path (max-product).
* **forward** — the total probability of the observations (sum-product).
* **forward-backward** — the per-position posterior over states (smoothing).
"""
from __future__ import annotations

import math

NEG_INF = float("-inf")


def _log(p):
    return math.log(p) if p > 0 else NEG_INF


def logsumexp(xs):
    m = max(xs)
    if m == NEG_INF:
        return NEG_INF
    return m + math.log(sum(math.exp(x - m) for x in xs))


class HMM:
    def __init__(self, states, init, trans, emit):
        """``init[s]`` start prob, ``trans[s][s2]`` transition, ``emit[s][o]``
        emission probability."""
        self.states = list(states)
        self.S = len(self.states)
        self.idx = {s: i for i, s in enumerate(self.states)}
        self.logpi = [_log(init[s]) for s in self.states]
        self.logA = [[_log(trans[s].get(s2, 0.0)) for s2 in self.states]
                     for s in self.states]
        self.emit = emit
        self.logB = [{o: _log(p) for o, p in emit[s].items()} for s in self.states]

    def _logb(self, i, o):
        return self.logB[i].get(o, NEG_INF)

    def viterbi(self, obs):
        """Most likely hidden-state sequence and its log-probability."""
        n = len(obs)
        delta = [self.logpi[i] + self._logb(i, obs[0]) for i in range(self.S)]
        back = [[0] * self.S for _ in range(n)]
        for t in range(1, n):
            new = [NEG_INF] * self.S
            for j in range(self.S):
                best_i, best = 0, NEG_INF
                for i in range(self.S):
                    val = delta[i] + self.logA[i][j]
                    if val > best:
                        best, best_i = val, i
                new[j] = best + self._logb(j, obs[t])
                back[t][j] = best_i
            delta = new
        last = max(range(self.S), key=lambda i: delta[i])
        path = [last]
        for t in range(n - 1, 0, -1):
            last = back[t][last]
            path.append(last)
        path.reverse()
        return [self.states[i] for i in path], max(delta)

    def forward(self, obs):
        """Log P(observations) — summed over all hidden paths."""
        alpha = [self.logpi[i] + self._logb(i, obs[0]) for i in range(self.S)]
        for t in range(1, len(obs)):
            alpha = [logsumexp([alpha[i] + self.logA[i][j] for i in range(self.S)])
                     + self._logb(j, obs[t]) for j in range(self.S)]
        return logsumexp(alpha)

    def _alphas(self, obs):
        out = [[self.logpi[i] + self._logb(i, obs[0]) for i in range(self.S)]]
        for t in range(1, len(obs)):
            prev = out[-1]
            out.append([logsumexp([prev[i] + self.logA[i][j] for i in range(self.S)])
                        + self._logb(j, obs[t]) for j in range(self.S)])
        return out

    def _betas(self, obs):
        n = len(obs)
        out = [[0.0] * self.S for _ in range(n)]
        for t in range(n - 2, -1, -1):
            for i in range(self.S):
                out[t][i] = logsumexp([self.logA[i][j] + self._logb(j, obs[t + 1])
                                       + out[t + 1][j] for j in range(self.S)])
        return out

    def forward_backward(self, obs):
        """Per-position posterior ``P(state | all observations)`` (list of dicts)."""
        alpha, beta = self._alphas(obs), self._betas(obs)
        logp = logsumexp(alpha[-1])
        post = []
        for t in range(len(obs)):
            row = {self.states[i]: math.exp(alpha[t][i] + beta[t][i] - logp)
                   for i in range(self.S)}
            post.append(row)
        return post
