"""CLI for the symbolic-regression engine.

    python -m labs.symbolic_regression.cli discover --target quadratic
    python -m labs.symbolic_regression.cli discover --target damped --gens 60
    python -m labs.symbolic_regression.cli list
"""
from __future__ import annotations

import argparse
import sys

from .gp import evolve
from .targets import TARGETS, get_target

_SPARK = "▁▂▃▄▅▆▇█"


def _spark(values) -> str:
    import math
    vals = [math.log10(v + 1e-9) for v in values]    # log scale (error spans decades)
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    return "".join(_SPARK[min(7, int((v - lo) / span * 7))] for v in vals)


def _cmd_discover(args) -> int:
    target = get_target(args.target)
    res = evolve(target, population=args.pop, generations=args.gens, seed=args.seed)
    print(f"# symbolic regression on '{target.name}'  "
          f"({len(target.X)} sampled points)\n")
    print(f"  hidden formula     : {target.formula}")
    print(f"  discovered formula : {res.formula}")
    print(f"  error (MSE)        : {res.best_mse:.3g}   "
          f"{'✅ exact match' if res.solved else '(approximate)'}")
    print(f"  expression size    : {res.size} nodes, found in {res.generations} generations")
    print(f"  error over time    : {_spark(res.history)}  "
          f"{res.history[0]:.2g} → {res.best_mse:.2g}")
    return 0


def _cmd_list(_args) -> int:
    print("Targets to rediscover:\n")
    for name, t in TARGETS.items():
        print(f"  {name:<10} y = {t.formula}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="symbolic_regression",
        description="Evolve a mathematical formula that fits the data.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("discover")
    p.add_argument("--target", default="quadratic")
    p.add_argument("--pop", type=int, default=300)
    p.add_argument("--gens", type=int, default=40)
    p.add_argument("--seed", default="gp")
    p.set_defaults(func=_cmd_discover)

    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
