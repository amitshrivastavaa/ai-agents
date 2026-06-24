"""CLI for the score-based diffusion sampler.

    python -m labs.diffusion.cli sample --target ring
    python -m labs.diffusion.cli sample --target spiral --n 400
    python -m labs.diffusion.cli list
"""
from __future__ import annotations

import argparse
import sys

from .diffusion import generate, nearest_mode_distance
from .target import TARGETS, get_target
from .render import scatter


def _cmd_sample(args) -> int:
    target = get_target(args.target)
    samples = generate(target, n=args.n, seed=args.seed)
    d = nearest_mode_distance(samples, target)
    print(f"# diffusion · target '{target.name}'  ({args.n} samples from noise)\n")
    print(scatter(samples, target))
    print(f"\n  mean distance to nearest mode: {d:.2f}  (per-mode spread σ₀ = {target.sigma0})")
    print("  o = target mode · shaded = generated sample density")
    return 0


def _cmd_list(_args) -> int:
    for name, t in TARGETS.items():
        print(f"  {name:<7} {len(t.modes)} modes")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="diffusion", description="Generate samples from noise with annealed Langevin dynamics.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("sample")
    p.add_argument("--target", default="ring")
    p.add_argument("--n", type=int, default=300)
    p.add_argument("--seed", default="diff")
    p.set_defaults(func=_cmd_sample)

    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
