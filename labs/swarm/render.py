"""ASCII rendering of a tour over the city map."""
from __future__ import annotations

from .tsp import TSP

_LABELS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _bresenham(a, b):
    (x0, y0), (x1, y1) = a, b
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        yield x0, y0
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def plot_tour(tsp: TSP, tour: list[int], *, width: int = 48, height: int = 20) -> str:
    xs = [c[0] for c in tsp.cities]
    ys = [c[1] for c in tsp.cities]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)

    def cell(idx):
        x, y = tsp.cities[idx]
        gx = int((x - minx) / (maxx - minx or 1) * (width - 1))
        gy = int((y - miny) / (maxy - miny or 1) * (height - 1))
        return gx, gy

    grid = [[" "] * width for _ in range(height)]
    for i in range(len(tour)):
        a, b = cell(tour[i]), cell(tour[(i + 1) % len(tour)])
        for cx, cy in _bresenham(a, b):
            if grid[cy][cx] == " ":
                grid[cy][cx] = "·"
    for idx in range(len(tsp.cities)):
        cx, cy = cell(idx)
        grid[cy][cx] = _LABELS[idx] if idx < len(_LABELS) else "*"
    return "\n".join("".join(row) for row in grid)


def sparkline(values: list[float]) -> str:
    bars = "▁▂▃▄▅▆▇█"
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1.0
    return "".join(bars[min(7, int((v - lo) / span * 7))] for v in values)
