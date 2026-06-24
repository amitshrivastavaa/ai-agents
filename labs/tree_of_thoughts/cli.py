"""CLI for the Tree-of-Thoughts Game-of-24 solver.

    python -m labs.tree_of_thoughts.cli solve 3 3 8 8
    python -m labs.tree_of_thoughts.cli solve 4 6 8 2 --method random
    python -m labs.tree_of_thoughts.cli compare
    python -m labs.tree_of_thoughts.cli list
"""
from __future__ import annotations

import argparse
import sys

from .game24 import exact_solve, expression
from .search import PUZZLES, brute_force, compare, random_search, tot_search

_METHODS = {"tot": tot_search, "random": random_search,
            "brute": lambda nums, **kw: brute_force(nums)}


def _cmd_solve(args) -> int:
    nums = tuple(args.numbers)
    if len(nums) != 4:
        print("give exactly four numbers, e.g. 3 3 8 8")
        return 1
    fn = _METHODS[args.method]
    kw = {"beam_width": args.beam, "samples": args.samples} if args.method == "tot" else {}
    if args.method == "random":
        kw = {"tries": args.tries}
    res = fn(nums, **kw)
    print(f"{nums} via {res.method}:")
    if res.solved:
        print(f"  ✅ 24 = {expression(res.path)}")
    else:
        truth = exact_solve(nums)
        if truth is None:
            print("  ∅ no solution exists (the verifier agrees)")
        else:
            print(f"  ✗ this method missed it — a solution does exist: {expression(truth)}")
    print(f"  (states examined: {res.nodes})")
    return 0


def _cmd_compare(args) -> int:
    c = compare(beam_width=args.beam, samples=args.samples, tries=args.tries)
    print(f"{c['n']} puzzles · {c['solvable']} solvable\n")
    print(f"  {'method':<18}{'solved':>10}{'avg states':>14}")
    for m in ("random", "tree_of_thoughts", "brute_force"):
        print(f"  {m:<18}{c[m]['solved']:>4}/{c['solvable']:<5}{c[m]['avg_nodes']:>14}")
    print("\nTree-of-Thoughts matches brute force's correctness while examining")
    print("far fewer states — and beats random, which wanders more yet solves less.")
    print("Deliberation (scoring and pruning thoughts) is what buys the efficiency.")
    return 0


def _cmd_list(_args) -> int:
    print("Built-in puzzles:")
    for p in PUZZLES:
        print(f"  {p}  ({'solvable' if exact_solve(p) else 'unsolvable'})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tree_of_thoughts",
        description="Solve the Game of 24 by deliberate search over thoughts.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("solve")
    p.add_argument("numbers", nargs="+", type=int)
    p.add_argument("--method", choices=list(_METHODS), default="tot")
    p.add_argument("--beam", type=int, default=12)
    p.add_argument("--samples", type=int, default=16)
    p.add_argument("--tries", type=int, default=200)
    p.set_defaults(func=_cmd_solve)

    p = sub.add_parser("compare")
    p.add_argument("--beam", type=int, default=12)
    p.add_argument("--samples", type=int, default=16)
    p.add_argument("--tries", type=int, default=200)
    p.set_defaults(func=_cmd_compare)

    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
