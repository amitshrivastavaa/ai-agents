"""The dishonest casino — the canonical HMM example.

A dealer secretly switches between a **fair** die and a **loaded** one (which
rolls 6 half the time). You see only the rolls; the hidden state is which die was
used. Viterbi recovers when the loaded die was in play.
"""
from __future__ import annotations

from .._kernel import rng
from .model import HMM

FACES = "123456"


def casino_hmm(p_stay_fair=0.95, p_stay_loaded=0.90, load=0.5):
    fair = {f: 1.0 / 6.0 for f in FACES}
    loaded = {f: (load if f == "6" else (1.0 - load) / 5.0) for f in FACES}
    return HMM(
        states=["F", "L"],
        init={"F": 0.5, "L": 0.5},
        trans={"F": {"F": p_stay_fair, "L": 1 - p_stay_fair},
               "L": {"L": p_stay_loaded, "F": 1 - p_stay_loaded}},
        emit={"F": fair, "L": loaded},
    )


def sample(model: HMM, n=200, seed="casino"):
    """Generate ``(rolls, hidden_states)`` from the model."""
    r = rng("hmm-casino", seed, n)

    def pick(dist):
        x = r.random()
        c = 0.0
        for k, p in dist.items():
            c += p
            if x < c:
                return k
        return k

    trans = {s: {model.states[j]: __exp(model.logA[i][j])
                 for j in range(model.S)} for i, s in enumerate(model.states)}
    init = {s: __exp(model.logpi[i]) for i, s in enumerate(model.states)}

    state = pick(init)
    rolls, hidden = [], []
    for _ in range(n):
        rolls.append(pick(model.emit[state]))
        hidden.append(state)
        state = pick(trans[state])
    return rolls, hidden


def __exp(x):
    import math
    return math.exp(x) if x != float("-inf") else 0.0


def accuracy(true_states, pred_states):
    return sum(1 for a, b in zip(true_states, pred_states) if a == b) / len(true_states)
