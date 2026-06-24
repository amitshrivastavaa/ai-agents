"""Demo: solve the Sussman anomaly and reverse a tower.

    python -m labs.planner.demo
"""
from __future__ import annotations

from .blocksworld import get_problem
from .render import render_plan, render_state
from .search import plan


def main() -> int:
    print("The Sussman anomaly — the blocks problem that breaks naive planners")
    print("(the two subgoals 'A on B' and 'B on C' interfere):\n")
    p = get_problem("sussman")
    steps, states = plan(p, method="bfs")
    print("start:")
    print(render_state(p.init))
    print("\ngoal: A on B, B on C\n")
    print(f"optimal plan ({len(steps)} actions, found by breadth-first search):")
    print(render_plan(steps))
    print("\nfinal state:")
    print(render_state(states[-1]))

    print("\n" + "=" * 44)
    print("Reverse a tower A/B/C → C/B/A:\n")
    p = get_problem("reverse")
    steps, states = plan(p, method="astar")
    print(f"plan ({len(steps)} actions, A*):")
    print(render_plan(steps))
    print("\nfinal state:")
    print(render_state(states[-1]))
    print("\nNo hand-coded recipe — the planner searches the space of actions and")
    print("finds a sequence whose effects achieve the goal. That's classical AI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
