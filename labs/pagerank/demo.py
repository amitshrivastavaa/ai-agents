"""Demo: rank a tiny web with PageRank, and prove it with a random surfer.

    python -m labs.pagerank.demo
"""
from __future__ import annotations

from . import graph as G
from .rank import pagerank, ranked
from .surfer import surf


def bars(items, width=34):
    hi = max(v for _, v in items) or 1.0
    out = []
    for name, v in items:
        out.append(f"   {name:>4}  {'█' * round(width * v / hi):<{width}} {v:.3f}")
    return "\n".join(out)


def main() -> int:
    g = G.web()
    r, iters = pagerank(g)
    order = ranked(g)

    print("PageRank — the eigenvector that ranked the web.\n")
    print("A tiny web (page → the pages it links to):")
    for u in g:
        print(f"   {u} → {', '.join(g[u]) or '(nothing)'}")
    print()
    print(f"PageRank (power iteration, converged in {iters} steps):")
    print(bars(order))
    print(f"\n   → C wins: it's linked by A, B *and* D. D loses: nobody links to it.")
    print(f"   ranks sum to {sum(r.values()):.3f} — they're a probability distribution.\n")

    # the random-surfer cross-check
    s = surf(g, steps=300_000, seed="demo")
    print("Why those numbers? A random surfer who follows links 85% of the time")
    print("and teleports 15% spends exactly this fraction of its life on each page:")
    print(f"   {'page':>4} {'PageRank':>10} {'surfer':>10}")
    for name, v in order:
        print(f"   {name:>4} {v:>10.3f} {s[name]:>10.3f}")
    print(f"\n   max difference {max(abs(r[n] - s[n]) for n in r):.4f} — PageRank IS the")
    print("   stationary distribution of that walk. Computed two completely")
    print("   different ways, the same answer.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
