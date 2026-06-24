"""ASCII rendering of attention weights."""
from __future__ import annotations

_BLOCKS = " ▏▎▍▌▋▊▉█"
_RAMP = " ·:-=+*#%@"


def attention_bars(seq, weights) -> str:
    """Show each attended position (token + a bar proportional to its weight)."""
    rows = ["  pos  token            attention"]
    for i, w in enumerate(weights):
        bar = _BLOCKS[-1] * int(w * 24) + _BLOCKS[min(8, int((w * 24 % 1) * 8))]
        rows.append(f"  {i:>3}  {str(seq[i])[:16]:<16} {bar} {w:.2f}")
    return "\n".join(rows)


def self_attention_grid(labels, matrix) -> str:
    """Render an n×n attention matrix as a shaded grid (rows = queries)."""
    width = max(len(str(l)) for l in labels)
    head = " " * (width + 2) + " ".join(f"{str(l)[:width]:>{width}}" for l in labels)
    rows = [head]
    for l, row in zip(labels, matrix):
        cells = " ".join(f"{_RAMP[int(min(1.0, v) * (len(_RAMP) - 1))]:>{width}}" for v in row)
        rows.append(f"{str(l)[:width]:>{width}}  {cells}")
    return "\n".join(rows)
