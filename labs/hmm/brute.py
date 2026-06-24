"""Brute-force reference: enumerate every hidden path. Only for tiny sequences —
used to *prove* Viterbi and forward are correct."""
from __future__ import annotations

import itertools
import math

from .model import HMM


def _path_logprob(model: HMM, path, obs):
    lp = model.logpi[path[0]] + model._logb(path[0], obs[0])
    for t in range(1, len(obs)):
        lp += model.logA[path[t - 1]][path[t]] + model._logb(path[t], obs[t])
    return lp


def best_path(model: HMM, obs):
    """The single most likely path, by exhaustive search."""
    best, best_lp = None, float("-inf")
    for path in itertools.product(range(model.S), repeat=len(obs)):
        lp = _path_logprob(model, path, obs)
        if lp > best_lp:
            best, best_lp = path, lp
    return [model.states[i] for i in best], best_lp


def total_logprob(model: HMM, obs):
    """log P(obs) summed over every path, by exhaustive search."""
    total = 0.0
    for path in itertools.product(range(model.S), repeat=len(obs)):
        total += math.exp(_path_logprob(model, path, obs))
    return math.log(total)
