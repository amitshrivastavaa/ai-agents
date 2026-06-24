"""ASCII rendering of blocks-world states and plans."""
from __future__ import annotations

from .strips import State


def towers(state: State):
    """Return (stacks, holding): each stack is bottom→top; holding is a list."""
    on = {f[1]: f[2] for f in state if f[0] == "on"}        # x on y
    above = {y: x for x, y in on.items()}                   # what sits on y
    bases = sorted(f[1] for f in state if f[0] == "ontable")
    holding = sorted(f[1] for f in state if f[0] == "holding")
    stacks = []
    for b in bases:
        stack = [b]
        cur = b
        while cur in above:
            cur = above[cur]
            stack.append(cur)
        stacks.append(stack)
    return stacks, holding


def render_state(state: State) -> str:
    stacks, holding = towers(state)
    height = max((len(s) for s in stacks), default=0)
    lines = []
    for level in range(height - 1, -1, -1):
        cells = [f"[{s[level]}]" if level < len(s) else "   " for s in stacks]
        lines.append(" ".join(cells))
    lines.append(" ".join("───" for _ in stacks) or "───")
    hand = ", ".join(holding) if holding else "empty"
    lines.append(f"hand: {hand}")
    return "\n".join(lines)


def render_plan(steps) -> str:
    return "\n".join(f"  {i:>2}. {a}" for i, a in enumerate(steps, 1))
