"""CLI for the PageRank lab.

    python -m labs.pagerank.cli rank --graph web
    python -m labs.pagerank.cli verify --graph communities
    python -m labs.pagerank.cli damping --graph web
"""
from __future__ import annotations

import argparse
import sys

from . import graph as G
from .rank import pagerank, ranked
from .surfer import surf
from .demo import bars


def _cmd_rank(args) -> int:
    g = G.GRAPHS[args.graph]
    order = ranked(g, damping=args.damping)
    _, iters = pagerank(g, damping=args.damping)
    print(f"# PageRank of {args.graph!r}  (damping={args.damping}, {iters} iters)\n")
    print(bars(order))
    return 0


def _cmd_verify(args) -> int:
    g = G.GRAPHS[args.graph]
    r, _ = pagerank(g)
    s = surf(g, steps=args.steps, seed=args.graph)
    print(f"# PageRank vs random surfer — {args.graph!r}  ({args.steps} steps)\n")
    print(f"   {'node':>6} {'PageRank':>10} {'surfer':>10}")
    for name, v in ranked(g):
        print(f"   {name:>6} {v:>10.4f} {s[name]:>10.4f}")
    print(f"\n   max difference {max(abs(r[n] - s[n]) for n in r):.4f}")
    return 0


def _cmd_damping(args) -> int:
    g = G.GRAPHS[args.graph]
    print(f"# how damping reshapes the ranking of {args.graph!r}\n")
    print(f"   {'node':>6}" + "".join(f"  d={d:>4}" for d in (0.0, 0.5, 0.85, 0.99)))
    base = [n for n, _ in ranked(g)]
    cols = {d: dict(ranked(g, damping=d)) for d in (0.0, 0.5, 0.85, 0.99)}
    for n in base:
        print(f"   {n:>6}" + "".join(f"  {cols[d][n]:>6.3f}" for d in (0.0, 0.5, 0.85, 0.99)))
    print("\n   d=0 → uniform (pure teleport); higher d → link structure dominates.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="pagerank", description="PageRank by power iteration, checked by a random surfer.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("rank", help="rank a graph's nodes")
    p.add_argument("--graph", default="web", choices=list(G.GRAPHS))
    p.add_argument("--damping", type=float, default=0.85)
    p.set_defaults(func=_cmd_rank)

    p = sub.add_parser("verify", help="cross-check against a random surfer")
    p.add_argument("--graph", default="web", choices=list(G.GRAPHS))
    p.add_argument("--steps", type=int, default=300_000)
    p.set_defaults(func=_cmd_verify)

    p = sub.add_parser("damping", help="effect of the damping factor")
    p.add_argument("--graph", default="web", choices=list(G.GRAPHS))
    p.set_defaults(func=_cmd_damping)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
