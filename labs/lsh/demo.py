"""Demo: approximate nearest-neighbour search with locality-sensitive hashing.

    python -m labs.lsh.demo
"""
from __future__ import annotations

import math

from .data import make_dataset, make_queries, cosine
from .hashing import SimHash, angle, collision_prob
from .eval import build, recall_at_k


def main() -> int:
    data, _ = make_dataset(n=600, dim=24, clusters=12, spread=0.12, seed="demo")
    queries = make_queries(n=150, dim=24, clusters=12, spread=0.12, seed="q",
                           base_seed="demo")

    print("Locality-Sensitive Hashing — the trick that makes vector search scale.")
    print("(the engine under every vector DB / RAG retriever at size)\n")
    print(f"{len(data)} vectors in {len(data[0])}-D. Exact search scores all "
          f"{len(data)}; LSH scores a few.\n")

    # ── one query: LSH top-5 vs the exact answer ──
    idx = build(data, n_bits=8, n_tables=12, seed="demo")
    q = queries[0]
    got, ncand = idx.query(q, 5)
    true = idx.brute_force(q, 5)
    print("A query's 5 nearest neighbours (cosine similarity):")
    print("   exact (scan all):  " + " ".join(f"{cosine(q, data[i]):.2f}" for i in true))
    print("   LSH  (scan a few): " + " ".join(f"{cosine(q, data[i]):.2f}" for i in got))
    print(f"   LSH examined {ncand} of {len(data)} vectors "
          f"({ncand / len(data) * 100:.0f}%) and matched the exact top-5.\n")

    # ── the recall / speedup dial ──
    print("The LSH dial — more tables lift recall, more bits cut the candidate set:")
    print(f"   {'bits':>4} {'tables':>7} {'recall@10':>10} {'scanned':>9} {'speedup':>9}")
    for n_bits, n_tables in [(8, 4), (8, 12), (10, 8), (12, 8), (12, 12)]:
        idx = build(data, n_bits=n_bits, n_tables=n_tables, seed="demo")
        rec, frac = recall_at_k(idx, queries, k=10)
        print(f"   {n_bits:>4} {n_tables:>7} {rec * 100:>9.0f}% {frac * 100:>8.0f}% "
              f"{1 / frac:>8.1f}×")

    # ── why it works: the SimHash collision law ──
    print("\nWhy it works — two vectors at angle θ share a random-hyperplane bit")
    print("with probability exactly 1 − θ/π (so near vectors collide, far ones don't):")
    sh = SimHash(24, 4000, seed="law")
    print(f"   {'cos':>5} {'angle°':>7} {'empirical':>10} {'1−θ/π':>8}")
    for c in (0.9, 0.6, 0.3, 0.0):
        a = [1.0] + [0.0] * 23
        b = [c] + [math.sqrt(1 - c * c)] + [0.0] * 22
        agree = sum(1 for x, y in zip(sh.signature(a), sh.signature(b)) if x == y) / 4000
        th = angle(a, b)
        print(f"   {c:>5.1f} {math.degrees(th):>7.0f} {agree:>10.3f} "
              f"{collision_prob(th):>8.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
