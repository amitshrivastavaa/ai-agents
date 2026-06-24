"""planner — a classical STRIPS planner that reasons about actions and goals.

The other half of AI from the from-scratch ML in this lab: symbolic, goal-
directed planning. A world is a set of true facts; an **action** has
preconditions and add/delete effects; a **plan** is a sequence of actions that
transforms the start state into one satisfying the goal. The planner finds that
sequence by searching the state space (breadth-first for optimal plans, A* with
a heuristic for speed).

It solves blocks-world problems including the famous **Sussman anomaly** — the
instance that breaks naive goal-by-goal planners because the subgoals interfere.
Fully offline, deterministic; renders the block towers and the plan in ASCII.
"""
from .strips import Action, apply_action, applicable
from .blocksworld import PROBLEMS, ground_actions, get_problem
from .search import plan

__all__ = ["Action", "apply_action", "applicable", "PROBLEMS",
           "ground_actions", "get_problem", "plan"]
