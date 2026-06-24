"""Binary glyph patterns (7×7) plus corruption and ASCII rendering helpers.

A pattern is a list of ±1 over ``W*H`` neurons: ``#`` → +1 (on), ``.`` → -1 (off).
"""
from __future__ import annotations

from .._kernel import rng

W, H = 7, 7
SIZE = (W, H)

_GLYPH_ART = {
    "T": ["#######",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "...#...",
          "...#..."],
    "L": ["#......",
          "#......",
          "#......",
          "#......",
          "#......",
          "#......",
          "#######"],
    "O": [".#####.",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          "#.....#",
          ".#####."],
    "X": ["#.....#",
          ".#...#.",
          "..#.#..",
          "...#...",
          "..#.#..",
          ".#...#.",
          "#.....#"],
    "H": ["#.....#",
          "#.....#",
          "#.....#",
          "#######",
          "#.....#",
          "#.....#",
          "#.....#"],
}


def to_vec(rows: list[str]) -> list[int]:
    return [1 if ch == "#" else -1 for row in rows for ch in row]


GLYPHS: dict[str, list[int]] = {name: to_vec(art) for name, art in _GLYPH_ART.items()}


def render(vec: list[int], *, on: str = "#", off: str = "·") -> str:
    rows = []
    for r in range(H):
        rows.append("".join(on if vec[r * W + c] == 1 else off for c in range(W)))
    return "\n".join(rows)


def side_by_side(*labelled: tuple[str, list[int]]) -> str:
    """Render several patterns next to each other with captions."""
    blocks = [render(v).splitlines() for _, v in labelled]
    captions = [name for name, _ in labelled]
    out = ["   ".join(f"{c:<{W}}" for c in captions)]
    for r in range(H):
        out.append("   ".join(block[r] for block in blocks))
    return "\n".join(out)


def corrupt(vec: list[int], noise: float, *, seed: str = "noise") -> list[int]:
    """Flip each neuron independently with probability ``noise``."""
    r = rng(seed, noise, tuple(vec))
    return [-x if r.random() < noise else x for x in vec]


def occlude(vec: list[int], fraction: float = 0.5) -> list[int]:
    """Erase (set to -1) the bottom ``fraction`` of rows — a partial cue."""
    out = list(vec)
    cutoff = int(H * (1 - fraction))
    for r in range(cutoff, H):
        for c in range(W):
            out[r * W + c] = -1
    return out
