"""The multi-armed bandit: K arms, each a coin with an unknown win probability.

The cleanest model of the **exploration vs exploitation** dilemma. Every pull you
must choose: play the arm that looks best so far (exploit), or try another to
learn more (explore). You only ever see the reward of the arm you *pulled* — the
counterfactual is hidden — so good play means spending just enough pulls learning
which arm is best, then committing.
"""
from __future__ import annotations

from .._kernel import rng


class BernoulliBandit:
    """K arms; arm i pays 1 with probability ``probs[i]``, else 0."""

    def __init__(self, probs, seed="bandit"):
        self.probs = [float(p) for p in probs]
        self.n = len(self.probs)
        self.best_arm = max(range(self.n), key=lambda i: self.probs[i])
        self.best_prob = self.probs[self.best_arm]
        self._r = rng(seed, tuple(self.probs))

    def pull(self, arm: int) -> float:
        """Sample the reward of pulling ``arm`` (1.0 or 0.0)."""
        return 1.0 if self._r.random() < self.probs[arm] else 0.0

    def gap(self, arm: int) -> float:
        """Expected regret of choosing ``arm``: how much worse than the best arm."""
        return self.best_prob - self.probs[arm]
