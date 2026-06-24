"""CLI for evolving a CartPole controller.

    python -m labs.neuroevolution.cli evolve
    python -m labs.neuroevolution.cli evolve --pop 30 --gens 25 --watch
    python -m labs.neuroevolution.cli random --watch
"""
from __future__ import annotations

import argparse
import sys

from .cartpole import CartPole
from .evolve import evolve
from .policy import Policy
from .render import rollout_frames

_SPARK = "▁▂▃▄▅▆▇█"


def _spark(values) -> str:
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    return "".join(_SPARK[min(7, int((v - lo) / span * 7))] for v in values)


def _show(policy, seed) -> None:
    shots, steps = rollout_frames(policy, seed=seed)
    for step, fr, deg in shots:
        print(f"\n  step {step:>3}  (pole {deg:+.1f}°)")
        print(fr)
    print(f"\n  balanced {steps} steps")


def _cmd_evolve(args) -> int:
    res = evolve(population=args.pop, generations=args.gens, seed=args.seed)
    print(f"# neuroevolution on CartPole  (pop {args.pop}, {args.gens} generations)\n")
    print(f"  best fitness: {res.best_fitness:.0f} / 500 steps")
    print(f"  per-generation best: {_spark(res.history)}  "
          f"{res.history[0]:.0f} → {res.best_fitness:.0f}")
    fresh = sum(CartPole().rollout(res.best_policy, seed=f"fresh{i}") for i in range(5)) / 5
    print(f"  generalization (5 unseen starts): {fresh:.0f} steps avg")
    if args.watch:
        print("\n  watching the evolved controller balance:")
        _show(res.best_policy, "watch")
    return 0


def _cmd_random(args) -> int:
    pol = Policy.random(6, seed=args.seed)
    print("# a RANDOM (un-evolved) controller — the pole falls fast\n")
    if args.watch:
        _show(pol, "watch")
    else:
        steps = CartPole().rollout(pol, seed="watch")
        print(f"  balanced {steps} steps")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="neuroevolution", description="Evolve a neural-net CartPole controller (no gradients).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("evolve")
    p.add_argument("--pop", type=int, default=24)
    p.add_argument("--gens", type=int, default=18)
    p.add_argument("--seed", default="evo")
    p.add_argument("--watch", action="store_true")
    p.set_defaults(func=_cmd_evolve)

    p = sub.add_parser("random")
    p.add_argument("--seed", default="r")
    p.add_argument("--watch", action="store_true")
    p.set_defaults(func=_cmd_random)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
