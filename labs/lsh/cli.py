"""CLI for the LSH lab.

    python -m labs.lsh.cli search --bits 8 --tables 12
    python -m labs.lsh.cli sweep
    python -m labs.lsh.cli law
"""
from __future__ import annotations

import argparse
import math
import sys

from .data import make_dataset, make_queries, cosine
from .hashing import SimHash, angle, collision_prob
from .eval import build, recall_at_k

_D = dict(n=600, dim=24, clusters=12, spread=0.12, seed="cli")


def _data_and_queries():
    data, _ = make_dataset(**_D)
    queries = make_queries(n=150, dim=_D["dim"], clusters=_D["clusters"],
                           spread=_D["spread"], seed="q", base_seed=_D["seed"])
    return data, queries


def _cmd_search(args) -> int:
    data, queries = _data_and_queries()
    idx = build(data, n_bits=args.bits, n_tables=args.tables, seed=_D["seed"])
    rec, frac = recall_at_k(idx, queries, k=args.k)
    print(f"# LSH search  ({args.bits} bits × {args.tables} tables, k={args.k})\n")
    q = queries[0]
    got, ncand = idx.query(q, args.k)
    true = idx.brute_force(q, args.k)
    print("  exact NN cosines: " + " ".join(f"{cosine(q, data[i]):.2f}" for i in true))
    print("  LSH   NN cosines: " + " ".join(f"{cosine(q, data[i]):.2f}" for i in got))
    print(f"\n  recall@{args.k} = {rec * 100:.0f}%   scanned {frac * 100:.0f}% of "
          f"the dataset   ({1 / frac:.1f}× faster than exact)")
    return 0


def _cmd_sweep(args) -> int:
    data, queries = _data_and_queries()
    print(f"# recall / speedup sweep  ({len(data)} vectors, {len(data[0])}-D)\n")
    print(f"  {'bits':>4} {'tables':>7} {'recall@10':>10} {'scanned':>9} {'speedup':>9}")
    for n_bits in (8, 10, 12):
        for n_tables in (4, 8, 12):
            idx = build(data, n_bits=n_bits, n_tables=n_tables, seed=_D["seed"])
            rec, frac = recall_at_k(idx, queries, k=10)
            print(f"  {n_bits:>4} {n_tables:>7} {rec * 100:>9.0f}% {frac * 100:>8.0f}% "
                  f"{1 / frac:>8.1f}×")
    return 0


def _cmd_law(args) -> int:
    sh = SimHash(24, args.bits, seed="law")
    print(f"# SimHash collision law: P(bit agrees) = 1 − θ/π  ({args.bits} planes)\n")
    print(f"  {'cos':>5} {'angle°':>7} {'empirical':>10} {'1−θ/π':>8}")
    for c in (0.95, 0.8, 0.5, 0.2, -0.2):
        a = [1.0] + [0.0] * 23
        b = [c] + [math.sqrt(1 - c * c)] + [0.0] * 22
        agree = sum(1 for x, y in zip(sh.signature(a), sh.signature(b))
                    if x == y) / args.bits
        th = angle(a, b)
        print(f"  {c:>5.2f} {math.degrees(th):>7.0f} {agree:>10.3f} "
              f"{collision_prob(th):>8.3f}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="lsh", description="Locality-sensitive hashing for nearest-neighbour search.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("search", help="run a query, report recall + speedup")
    p.add_argument("--bits", type=int, default=8)
    p.add_argument("--tables", type=int, default=12)
    p.add_argument("--k", type=int, default=10)
    p.set_defaults(func=_cmd_search)

    p = sub.add_parser("sweep", help="recall/speedup over bits × tables")
    p.set_defaults(func=_cmd_sweep)

    p = sub.add_parser("law", help="verify the collision-probability law")
    p.add_argument("--bits", type=int, default=4000)
    p.set_defaults(func=_cmd_law)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
