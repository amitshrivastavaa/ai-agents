"""CLI for the tiny_town generative-agent simulation.

    python -m labs.tiny_town.cli --days 3
    python -m labs.tiny_town.cli --days 2 --watch        # show the who's-where board
    python -m labs.tiny_town.cli --days 3 --json
"""
from __future__ import annotations

import argparse
import json
import sys

from .render import board_text, chronicle_text, summary_text
from .sim import run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tiny_town",
        description="Simulate a tiny town of generative agents and watch relationships emerge.",
    )
    parser.add_argument("--days", type=int, default=2)
    parser.add_argument("--seed", default="town")
    parser.add_argument("--watch", action="store_true",
                        help="print the who's-where board for every phase")
    parser.add_argument("--quiet-reflections", action="store_true",
                        help="hide end-of-day reflections from the chronicle")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    sim = run(days=args.days, seed=args.seed, record_boards=args.watch)

    if args.json:
        print(json.dumps(sim.to_dict(), indent=2))
        return 0

    if args.watch:
        for day, phase, occupants in sim.boards:
            print(board_text(day, phase, occupants))
            print()

    print("📜 Chronicle")
    print(chronicle_text(sim, include_reflections=not args.quiet_reflections))
    print(summary_text(sim))
    return 0


if __name__ == "__main__":
    sys.exit(main())
