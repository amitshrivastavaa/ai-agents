"""Demo: a forest of trees votes — smoother, steadier than any one tree.

    python -m labs.forest.demo
"""
from __future__ import annotations

import statistics

from .forest import RandomForest
from ..tree.tree import DecisionTree
from ..tree.data import moons, blobs, xor, train_test_split
from ..tree.metrics import accuracy

_REGION = {0: "·", 1: "░"}
_POINT = {0: "o", 1: "#"}


def boundary(predict, X, y, w=46, h=15):
    xs = [p[0] for p in X]
    ys = [p[1] for p in X]
    lox, hix = min(xs) - 0.3, max(xs) + 0.3
    loy, hiy = min(ys) - 0.3, max(ys) + 0.3
    cells = [[lox + (hix - lox) * cc / (w - 1) for cc in range(w)] for _ in range(1)][0]
    grid = []
    for rr in range(h):
        yy = loy + (hiy - loy) * (h - 1 - rr) / (h - 1)
        preds = predict([[x, yy] for x in cells])
        grid.append([_REGION.get(p, "·") for p in preds])
    for (px, py), c in zip(X, y):
        cc = round((px - lox) / (hix - lox) * (w - 1))
        rr = round((hiy - py) / (hiy - loy) * (h - 1))
        if 0 <= cc < w and 0 <= rr < h:
            grid[rr][cc] = _POINT.get(c, "?")
    return ["  |" + "".join(r) + "|" for r in grid]


def main() -> int:
    X, y = moons(n=400, seed="demo")
    Xtr, ytr, Xte, yte = train_test_split(X, y, seed="demo")
    tree = DecisionTree(max_depth=8).fit(Xtr, ytr)
    forest = RandomForest(n_trees=25, max_depth=8, seed="demo").fit(Xtr, ytr)

    print("Random forest — many trees vote, and the noise cancels out.\n")
    print("Each tree trains on a bootstrap resample with random features, so they")
    print("overfit differently; averaging their votes is smoother and steadier.\n")

    print("25-tree forest decision boundary (· vs ░, points o/#):")
    for line in boundary(lambda P: forest.predict(P), X, y):
        print(line)
    print("\nBoth a single tree and the forest separate these moons — the forest's")
    print("edge shows up in the numbers that matter:")

    print(f"\n  single tree test accuracy : {accuracy(tree.predict(Xte), yte) * 100:.1f}%")
    print(f"  forest      test accuracy : {accuracy(forest.predict(Xte), yte) * 100:.1f}%")
    print(f"  forest out-of-bag accuracy: {forest.oob_score(Xtr, ytr) * 100:.1f}%  "
          f"(validation for free — no held-out set needed)\n")

    print("More trees → less variance. Mean ± std of test accuracy over 10 splits:")
    for nt in (1, 5, 15, 40):
        accs = []
        for s in range(10):
            Xs, ys = moons(n=400, seed=("v", s))
            xtr, ytr2, xte, yte2 = train_test_split(Xs, ys, seed=("v", s))
            f = RandomForest(n_trees=nt, max_depth=8, seed=("v", s)).fit(xtr, ytr2)
            accs.append(accuracy(f.predict(xte), yte2))
        print(f"   {nt:>2} trees   {sum(accs) / len(accs) * 100:5.1f}%  ± {statistics.pstdev(accs) * 100:.1f}")

    Xx, yx = xor(n=400, seed="demo")
    xtr, ytr3, xte, yte3 = train_test_split(Xx, yx, seed="demo")
    fx = RandomForest(n_trees=25, max_depth=8, seed="x").fit(xtr, ytr3)
    print(f"\n  And XOR — the single tree's nemesis — the forest still nails: "
          f"{accuracy(fx.predict(xte), yte3) * 100:.0f}%.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
