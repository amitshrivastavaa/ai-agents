"""A verifiable-reward task (RLVR) — the setup behind reasoning-model training.

There are ``S`` "prompts" (contexts); each has exactly one correct "answer"
among ``A`` possible actions. The reward is **verifiable**: 1 if the action is
correct, else 0 — no learned reward model, just a checker. The policy must learn
the correct answer for every prompt from this binary signal alone.
"""
from __future__ import annotations

from .._kernel import rng


class VerifiableTask:
    def __init__(self, n_contexts=4, n_actions=4, seed="task"):
        self.S = n_contexts
        self.A = n_actions
        r = rng("grpo-task", seed, n_contexts, n_actions)
        self.answers = [r.randrange(n_actions) for _ in range(n_contexts)]

    def reward(self, s: int, a: int) -> float:
        return 1.0 if a == self.answers[s] else 0.0

    def chance(self) -> float:
        """Reward of a uniform-random policy (= 1/A)."""
        return 1.0 / self.A
