"""ASCII rendering of the cart and pole."""
from __future__ import annotations

import math

from .cartpole import CartPole, X_LIMIT
from .policy import Policy


def frame(state: list[float], *, width: int = 41, pole_rows: int = 6) -> str:
    x, _, theta, _ = state
    cx = int((x + X_LIMIT) / (2 * X_LIMIT) * (width - 1))
    cx = max(0, min(width - 1, cx))

    grid = [[" "] * width for _ in range(pole_rows)]
    for r in range(pole_rows):
        height = pole_rows - r                       # rows above the cart
        col = cx + round(math.sin(theta) * height * 1.8)
        if 0 <= col < width:
            grid[r][col] = "O" if r == 0 else "|"

    cart = [" "] * width
    for dx in (-1, 0, 1):
        if 0 <= cx + dx < width:
            cart[cx + dx] = "#"

    lines = ["".join(row) for row in grid]
    lines.append("".join(cart))
    lines.append("=" * width)
    return "\n".join(lines)


def rollout_frames(policy: Policy, *, seed: str = "show", every: int = 16,
                   max_frames: int = 8, max_steps: int = 500):
    """Run an episode and capture (step, frame, theta_deg) snapshots."""
    env = CartPole(max_steps=max_steps)
    state = env.reset(seed=seed)
    shots = [(0, frame(state), math.degrees(state[2]))]
    done = False
    while not done:
        state, _, done = env.step(policy.act(state))
        if env.steps % every == 0 and len(shots) < max_frames:
            shots.append((env.steps, frame(state), math.degrees(state[2])))
    return shots, env.steps
