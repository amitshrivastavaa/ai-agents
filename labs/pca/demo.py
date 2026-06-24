"""Demo: find the axes of variation, then compress to them.

    python -m labs.pca.demo
"""
from __future__ import annotations

from .pca import PCA
from .data import correlated_2d, low_rank
from .linalg import dot


def scatter(points, axis_dir, mean, w=46, h=15):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    lox, hix, loy, hiy = min(xs), max(xs), min(ys), max(ys)

    def col(x):
        return round((x - lox) / (hix - lox) * (w - 1)) if hix > lox else 0

    def rowy(y):
        return round((y - loy) / (hiy - loy) * (h - 1)) if hiy > loy else 0

    grid = [[" "] * w for _ in range(h)]
    for x, y in points:
        grid[h - 1 - rowy(y)][col(x)] = "·"
    for t in range(-60, 61):                      # draw the PC1 axis through mean
        x = mean[0] + 0.1 * t * axis_dir[0]
        y = mean[1] + 0.1 * t * axis_dir[1]
        c, rr = col(x), rowy(y)
        if 0 <= c < w and 0 <= rr < h:
            grid[h - 1 - rr][c] = "█"
    return ["  |" + "".join(r) + "|" for r in grid]


def main() -> int:
    pts, axis = correlated_2d(n=400, angle=0.5, seed="demo")
    p = PCA(2).fit(pts)
    print("PCA — find the directions your data actually varies along.\n")
    print("A 2-D cloud (·) with PC1 (█) drawn through the mean:")
    for line in scatter(pts, p.components[0], p.mean):
        print(line)
    evr = p.explained_variance_ratio
    print(f"\n  PC1 explains {evr[0] * 100:.0f}% of the variance, PC2 just {evr[1] * 100:.0f}%.")
    print(f"  PC1 aligns with the true stretch axis to {abs(dot(p.components[0], axis)):.3f} "
          f"(1.0 = exact).\n")

    # compression of genuinely low-rank data
    X = low_rank(n=200, dim=40, rank=3, noise=0.03, seed="demo")
    print("Compression — 40-D vectors that secretly live in a 3-D subspace.")
    print("Project to k components, reconstruct, measure the error:\n")
    print(f"   {'k':>3} {'cumulative variance':>22} {'reconstruction MSE':>20}")
    for k in (1, 2, 3, 5, 10):
        pk = PCA(k).fit(X)
        cum = sum(pk.explained_variance_ratio)
        R = pk.reconstruct(X)
        mse = sum(sum((a - b) ** 2 for a, b in zip(x, r))
                  for x, r in zip(X, R)) / len(X)
        bar = "█" * round(22 * cum)
        print(f"   {k:>3} {bar:>22} {mse:>20.4f}")
    print("\n  The elbow is at k=3 — PCA discovers the true dimensionality. Three")
    print("  numbers per vector reconstruct the 40 almost perfectly; the rest is noise.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
