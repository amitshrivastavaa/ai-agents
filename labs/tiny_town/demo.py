"""Demo: run the town for 3 days and show one board, the chronicle, and summary.

    python -m labs.tiny_town.demo
"""
from __future__ import annotations

from .render import board_text, chronicle_text, summary_text
from .sim import run


def main() -> int:
    sim = run(days=3, seed="demo", record_boards=True)

    # show the very first "who's where" board as a taste of the live view
    day, phase, occupants = sim.boards[2]  # noon of day 1 — the cafe rush
    print("A snapshot of the town (use --watch for every phase):\n")
    print(board_text(day, phase, occupants))

    print("\n" + "=" * 70)
    print(chronicle_text(sim))
    print(summary_text(sim))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
