"""State-space search: breadth-first (optimal) and A* (heuristic-guided)."""
from __future__ import annotations

import heapq
from collections import deque

from .blocksworld import ground_actions
from .strips import Action, apply_action


def _reconstruct(came, state) -> list[Action]:
    plan = []
    while came[state] is not None:
        prev, action = came[state]
        plan.append(action)
        state = prev
    return list(reversed(plan))


def bfs_plan(actions, init, goal, *, max_expansions: int = 300_000):
    """Optimal (fewest-actions) plan via breadth-first search, or None."""
    if goal <= init:
        return []
    frontier = deque([init])
    came = {init: None}
    expansions = 0
    while frontier and expansions < max_expansions:
        s = frontier.popleft()
        expansions += 1
        for a in actions:
            if a.pre <= s:
                s2 = apply_action(a, s)
                if s2 not in came:
                    came[s2] = (s, a)
                    if goal <= s2:
                        return _reconstruct(came, s2)
                    frontier.append(s2)
    return None


def astar_plan(actions, init, goal, *, max_expansions: int = 300_000):
    """A* with the goal-count heuristic h(s) = |goal − s| (often optimal here)."""
    def h(s):
        return len(goal - s)

    counter = 0
    pq = [(h(init), 0, counter, init)]
    best = {init: 0}
    came = {init: None}
    expansions = 0
    while pq and expansions < max_expansions:
        _, g, _, s = heapq.heappop(pq)
        if goal <= s:
            return _reconstruct(came, s)
        if g > best.get(s, 1 << 30):
            continue
        expansions += 1
        for a in actions:
            if a.pre <= s:
                s2 = apply_action(a, s)
                ng = g + 1
                if ng < best.get(s2, 1 << 30):
                    best[s2] = ng
                    came[s2] = (s, a)
                    counter += 1
                    heapq.heappush(pq, (ng + h(s2), ng, counter, s2))
    return None


def plan(problem, *, method: str = "bfs"):
    """Return (plan, states) where states traces init → … → goal, or (None, [])."""
    actions = ground_actions(problem.blocks)
    solver = astar_plan if method == "astar" else bfs_plan
    steps = solver(actions, problem.init, problem.goal)
    if steps is None:
        return None, []
    states = [problem.init]
    s = problem.init
    for a in steps:
        s = apply_action(a, s)
        states.append(s)
    return steps, states
