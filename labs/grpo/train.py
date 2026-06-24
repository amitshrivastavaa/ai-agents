"""GRPO — Group Relative Policy Optimization, from scratch.

The algorithm behind DeepSeek-R1-style reasoning training, in its essential form.
For a prompt ``s`` you sample a **group** of ``G`` responses from the current
policy, score them, and turn the scores into advantages by subtracting the
**group mean** and dividing by the group std:

    Â_i = (r_i − mean(r)) / (std(r) + ε)

— no value network, no critic; the group is its own baseline. Then take a
policy-gradient step:

    θ_s ← θ_s + lr · (1/G) Σ_i  Â_i · (onehot(a_i) − π(·|s))

Responses better than their groupmates are made more likely; worse ones, less.
The contrast we measure: plain REINFORCE (no baseline, ``advantage = reward``)
only ever pushes rewarded actions *up* and has far higher gradient variance, so
it learns slower and less reliably than GRPO's centered, normalized signal.
"""
from __future__ import annotations

import math

from .policy import SoftmaxPolicy


def group_advantages(rewards, normalize=True):
    n = len(rewards)
    mean = sum(rewards) / n
    adv = [r - mean for r in rewards]
    if normalize:
        std = math.sqrt(sum(a * a for a in adv) / n)
        adv = [a / std for a in adv] if std > 1e-8 else [0.0] * n
    return adv


def _pg_step(policy, task, s, group_size, lr, *, baseline):
    """One policy-gradient step. baseline='group' → GRPO; 'none' → REINFORCE."""
    p = policy.probs(s)
    actions = [policy.sample(s) for _ in range(group_size)]
    rewards = [task.reward(s, a) for a in actions]
    if baseline == "group":
        adv = group_advantages(rewards, normalize=True)
    else:
        adv = rewards                                   # no baseline
    grad = [0.0] * policy.A
    for a, ai in zip(actions, adv):
        for b in range(policy.A):
            grad[b] += ai * ((1.0 if b == a else 0.0) - p[b])
    for b in range(policy.A):
        policy.theta[s][b] += lr * grad[b] / group_size
    return sum(rewards) / group_size


def mean_correct_prob(policy, task) -> float:
    """Average probability the policy assigns to the correct answer (smooth)."""
    return sum(policy.probs(s)[task.answers[s]] for s in range(task.S)) / task.S


def accuracy(policy, task) -> float:
    """Fraction of prompts whose greedy (argmax) answer is correct."""
    correct = sum(1 for s in range(task.S) if policy.greedy(s) == task.answers[s])
    return correct / task.S


def train(task, *, steps=300, group_size=12, lr=0.5, method="grpo", seed="run"):
    """Train a fresh policy; return ``(policy, history)`` where history[t] is the
    mean correct-answer probability after step t."""
    policy = SoftmaxPolicy(task.S, task.A, seed=("pol", method, seed))
    baseline = "group" if method == "grpo" else "none"
    history = []
    for t in range(steps):
        s = t % task.S                                  # round-robin over prompts
        _pg_step(policy, task, s, group_size, lr, baseline=baseline)
        history.append(mean_correct_prob(policy, task))
    return policy, history


def steps_to_threshold(history, thr=0.95):
    """First step at which mean correct-prob reaches ``thr`` (or len if never)."""
    for i, v in enumerate(history):
        if v >= thr:
            return i + 1
    return len(history)
