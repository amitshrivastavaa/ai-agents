"""Demo: Gaussian Process regression with calibrated uncertainty.

    python -m labs.gp.demo
"""
from __future__ import annotations

import math

from .gp import GP, rbf


def plot(gp, f, Xtrain, ytrain, xlo, xhi, w=64, h=17):
    xs = [xlo + (xhi - xlo) * i / (w - 1) for i in range(w)]
    preds = [gp.predict(x) for x in xs]
    means = [m for m, _ in preds]
    stds = [math.sqrt(v) for _, v in preds]
    los = [m - 2 * s for m, s in zip(means, stds)]
    his = [m + 2 * s for m, s in zip(means, stds)]
    trues = [f(x) for x in xs]
    ylo = min(min(los), min(trues)) - 0.2
    yhi = max(max(his), max(trues)) + 0.2

    def row(y):
        return round((y - ylo) / (yhi - ylo) * (h - 1))

    grid = [[" "] * w for _ in range(h)]
    for c in range(w):
        for r in range(row(los[c]), row(his[c]) + 1):          # 95% band
            if 0 <= r < h:
                grid[h - 1 - r][c] = "░"
    for c in range(w):                                          # true function
        r = row(trues[c])
        if 0 <= r < h:
            grid[h - 1 - r][c] = "·"
    for c in range(w):                                          # posterior mean
        r = row(means[c])
        if 0 <= r < h:
            grid[h - 1 - r][c] = "━"
    for x, y in zip(Xtrain, ytrain):                            # observations
        c = round((x - xlo) / (xhi - xlo) * (w - 1))
        r = row(y)
        if 0 <= c < w and 0 <= r < h:
            grid[h - 1 - r][c] = "o"
    return ["  |" + "".join(r) + "|" for r in grid]


def main() -> int:
    f = math.sin
    Xtrain = [0.0, 0.6, 1.2, 1.8, 2.4, 7.0, 7.6, 8.2]          # note the gap 2.4–7
    ytrain = [f(x) for x in Xtrain]
    gp = GP(rbf(length=1.0, var=1.0), noise=1e-3, prior_var=1.0).fit(Xtrain, ytrain)

    print("Gaussian Process regression — curve fitting that knows what it doesn't know.\n")
    print("Fit to noisy samples of sin(x), WITH a gap in the data from x≈2.4 to 7.")
    print("  o = observation   ━ = posterior mean   · = true sin   ░ = 95% band\n")
    for line in plot(gp, f, Xtrain, ytrain, -1.0, 9.5):
        print(line)

    print("\nRead the band: it pinches to nothing AT the data and balloons in the")
    print("gap and beyond the last point — the model's honest uncertainty.\n")
    print("  x      mean     ±2σ band      note")
    for x, note in [(0.6, "on a data point"), (4.7, "middle of the gap"),
                    (7.6, "on a data point"), (9.3, "past all data")]:
        m, v = gp.predict(x)
        s = math.sqrt(v)
        print(f"  {x:4.1f}   {m:+.2f}    ±{2 * s:.2f}        {note}")
    print("\n  At the data the std is the noise floor; in the gap and beyond it")
    print("  returns to the prior — uncertainty you can actually trust.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
