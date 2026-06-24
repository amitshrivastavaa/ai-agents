"""CLI for the reaction-diffusion morphogenesis sandbox.

    python -m labs.morphogenesis.cli run --pattern mitosis
    python -m labs.morphogenesis.cli run --pattern coral --steps 4000
    python -m labs.morphogenesis.cli run --pattern maze --heal
    python -m labs.morphogenesis.cli list
"""
from __future__ import annotations

import argparse
import sys

from .grid import Grid, PRESETS, get_preset
from .render import shade


def _cmd_run(args) -> int:
    _, _, desc = get_preset(args.pattern)
    g = Grid.from_preset(args.pattern, w=args.w, h=args.h, seed=args.seed)
    frames = max(1, args.frames)
    per = max(1, args.steps // frames)

    print(f"# {args.pattern} — {desc}  ({g.w}×{g.h}, {args.steps} steps)\n")
    for f in range(frames):
        g.step(per)
        if args.frames > 1:
            print(f"— step {g.steps_run} (activity {g.activity():.3f}) —")
            print(shade(g))
            print()
    if args.frames == 1:
        print(shade(g))

    if args.heal:
        x0, y0 = g.w // 2 - 8, g.h // 2 - 5
        x1, y1 = g.w // 2 + 8, g.h // 2 + 5
        g.damage(x0=x0, y0=y0, x1=x1, y1=y1)
        print("\n— after damage (a hole wiped in the pattern) —")
        print(shade(g))
        g.step(max(1500, args.steps // 2))
        print(f"\n— after healing ({g.steps_run} total steps): the hole regrows —")
        print(shade(g))
    return 0


def _cmd_list(_args) -> int:
    print("Patterns (Gray-Scott regimes):\n")
    for name, (F, k, desc) in PRESETS.items():
        print(f"  {name:<9} F={F:.4f} k={k:.4f}  — {desc}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="morphogenesis",
        description="Self-organizing, self-healing reaction-diffusion patterns.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run")
    p.add_argument("--pattern", default="mitosis")
    p.add_argument("--steps", type=int, default=3000)
    p.add_argument("--frames", type=int, default=1, help="show N evolution snapshots")
    p.add_argument("--w", type=int, default=56)
    p.add_argument("--h", type=int, default=24)
    p.add_argument("--seed", default="morph")
    p.add_argument("--heal", action="store_true", help="damage the pattern, then watch it heal")
    p.set_defaults(func=_cmd_run)

    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
