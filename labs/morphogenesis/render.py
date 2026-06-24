"""ASCII shading of the V field."""
from __future__ import annotations

from .grid import Grid

_RAMP = " .·:-=+*#%@"


def shade(grid: Grid, *, vmax: float = 0.4) -> str:
    ramp = _RAMP
    last = len(ramp) - 1
    rows = []
    for y in range(grid.h):
        row = []
        for x in range(grid.w):
            v = grid.V[y * grid.w + x]
            level = int(max(0.0, min(1.0, v / vmax)) * last)
            row.append(ramp[level])
        rows.append("".join(row))
    return "\n".join(rows)
