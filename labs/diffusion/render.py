"""ASCII density scatter of generated samples (with target modes overlaid)."""
from __future__ import annotations

from .target import Target

_RAMP = " .:-=+*#%@"


def scatter(samples, target: Target | None = None, *, width: int = 45,
            height: int = 21, span: float | None = None) -> str:
    if span is None:
        span = 1.0
        pts = list(samples) + (target.modes if target else [])
        for x, y in pts:
            span = max(span, abs(x), abs(y))
        span += 2.0

    def cell(x, y):
        gx = int((x + span) / (2 * span) * (width - 1))
        gy = int((span - y) / (2 * span) * (height - 1))
        return gy, gx

    counts = [[0] * width for _ in range(height)]
    for x, y in samples:
        gy, gx = cell(x, y)
        if 0 <= gy < height and 0 <= gx < width:
            counts[gy][gx] += 1
    hi = max((c for row in counts for c in row), default=1) or 1

    grid = [[" "] * width for _ in range(height)]
    for gy in range(height):
        for gx in range(width):
            c = counts[gy][gx]
            if c:
                grid[gy][gx] = _RAMP[min(len(_RAMP) - 1, 1 + int(c / hi * (len(_RAMP) - 2)))]
    if target:                                  # overlay modes as 'o' where empty
        for mx, my in target.modes:
            gy, gx = cell(mx, my)
            if 0 <= gy < height and 0 <= gx < width and grid[gy][gx] == " ":
                grid[gy][gx] = "o"
    return "\n".join("".join(row) for row in grid)
