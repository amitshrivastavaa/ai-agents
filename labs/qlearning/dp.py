"""Value iteration — the dynamic-programming optimum, for checking Q-learning."""
from __future__ import annotations

from .gridworld import ACTIONS, GridWorld


def value_iteration(env: GridWorld, *, gamma: float = 0.95, theta: float = 1e-6):
    """Return (V, policy): optimal state values and the greedy optimal policy."""
    V = {s: 0.0 for s in env.states()}
    while True:
        delta = 0.0
        for s in env.states():
            if env.is_terminal(s):
                continue
            best = max(_backup(env, s, a, V, gamma) for a in ACTIONS)
            delta = max(delta, abs(best - V[s]))
            V[s] = best
        if delta < theta:
            break
    policy = {}
    for s in env.states():
        if env.is_terminal(s):
            continue
        policy[s] = max(range(len(ACTIONS)),
                        key=lambda a: _backup(env, s, ACTIONS[a], V, gamma))
    return V, policy


def _backup(env: GridWorld, s, action: str, V, gamma: float) -> float:
    s2, reward, done = env.step(s, action)
    return reward + (0.0 if done else gamma * V[s2])
