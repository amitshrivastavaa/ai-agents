"""The Iterated Prisoner's Dilemma match engine.

A strategy is a callable ``fn(mine, theirs, rng) -> 'C' | 'D'`` — a pure
function of the history so far (its own past moves and the opponent's), which
keeps strategies stateless and trivially reusable across matches and evolution.
"""
from __future__ import annotations

# Standard IPD payoffs (my_move, their_move) -> my points.
# T > R > P > S and 2R > T + S, so mutual cooperation beats alternating exploit.
PAYOFF = {
    ("C", "C"): 3,  # reward
    ("C", "D"): 0,  # sucker
    ("D", "C"): 5,  # temptation
    ("D", "D"): 1,  # punishment
}


def play_match(a_fn, b_fn, rounds: int, rng):
    """Play ``rounds`` of IPD between two strategies.

    Returns ``(score_a, score_b, coops_a, coops_b)``. Both players choose
    simultaneously from the history *before* the current round.
    """
    a_hist: list[str] = []
    b_hist: list[str] = []
    sa = sb = ca = cb = 0
    for _ in range(rounds):
        ma = a_fn(a_hist, b_hist, rng)
        mb = b_fn(b_hist, a_hist, rng)
        sa += PAYOFF[(ma, mb)]
        sb += PAYOFF[(mb, ma)]
        ca += ma == "C"
        cb += mb == "C"
        a_hist.append(ma)
        b_hist.append(mb)
    return sa, sb, ca, cb
