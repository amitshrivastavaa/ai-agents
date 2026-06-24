"""CLI for the flow-matching lab.

    python -m labs.flow.cli sample --target ring --steps 16
    python -m labs.flow.cli steps --target spiral
    python -m labs.flow.cli list
"""
from __future__ import annotations

import argparse
import sys

from . import targets
from .demo import scatter, _side_by_side
from .sample import generate, nearest_data_rmse, mode_coverage


def _cmd_sample(args) -> int:
    data = targets.get(args.target)
    gen = generate(data, args.n, steps=args.steps, method=args.method, seed=args.seed)
    print(f"# flow matching → {args.target}  ({args.steps} {args.method} steps)\n")
    print("   target data                 generated samples")
    print(_side_by_side(scatter(data, ch="#"), scatter(gen, ch="•")))
    print(f"\n   nearest-data RMSE = {nearest_data_rmse(gen, data):.3f}   "
          f"mode coverage = {mode_coverage(gen, data) * 100:.0f}%")
    return 0


def _cmd_steps(args) -> int:
    data = targets.get(args.target)
    print(f"# error vs ODE steps → {args.target}\n")
    rmses = [(s, nearest_data_rmse(generate(data, args.n, steps=s, seed=args.seed), data))
             for s in (1, 2, 4, 8, 16, 32, 64)]
    hi = max(r for _, r in rmses) or 1.0
    for s, r in rmses:
        bar = "█" * round(40 * r / hi)
        print(f"  {s:3d} steps  {bar:<40} {r:.4f}")
    print("\n  a deterministic straight-path ODE converges in a handful of steps.")
    return 0


def _cmd_list(args) -> int:
    print("targets:", ", ".join(targets.NAMES))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="flow", description="Flow matching / rectified flow from scratch.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("sample", help="flow noise onto a target shape")
    p.add_argument("--target", default="ring", choices=targets.NAMES)
    p.add_argument("--steps", type=int, default=16)
    p.add_argument("--n", type=int, default=220)
    p.add_argument("--method", default="euler", choices=("euler", "midpoint"))
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_sample)

    p = sub.add_parser("steps", help="accuracy vs number of ODE steps")
    p.add_argument("--target", default="ring", choices=targets.NAMES)
    p.add_argument("--n", type=int, default=160)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_steps)

    p = sub.add_parser("list", help="available targets")
    p.set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
