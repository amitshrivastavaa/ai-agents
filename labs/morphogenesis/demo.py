"""Demo: grow a pattern from a seed, then damage it and watch it heal.

    python -m labs.morphogenesis.demo
"""
from __future__ import annotations

from .grid import Grid
from .render import shade


def main() -> int:
    g = Grid.from_preset("mitosis", w=54, h=22, seed="demo")
    print("Gray-Scott 'mitosis' — from a seed, the field organizes itself:\n")
    for step_to in (600, 1800, 3200):
        g.step(step_to - g.steps_run)
        print(f"— {g.steps_run} steps (activity {g.activity():.3f}) —")
        print(shade(g))
        print()

    print("Now wipe a hole through the middle …\n")
    g.damage(x0=18, y0=6, x1=36, y1=16)
    print(shade(g))

    g.step(1600)
    print(f"\n… and it heals — the pattern regrows into the gap ({g.steps_run} steps):\n")
    print(shade(g))

    print("\nNo controller, no training — structure and repair emerge from two")
    print("chemicals diffusing and reacting. Turing's morphogenesis; the lineage")
    print("that leads to Growing Neural Cellular Automata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
