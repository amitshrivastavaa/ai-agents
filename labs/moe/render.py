"""ASCII plot of the data, the mixture's fit, and which expert owns where."""
from __future__ import annotations

from .data import Dataset
from .moe import MixtureOfExperts

_DIGITS = "0123456789"


def plot_fit(data: Dataset, moe: MixtureOfExperts, *, width: int = 56, height: int = 18) -> str:
    xs, ys = data.X, data.y
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    pad = 0.05 * (ymax - ymin or 1)
    ymin, ymax = ymin - pad, ymax + pad

    def col(x):
        return max(0, min(width - 1, round((x - xmin) / (xmax - xmin or 1) * (width - 1))))

    def row(y):
        return max(0, min(height - 1, round((ymax - y) / (ymax - ymin or 1) * (height - 1))))

    grid = [[" "] * width for _ in range(height)]
    # data points
    for x, y in zip(xs, ys):
        grid[row(y)][col(x)] = "·"
    # mixture prediction, labelled by the routed expert id
    for c in range(width):
        x = xmin + (xmax - xmin) * c / (width - 1)
        e = moe.route(x)
        r = row(moe.predict(x))
        grid[r][c] = _DIGITS[e % 10]
    return "\n".join("".join(r) for r in grid)
