"""CLI for the STRIPS blocks-world planner.

    python -m labs.planner.cli solve --problem sussman
    python -m labs.planner.cli solve --problem reverse --trace
    python -m labs.planner.cli solve --problem build4 --astar
    python -m labs.planner.cli list
"""
from __future__ import annotations

import argparse
import sys

from .blocksworld import PROBLEMS, get_problem
from .render import render_plan, render_state
from .search import plan
from .strips import satisfies


def _cmd_solve(args) -> int:
    p = get_problem(args.problem)
    method = "astar" if args.astar else "bfs"
    steps, states = plan(p, method=method)
    print(f"# blocks-world '{p.name}'  ({method.upper()})\n")
    print("start:")
    print(render_state(p.init))
    if steps is None:
        print("\n  no plan found.")
        return 1
    print(f"\nplan ({len(steps)} actions):")
    print(render_plan(steps))
    if args.trace:
        for i, (a, st) in enumerate(zip(steps, states[1:]), 1):
            print(f"\n  after {i}. {a}:")
            print(render_state(st))
    print("\ngoal reached:" if satisfies(states[-1], p.goal) else "\nFINAL (goal NOT reached):")
    print(render_state(states[-1]))
    return 0


def _cmd_list(_args) -> int:
    for name, p in PROBLEMS.items():
        print(f"  {name:<8} {len(p.blocks)} blocks")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="planner", description="A STRIPS planner that solves blocks-world problems.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("solve")
    p.add_argument("--problem", default="sussman")
    p.add_argument("--astar", action="store_true", help="use A* instead of BFS")
    p.add_argument("--trace", action="store_true", help="show the state after each action")
    p.set_defaults(func=_cmd_solve)

    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
