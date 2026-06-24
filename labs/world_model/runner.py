"""Run a planner in the (real) world and record what happened."""
from __future__ import annotations

from dataclasses import dataclass, field

from .env import GridWorld


@dataclass
class Episode:
    planner: str
    map_name: str
    outcome: str            # "goal" | "lava" | "timeout"
    steps: int
    total_reward: float
    trajectory: list[tuple]

    @property
    def reached_goal(self) -> bool:
        return self.outcome == "goal"


def run_episode(env: GridWorld, planner, *, map_name: str = "?",
                max_steps: int = 150) -> Episode:
    """The agent acts in the real env, re-planning from each state it reaches."""
    pos = env.start
    traj = [pos]
    total = 0.0
    outcome = "timeout"
    for _ in range(max_steps):
        action = planner.plan(env, pos)
        nxt, reward, done = env.step(pos, action)
        total += reward
        pos = nxt
        traj.append(pos)
        if done:
            outcome = "goal" if pos == env.goal else "lava"
            break
    return Episode(getattr(planner, "name", "?"), map_name, outcome,
                   len(traj) - 1, total, traj)


def compare(env: GridWorld, planners: list, *, map_name: str = "?",
            max_steps: int = 200) -> list[Episode]:
    return [run_episode(env, p, map_name=map_name, max_steps=max_steps) for p in planners]
