"""Demo: cluster 2-D blobs, and why k-means++ init matters.

    python -m labs.kmeans.demo
"""
from __future__ import annotations

from .data import blobs
from .kmeans import KMeans
from .metrics import purity, best_of, elbow

_MARKS = "○◆▲■✦✚"


def scatter(points, labels, centroids, w=46, h=16):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    lox, hix, loy, hiy = min(xs), max(xs), min(ys), max(ys)

    def cell(p):
        cx = round((p[0] - lox) / (hix - lox) * (w - 1)) if hix > lox else 0
        cy = round((p[1] - loy) / (hiy - loy) * (h - 1)) if hiy > loy else 0
        return cx, cy

    grid = [[" "] * w for _ in range(h)]
    for p, c in zip(points, labels):
        cx, cy = cell(p)
        grid[h - 1 - cy][cx] = _MARKS[c % len(_MARKS)]
    for c in centroids:                          # centroids as '@'
        cx, cy = cell(c)
        if 0 <= cx < w and 0 <= cy < h:
            grid[h - 1 - cy][cx] = "@"
    return ["  |" + "".join(r) + "|" for r in grid]


def main() -> int:
    X, true, centers = blobs(n=400, k=4, spread=0.5, seed="demo")
    km = best_of(X, k=4, restarts=5, seed="demo")

    print("k-means — group points by who they're closest to.\n")
    print(f"400 points, 4 hidden blobs. k-means++ found them ({_MARKS[:4]}, @=centroid):")
    for line in scatter(X, km.labels, km.centroids):
        print(line)
    print(f"\n  purity vs the true blobs: {purity(km.labels, true, 4) * 100:.0f}%   "
          f"(converged in {km.n_iter} iterations, inertia {km.inertia:.0f})")
    print("  every Lloyd step only ever lowers the within-cluster distance.\n")

    # init matters
    pp = [KMeans(k=4, init="kmeans++", seed=("p", s)).fit(X).inertia for s in range(20)]
    rr = [KMeans(k=4, init="random", seed=("r", s)).fit(X).inertia for s in range(20)]
    print("Initialization decides everything:")
    print(f"   k-means++ : mean inertia {sum(pp) / len(pp):6.0f},  worst {max(pp):6.0f}")
    print(f"   random    : mean inertia {sum(rr) / len(rr):6.0f},  worst {max(rr):6.0f}")
    print("   k-means++ seeds centroids far apart, so it rarely lands in a bad optimum.\n")

    # elbow
    print("How many clusters? The 'elbow' in inertia-vs-k reveals it:")
    el = elbow(X, ks=range(1, 8), seed="demo")
    hi = el[0][1]
    for k, inertia in el:
        bar = "█" * round(40 * inertia / hi)
        mark = "  ← elbow (true k=4)" if k == 4 else ""
        print(f"   k={k}  {bar:<40} {inertia:6.0f}{mark}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
