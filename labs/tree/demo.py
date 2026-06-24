"""Demo: a decision tree carves space into rectangles.

    python -m labs.tree.demo
"""
from __future__ import annotations

from .tree import DecisionTree
from .data import moons, xor, blobs, train_test_split
from .metrics import accuracy, depth_sweep

_REGION = {0: "·", 1: "░", 2: "▒"}
_POINT = {0: "o", 1: "#", 2: "@"}


def boundary(tree, X, y, w=50, h=20):
    xs = [p[0] for p in X]
    ys = [p[1] for p in X]
    lox, hix = min(xs) - 0.3, max(xs) + 0.3
    loy, hiy = min(ys) - 0.3, max(ys) + 0.3
    grid = [[" "] * w for _ in range(h)]
    for rr in range(h):
        for cc in range(w):
            x = lox + (hix - lox) * cc / (w - 1)
            yy = loy + (hiy - loy) * (h - 1 - rr) / (h - 1)
            grid[rr][cc] = _REGION.get(tree._predict_one([x, yy]), "·")
    for (px, py), c in zip(X, y):
        cc = round((px - lox) / (hix - lox) * (w - 1))
        rr = round((hiy - py) / (hiy - loy) * (h - 1))
        if 0 <= cc < w and 0 <= rr < h:
            grid[rr][cc] = _POINT.get(c, "?")
    return ["  |" + "".join(r) + "|" for r in grid]


def main() -> int:
    print("Decision tree — yes/no questions that carve space into rectangles.\n")

    X, y = moons(n=400, seed="demo")
    Xtr, ytr, Xte, yte = train_test_split(X, y, seed="demo")
    t = DecisionTree(max_depth=7).fit(Xtr, ytr)
    print("Two interleaving 'moons' (o/#) — a curved boundary built from straight cuts:")
    for line in boundary(t, X, y):
        print(line)
    print(f"\n  train accuracy {accuracy(t.predict(Xtr), ytr) * 100:.0f}%, "
          f"test {accuracy(t.predict(Xte), yte) * 100:.0f}%   "
          f"(depth {t.depth()}, {t.n_leaves()} leaves)\n")

    print("Depth controls the bias/variance trade-off — train fits ever better,")
    print("test peaks then overfits:")
    print(f"   {'depth':>5} {'train':>8} {'test':>8}")
    for d, tr, te in depth_sweep(Xtr, ytr, Xte, yte, depths=range(1, 11)):
        gap = "  ← overfitting" if tr - te > 0.12 else ""
        print(f"   {d:>5} {tr * 100:>7.0f}% {te * 100:>7.0f}%{gap}")

    Xb, yb = blobs(n=300, seed="demo")
    bt = DecisionTree(max_depth=6).fit(Xb, yb)
    print(f"\n  Multiclass too: 3-blob data → {accuracy(bt.predict(Xb), yb) * 100:.0f}% "
          f"in {bt.n_leaves()} leaves. And XOR — which a linear model can't separate")
    Xx, yx = xor(n=400, seed="demo")
    xt = DecisionTree(max_depth=6).fit(Xx, yx)
    print(f"  at all (~50%) — the tree nails at {accuracy(xt.predict(Xx), yx) * 100:.0f}% "
          f"(greedy splitting just needs a few levels to find the checkerboard).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
