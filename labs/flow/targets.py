"""2-D target point sets — the data the flow learns to transport noise onto."""
from __future__ import annotations

import math


def ring(k: int = 24, r: float = 4.0):
    return [[r * math.cos(2 * math.pi * i / k), r * math.sin(2 * math.pi * i / k)]
            for i in range(k)]


def clusters(per: int = 1):
    centers = [(-4, -4), (4, 4), (-4, 4), (4, -4)]
    return [[float(cx), float(cy)] for (cx, cy) in centers for _ in range(per)]


def grid(n: int = 5, span: float = 4.0):
    if n == 1:
        return [[0.0, 0.0]]
    step = 2 * span / (n - 1)
    return [[-span + step * i, -span + step * j] for i in range(n) for j in range(n)]


def two_moons(k: int = 16, r: float = 4.0):
    pts = []
    for i in range(k):
        a = math.pi * i / (k - 1)
        pts.append([r * math.cos(a) - 2.0, r * math.sin(a) - 1.0])
        pts.append([r * math.cos(a) + 2.0, -r * math.sin(a) + 1.0])
    return pts


def spiral(k: int = 40, turns: float = 2.0, r: float = 5.0):
    pts = []
    for i in range(k):
        f = i / (k - 1)
        ang = 2 * math.pi * turns * f
        rad = r * f
        pts.append([rad * math.cos(ang), rad * math.sin(ang)])
    return pts


def get(name: str):
    return {
        "ring": ring(),
        "clusters": clusters(),
        "grid": grid(),
        "moons": two_moons(),
        "spiral": spiral(),
    }[name]


NAMES = ["ring", "clusters", "grid", "moons", "spiral"]
