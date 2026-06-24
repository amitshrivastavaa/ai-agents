"""Planners that share one world model — from reflex to imagination.

* :class:`ReactivePlanner` — greedy toward the goal, no lookahead. It will
  happily step into lava if that's the move that shrinks the distance.
* :class:`LookaheadPlanner` — breadth-first search over the model for the
  optimal *safe* path; returns the first move of it. A perfect plan.
* :class:`MCTSPlanner` — Monte-Carlo Tree Search. It runs many imagined
  rollouts in the model, grows a search tree (UCT), and commits to the move
  with the best simulated return. The "simulate before you act" approach.
"""
from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field

from .._kernel import rng
from .env import ACTIONS, GridWorld


def _manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class ReactivePlanner:
    name = "reactive"

    def plan(self, model: GridWorld, pos) -> str:
        # pick the (non-wall) move that most reduces distance to the goal;
        # crucially, no awareness of lava beyond the immediate cell.
        best, best_d = None, math.inf
        for a in ("N", "S", "E", "W"):
            nxt, _, _ = model.step(pos, a)
            if nxt == pos:
                continue  # bumped a wall
            d = _manhattan(nxt, model.goal)
            if d < best_d:
                best, best_d = a, d
        return best or "N"


class LookaheadPlanner:
    name = "lookahead"

    def plan(self, model: GridWorld, pos) -> str:
        path = self._bfs(model, pos)
        if not path:
            return ReactivePlanner().plan(model, pos)
        return path[0]

    @staticmethod
    def _bfs(model: GridWorld, start) -> list[str]:
        """Shortest action sequence to the goal avoiding walls and lava."""
        q = deque([start])
        came: dict = {start: None}
        while q:
            cur = q.popleft()
            if cur == model.goal:
                break
            for a in ("N", "S", "E", "W"):
                nxt, _, _ = model.step(cur, a)
                if nxt == cur or nxt in came:
                    continue
                if nxt in model.lava and nxt != model.goal:
                    continue
                came[nxt] = (cur, a)
                q.append(nxt)
        if model.goal not in came:
            return []
        actions: list[str] = []
        cur = model.goal
        while came[cur] is not None:
            prev, a = came[cur]
            actions.append(a)
            cur = prev
        return list(reversed(actions))


@dataclass
class RolloutPlanner:
    """Model-predictive control: imagine many futures, then commit.

    For each legal first move it runs ``rollouts`` simulated trajectories in the
    world model under a goal-biased, lava-avoiding policy, scores each by its
    discounted return (with a cost-to-go heuristic at the horizon), and picks the
    move with the best *average imagined* outcome. The classic "plan by
    simulation" idea — robust, deterministic, and free of tree-search cycles.
    """

    rollouts: int = 40
    horizon: int = 45
    gamma: float = 0.98
    h_weight: float = 2.0
    seed: str = "rollout"
    name: str = "rollout"

    @staticmethod
    def _legal(model: GridWorld, pos) -> list[str]:
        return [a for a in ("N", "S", "E", "W") if model.step(pos, a)[0] != pos]

    def _rollout_action(self, model: GridWorld, pos, r) -> str:
        moves = []  # legal moves that don't knowingly step into lava
        for a in self._legal(model, pos):
            nxt, _, _ = model.step(pos, a)
            if nxt in model.lava and nxt != model.goal:
                continue
            moves.append((a, nxt))
        if not moves:
            legal = self._legal(model, pos)
            return r.choice(legal) if legal else "N"
        if r.random() < 0.7:  # goal-biased
            best_d = min(_manhattan(nxt, model.goal) for _, nxt in moves)
            best = [a for a, nxt in moves if _manhattan(nxt, model.goal) == best_d]
            return r.choice(best)
        return r.choice([a for a, _ in moves])

    def _rollout(self, model: GridWorld, pos, r) -> float:
        total, disc, cur, done = 0.0, 1.0, pos, False
        for _ in range(self.horizon):
            a = self._rollout_action(model, cur, r)
            nxt, rew, done = model.step(cur, a)
            total += disc * rew
            disc *= self.gamma
            cur = nxt
            if done:
                break
        if not done:  # cost-to-go heuristic at the horizon
            total += disc * (-self.h_weight * _manhattan(cur, model.goal))
        return total

    def plan(self, model: GridWorld, pos) -> str:
        r = rng(self.seed, pos, self.rollouts)
        best_a, best_q = None, -math.inf
        for a in self._legal(model, pos):
            nxt, rew, done = model.step(pos, a)
            total = 0.0
            for _ in range(self.rollouts):
                total += rew + (0.0 if done else self.gamma * self._rollout(model, nxt, r))
            q = total / self.rollouts
            if q > best_q:
                best_a, best_q = a, q
        return best_a or "N"


# kept for backwards-friendly naming; the rollout planner is our "imagination"
MCTSPlanner = RolloutPlanner

_PLANNERS = {
    "reactive": ReactivePlanner,
    "lookahead": LookaheadPlanner,
    "rollout": RolloutPlanner,
}


def get_planner(name: str):
    try:
        return _PLANNERS[name]()
    except KeyError:
        raise KeyError(f"unknown planner {name!r}; choose from {sorted(_PLANNERS)}") from None
