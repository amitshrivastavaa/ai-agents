"""Strategies: the classic named ones plus an evolvable memory-one family.

Each named strategy is a pure function of history. ``Memory1`` is parameterized
by five cooperation probabilities (an opening plus one per last-round outcome),
so the whole space of memory-one strategies — Tit-for-Tat, Pavlov, Always-Defect
and everything between — is reachable by a genetic algorithm.
"""
from __future__ import annotations

from dataclasses import dataclass

C, D = "C", "D"


def all_c(mine, theirs, rng):
    return C


def all_d(mine, theirs, rng):
    return D


def tit_for_tat(mine, theirs, rng):
    return theirs[-1] if theirs else C


def suspicious_tft(mine, theirs, rng):
    return theirs[-1] if theirs else D


def grim(mine, theirs, rng):
    return D if D in theirs else C  # cooperate until ever betrayed, then never


def tit_for_two_tats(mine, theirs, rng):
    return D if theirs[-2:] == [D, D] else C


def pavlov(mine, theirs, rng):
    # win-stay/lose-shift: repeat last move if it earned a good payoff (R or T)
    if not mine:
        return C
    good = (mine[-1] == C and theirs[-1] == C) or (mine[-1] == D and theirs[-1] == C)
    return mine[-1] if good else (D if mine[-1] == C else C)


def random_5050(mine, theirs, rng):
    return C if rng.random() < 0.5 else D


STRATEGIES = {
    "AllC": all_c,
    "AllD": all_d,
    "TitForTat": tit_for_tat,
    "Suspicious": suspicious_tft,
    "Grim": grim,
    "TitFor2Tats": tit_for_two_tats,
    "Pavlov": pavlov,
    "Random": random_5050,
}

# strategies with no randomness — used for the (deterministic) replicator dynamics
DETERMINISTIC = ["AllC", "AllD", "TitForTat", "Grim", "TitFor2Tats", "Pavlov"]


def get_strategy(name: str):
    try:
        return STRATEGIES[name]
    except KeyError:
        raise KeyError(f"unknown strategy {name!r}; choose from {sorted(STRATEGIES)}") from None


@dataclass(frozen=True)
class Memory1:
    """A memory-one strategy: P(cooperate) keyed on the last round's outcome.

    Genome = (open, p_cc, p_cd, p_dc, p_dd), each a probability. ``open`` is the
    first-move cooperation chance; the rest are P(cooperate) given (my, their)
    moves last round. Tit-for-Tat ≈ (1, 1, 0, 1, 0); Pavlov ≈ (1, 1, 0, 0, 1);
    Always-Defect ≈ (0, 0, 0, 0, 0).
    """

    open: float
    p_cc: float
    p_cd: float
    p_dc: float
    p_dd: float

    def __call__(self, mine, theirs, rng):
        if not mine:
            p = self.open
        else:
            p = {(C, C): self.p_cc, (C, D): self.p_cd,
                 (D, C): self.p_dc, (D, D): self.p_dd}[(mine[-1], theirs[-1])]
        return C if rng.random() < p else D

    def genome(self) -> tuple[float, ...]:
        return (self.open, self.p_cc, self.p_cd, self.p_dc, self.p_dd)

    def nearest_named(self) -> str:
        """Closest classic memory-one archetype, for human-readable reporting."""
        archetypes = {
            "TitForTat": (1, 1, 0, 1, 0),
            "Pavlov": (1, 1, 0, 0, 1),
            "AllD": (0, 0, 0, 0, 0),
            "AllC": (1, 1, 1, 1, 1),
            "Grim-ish": (1, 1, 0, 0, 0),
        }
        g = self.genome()
        best, best_d = None, 1e9
        for name, arc in archetypes.items():
            d = sum(abs(a - b) for a, b in zip(g, arc))
            if d < best_d:
                best, best_d = name, d
        return f"{best}~{best_d:.1f}"
