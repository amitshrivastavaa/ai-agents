"""ASCII rendering of the learned policy (arrows) and value function (heatmap)."""
from __future__ import annotations

from .agent import QLearningAgent
from .gridworld import GridWorld

_ARROWS = ("↑", "↓", "←", "→")          # matches ACTIONS order
_RAMP = " .:-=+*#%@"


def policy_arrows(env: GridWorld, agent: QLearningAgent) -> str:
    rows = []
    for y in range(env.height):
        row = []
        for x in range(env.width):
            s = (x, y)
            if s in env.walls:
                row.append("█")
            elif s == env.goal:
                row.append("G")
            elif s in env.pits:
                row.append("X")
            elif s == env.start:
                row.append("S")
            else:
                row.append(_ARROWS[agent.greedy_action(s)])
        rows.append("".join(row))
    return "\n".join(rows)


def value_heatmap(env: GridWorld, values) -> str:
    cells = [values[s] for s in env.states() if not env.is_terminal(s)]
    lo, hi = (min(cells), max(cells)) if cells else (0.0, 1.0)
    span = (hi - lo) or 1.0
    rows = []
    for y in range(env.height):
        row = []
        for x in range(env.width):
            s = (x, y)
            if s in env.walls:
                row.append("██")
            elif s == env.goal:
                row.append(" G")
            elif s in env.pits:
                row.append(" X")
            else:
                v = values.get(s, lo)
                level = int((v - lo) / span * (len(_RAMP) - 1))
                row.append(_RAMP[level] * 2)
        rows.append("".join(row))
    return "\n".join(rows)
