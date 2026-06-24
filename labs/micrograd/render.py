"""ASCII visualizations: loss curves, decision boundaries, and regression fits."""
from __future__ import annotations

import math

from .train import Dataset, _predict
from .nn import MLP

_SPARK = "▁▂▃▄▅▆▇█"


def sparkline(values: list[float]) -> str:
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    return "".join(_SPARK[min(7, int((v - lo) / span * 7))] for v in values)


def decision_boundary(model: MLP, data: Dataset, *, width: int = 42, height: int = 18) -> str:
    xs = [p[0] for p in data.X]
    ys = [p[1] for p in data.X]
    pad = 0.4
    minx, maxx = min(xs) - pad, max(xs) + pad
    miny, maxy = min(ys) - pad, max(ys) + pad

    grid = [[" "] * width for _ in range(height)]
    for gy in range(height):
        for gx in range(width):
            x = minx + (maxx - minx) * gx / (width - 1)
            y = maxy - (maxy - miny) * gy / (height - 1)
            pred = _predict(model, [x, y]).data
            grid[gy][gx] = "░" if pred >= 0 else " "

    def cell(px, py):
        gx = round((px - minx) / (maxx - minx) * (width - 1))
        gy = round((maxy - py) / (maxy - miny) * (height - 1))
        return max(0, min(height - 1, gy)), max(0, min(width - 1, gx))

    for (px, py), label in zip(data.X, data.y):
        gy, gx = cell(px, py)
        grid[gy][gx] = "+" if label >= 0 else "o"
    return "\n".join("".join(row) for row in grid)


def regression_plot(model: MLP, data: Dataset, *, width: int = 48, height: int = 12) -> str:
    xs = [p[0] for p in data.X]
    minx, maxx = min(xs), max(xs)
    samples = [(minx + (maxx - minx) * i / (width - 1)) for i in range(width)]
    preds = [_predict(model, [x]).data for x in samples]
    trues = [math.sin(x) for x in samples]
    lo = min(min(preds), min(trues), -1.0)
    hi = max(max(preds), max(trues), 1.0)

    grid = [[" "] * width for _ in range(height)]

    def row(v):
        return max(0, min(height - 1, round((hi - v) / ((hi - lo) or 1) * (height - 1))))

    for gx in range(width):
        grid[row(trues[gx])][gx] = "·"
    for gx in range(width):
        r = row(preds[gx])
        grid[r][gx] = "#" if grid[r][gx] == " " else "*"
    return "\n".join("".join(r) for r in grid) + "\n  (· true sin   # prediction   * overlap)"
