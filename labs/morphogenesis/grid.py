"""The Gray-Scott reaction-diffusion grid.

Two fields U and V on a toroidal grid. Each step:

    U' = U + (Du·∇²U − U·V² + F·(1−U)) · dt
    V' = V + (Dv·∇²V + U·V² − (F+k)·V) · dt

U is fed in at rate F and V is removed at rate F+k; the U·V² term is the
reaction (U + 2V → 3V). Different (F, k) give wildly different morphologies.
The Laplacian ∇² uses a 3×3 stencil (orthogonal 0.2, diagonal 0.05, centre −1).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .._kernel import rng

# (F, k, description) — classic Gray-Scott regimes
PRESETS: dict[str, tuple[float, float, str]] = {
    "mitosis": (0.0367, 0.0649, "dividing cells (bacteria splitting)"),
    "coral":   (0.0545, 0.0620, "branching coral growth"),
    "maze":    (0.0290, 0.0570, "winding maze of stripes"),
    "spots":   (0.0250, 0.0600, "isolated spots"),
    "holes":   (0.0390, 0.0580, "negative spots / holes"),
}


def get_preset(name: str) -> tuple[float, float, str]:
    try:
        return PRESETS[name]
    except KeyError:
        raise KeyError(f"unknown pattern {name!r}; choose from {sorted(PRESETS)}") from None


@dataclass
class Grid:
    w: int
    h: int
    F: float
    k: float
    Du: float = 0.16
    Dv: float = 0.08
    dt: float = 1.0
    U: list[float] = field(default_factory=list)
    V: list[float] = field(default_factory=list)
    _idx: list[tuple] = field(default_factory=list, repr=False)
    steps_run: int = 0

    @classmethod
    def from_preset(cls, name: str, *, w: int = 56, h: int = 26,
                    seed: str = "morph") -> "Grid":
        F, k, _ = get_preset(name)
        g = cls(w=w, h=h, F=F, k=k)
        g._build_index()
        g.seed(seed=seed)
        return g

    def _build_index(self) -> None:
        w, h = self.w, self.h
        idx = []
        for y in range(h):
            for x in range(w):
                c = y * w + x
                n, s = ((y - 1) % h) * w + x, ((y + 1) % h) * w + x
                we, ea = y * w + (x - 1) % w, y * w + (x + 1) % w
                nw = ((y - 1) % h) * w + (x - 1) % w
                ne = ((y - 1) % h) * w + (x + 1) % w
                sw = ((y + 1) % h) * w + (x - 1) % w
                se = ((y + 1) % h) * w + (x + 1) % w
                idx.append((c, n, s, we, ea, nw, ne, sw, se))
        self._idx = idx

    def seed(self, *, seed: str = "morph") -> None:
        """U=1, V=0 everywhere, with a central block plus light noise of V."""
        n = self.w * self.h
        self.U = [1.0] * n
        self.V = [0.0] * n
        r = rng(seed, self.w, self.h)
        cx, cy = self.w // 2, self.h // 2
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                c = ((cy + dy) % self.h) * self.w + (cx + dx) % self.w
                self.U[c], self.V[c] = 0.5, 0.25
        for c in range(n):           # sparse seeded nucleation sites
            if r.random() < 0.04:
                self.V[c] = 0.5
        self.steps_run = 0

    def step(self, n: int = 1) -> None:
        U, V = self.U, self.V
        Du, Dv, F, k, dt = self.Du, self.Dv, self.F, self.k, self.dt
        for _ in range(n):
            nU = U[:]
            nV = V[:]
            for c, no, so, we, ea, nw, ne, sw, se in self._idx:
                u, v = U[c], V[c]
                lu = 0.2 * (U[no] + U[so] + U[we] + U[ea]) + \
                    0.05 * (U[nw] + U[ne] + U[sw] + U[se]) - u
                lv = 0.2 * (V[no] + V[so] + V[we] + V[ea]) + \
                    0.05 * (V[nw] + V[ne] + V[sw] + V[se]) - v
                uvv = u * v * v
                nU[c] = u + (Du * lu - uvv + F * (1 - u)) * dt
                nV[c] = v + (Dv * lv + uvv - (F + k) * v) * dt
            U, V = nU, nV
        self.U, self.V = U, V
        self.steps_run += n

    def damage(self, *, x0: int, y0: int, x1: int, y1: int) -> None:
        """Wipe a rectangular region back to the resting state (U=1, V=0)."""
        for y in range(y0, y1):
            for x in range(x0, x1):
                c = (y % self.h) * self.w + (x % self.w)
                self.U[c], self.V[c] = 1.0, 0.0

    def v_field(self) -> list[float]:
        return self.V

    def activity(self) -> float:
        """Mean V — a scalar measure of how much pattern is present."""
        return sum(self.V) / len(self.V)
