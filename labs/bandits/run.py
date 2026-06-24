"""Simulate policies on a bandit and measure cumulative (expected) regret."""
from __future__ import annotations

from .bandit import BernoulliBandit
from .policies import Random, Greedy, EpsilonGreedy, UCB1, Thompson


def simulate(bandit: BernoulliBandit, policy, horizon: int):
    """Run ``policy`` on ``bandit`` for ``horizon`` pulls.

    Returns ``(cumulative_regret, chosen_arms)``. Regret is *expected* regret —
    summed true gaps ``best_prob − prob[chosen]`` — so the curve is smooth and
    measures decision quality, not reward luck.
    """
    regret = 0.0
    cum: list[float] = []
    chosen: list[int] = []
    for t in range(1, horizon + 1):
        arm = policy.select(t)
        reward = bandit.pull(arm)
        policy.update(arm, reward)
        regret += bandit.gap(arm)
        cum.append(regret)
        chosen.append(arm)
    return cum, chosen


def make_policies(n: int, seed):
    """The five policies, each freshly seeded for one run."""
    return {
        "random": Random(n, seed=("random", seed)),
        "greedy": Greedy(n, seed=("greedy", seed)),
        "ε-greedy(.1)": EpsilonGreedy(n, epsilon=0.1, seed=("eg", seed)),
        "UCB1": UCB1(n, seed=("ucb", seed)),
        "Thompson": Thompson(n, seed=("ts", seed)),
    }


def evaluate(probs, horizon=2000, runs=60):
    """Average each policy's regret curve + %-optimal-pulls over ``runs`` seeds."""
    names = list(make_policies(len(probs), 0).keys())
    sums = {k: [0.0] * horizon for k in names}
    opt = {k: 0 for k in names}
    for s in range(runs):
        bandit = BernoulliBandit(probs, seed=("eval", s))
        for name, pol in make_policies(len(probs), s).items():
            cum, chosen = simulate(bandit, pol, horizon)
            row = sums[name]
            for i, v in enumerate(cum):
                row[i] += v
            opt[name] += sum(1 for a in chosen if a == bandit.best_arm)
    avg = {k: [v / runs for v in sums[k]] for k in names}
    pct_opt = {k: opt[k] / (runs * horizon) for k in names}
    return avg, pct_opt
