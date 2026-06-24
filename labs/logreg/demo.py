"""Demo: logistic regression — a linear boundary, fit by convex descent.

    python -m labs.logreg.demo
"""
from __future__ import annotations

from .logreg import LogisticRegression
from .data import linear, moons, split

_REGION = {0: "·", 1: "░"}
_POINT = {0: "o", 1: "#"}
_SPARK = "▁▂▃▄▅▆▇█"


def boundary(model, X, y, w=46, h=15):
    xs = [p[0] for p in X]
    ys = [p[1] for p in X]
    lox, hix = min(xs) - 0.3, max(xs) + 0.3
    loy, hiy = min(ys) - 0.3, max(ys) + 0.3
    grid = []
    for rr in range(h):
        yy = loy + (hiy - loy) * (h - 1 - rr) / (h - 1)
        row = model.predict([[lox + (hix - lox) * cc / (w - 1), yy] for cc in range(w)])
        grid.append([_REGION[p] for p in row])
    for (px, py), c in zip(X, y):
        cc = round((px - lox) / (hix - lox) * (w - 1))
        rr = round((hiy - py) / (hiy - loy) * (h - 1))
        if 0 <= cc < w and 0 <= rr < h:
            grid[rr][cc] = _POINT[c]
    return ["  |" + "".join(r) + "|" for r in grid]


def spark(xs):
    lo, hi = min(xs), max(xs)
    span = (hi - lo) or 1.0
    return "".join(_SPARK[min(7, int((x - lo) / span * 7))] for x in xs)


def _acc(yh, y):
    return sum(1 for a, b in zip(yh, y) if a == b) / len(y)


def main() -> int:
    X, y = linear(n=400, gap=1.4, seed="demo")
    Xtr, ytr, Xte, yte = split(X, y, seed="demo")
    m = LogisticRegression(lr=0.5, epochs=300).fit(Xtr, ytr)

    print("Logistic regression — P(y=1|x) = σ(w·x + b), fit by gradient descent.\n")
    print("It draws the best straight boundary between two classes (o / #):")
    for line in boundary(m, X, y):
        print(line)
    print(f"\n  test accuracy {_acc(m.predict(Xte), yte) * 100:.0f}%   "
          f"learned weights w=({m.w[0]:+.2f}, {m.w[1]:+.2f}), b={m.b:+.2f}\n")

    lh = m.loss_history
    pts = [lh[min(len(lh) - 1, round(i * (len(lh) - 1) / 43))] for i in range(44)]
    print("Cross-entropy loss is convex, so gradient descent slides to the global")
    print(f"optimum — no local minima:  {spark(pts)}  ({lh[0]:.2f} → {lh[-1]:.2f})\n")

    # calibration — do the probabilities mean what they say?
    probs = m.predict_proba(Xte)
    print("And the outputs are real probabilities — predicted vs. actual positive rate:")
    bins = {}
    for p, t in zip(probs, yte):
        bins.setdefault(round(p * 4) / 4, []).append(t)
    for b in sorted(bins):
        if len(bins[b]) >= 4:
            print(f"   said {b * 100:3.0f}% → actually {sum(bins[b]) / len(bins[b]) * 100:3.0f}% "
                  f"positive  (n={len(bins[b])})")

    # the linear limit
    Xm, ym = moons(n=400, seed="demo")
    xtr, ytr2, xte, yte2 = split(Xm, ym, seed="demo")
    lm = LogisticRegression(lr=0.5, epochs=300).fit(xtr, ytr2)
    print(f"\nIts limit: one straight line. On non-linear 'moons' it tops out at "
          f"{_acc(lm.predict(xte), yte2) * 100:.0f}%")
    print("— exactly where the lab's tree/forest (axis-aligned splits) pull ahead.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
