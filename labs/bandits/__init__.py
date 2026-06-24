"""bandits — the multi-armed bandit and the exploration/exploitation dilemma.

Five policies on a Bernoulli bandit, scored by cumulative regret:

* ``Random`` / ``Greedy`` — the two failure modes (never learn / fixate early),
  both with **linear** regret.
* ``EpsilonGreedy`` — explore a fixed fraction; bends the curve but keeps paying.
* ``UCB1`` — optimism in the face of uncertainty; **logarithmic** regret.
* ``Thompson`` — Bayesian posterior sampling; logarithmic regret, best constant.

The stateless root of reinforcement learning (one state, K actions) — companion
to this lab's ``qlearning``. Offline, stdlib-only, deterministic.
"""
from .bandit import BernoulliBandit
from .policies import Policy, Random, Greedy, EpsilonGreedy, UCB1, Thompson
from .run import simulate, evaluate, make_policies

__all__ = [
    "BernoulliBandit",
    "Policy", "Random", "Greedy", "EpsilonGreedy", "UCB1", "Thompson",
    "simulate", "evaluate", "make_policies",
]
