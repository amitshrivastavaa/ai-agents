"""Demo: prediction intervals with a guaranteed coverage rate.

    python -m labs.conformal.demo
"""
from __future__ import annotations

from .data import heteroscedastic, split
from .conformal import calibrate, coverage, mean_width
from .model import knn_predict


def band_plot(predict, Xtr, ytr, Xte, yte, lo=-3.0, hi=3.0, w=58, h=15):
    xs = [lo + (hi - lo) * i / (w - 1) for i in range(w)]
    bands = [predict(x) for x in xs]
    yhat = [knn_predict(x, Xtr, ytr) for x in xs]
    allv = [v for b in bands for v in b] + yte
    ylo, yhi = min(allv) - 0.2, max(allv) + 0.2

    def row(v):
        return round((v - ylo) / (yhi - ylo) * (h - 1))

    grid = [[" "] * w for _ in range(h)]
    for c, (blo, bhi) in enumerate(bands):
        for r in range(row(blo), row(bhi) + 1):
            if 0 <= r < h:
                grid[h - 1 - r][c] = "░"
    for c in range(w):
        r = row(yhat[c])
        if 0 <= r < h:
            grid[h - 1 - r][c] = "━"
    for x, y in zip(Xte, yte):                       # test points: o inside, x outside
        c = round((x - lo) / (hi - lo) * (w - 1))
        r = row(y)
        if 0 <= c < w and 0 <= r < h:
            inside = predict(x)[0] <= y <= predict(x)[1]
            grid[h - 1 - r][c] = "·" if inside else "×"
    return ["  |" + "".join(r) + "|" for r in grid]


def main() -> int:
    X, y = heteroscedastic(n=700, seed="demo")
    (Xtr, ytr), (Xcal, ycal), (Xte, yte) = split(X, y, seed="ten")

    print("Conformal prediction — error bars you can actually trust.\n")
    print("Wrap ANY model: score it on a held-out calibration set, take the 90th")
    print("percentile error, and ŷ ± that covers the truth ≥90% of the time —")
    print("for any data distribution, with a proof. Here, k-NN on noisy sin(x).\n")

    pred = calibrate(Xtr, ytr, Xcal, ycal, alpha=0.1, k=9)
    print("90% interval (░ band, ━ prediction, · covered, × missed):")
    for line in band_plot(pred, Xtr, ytr, Xte, yte):
        print(line)
    print(f"   empirical coverage on test: {coverage(pred, Xte, yte) * 100:.0f}%  "
          f"(target 90%)\n")

    # the guarantee holds across many splits, regardless of the data
    print("The guarantee, not a fluke — coverage over 40 fresh random splits:")
    for alpha in (0.05, 0.1, 0.2):
        covs = []
        for s in range(40):
            tr, cal, te = split(X, y, seed=("s", s))
            p = calibrate(tr[0], tr[1], cal[0], cal[1], alpha=alpha, k=9)
            covs.append(coverage(p, te[0], te[1]))
        print(f"   α={alpha:<4} target {1 - alpha:.2f}   measured {sum(covs) / len(covs):.3f}")

    # adaptive intervals
    adp = calibrate(Xtr, ytr, Xcal, ycal, alpha=0.1, k=9, normalized=True)
    print("\nAdaptive conformal scales intervals by local difficulty — same coverage,")
    print("tighter where the data is clean:")
    print(f"   standard : width {mean_width(pred, Xte):.2f} everywhere, "
          f"coverage {coverage(pred, Xte, yte) * 100:.0f}%")
    print(f"   adaptive : width {mean_width(adp, Xte):.2f} avg, "
          f"coverage {coverage(adp, Xte, yte) * 100:.0f}% — narrow on the calm side, wide on the noisy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
