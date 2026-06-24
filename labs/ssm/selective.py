"""Selective (Mamba-style) SSM: input-dependent dynamics via the timestep Δ.

Mamba discretizes a continuous SSM with a per-step timestep ``Δ_t`` that *depends
on the input* (zero-order hold):

    ā_t = exp(Δ_t · A)
    b̄_t = (ā_t − 1) / A · B            (A < 0 for stability)

Read off the two regimes:

* **Δ_t large**  → ā_t → 0 and b̄_t → B: the state is *overwritten* by ``x_t``.
* **Δ_t = 0**    → ā_t = 1 and b̄_t = 0: the state is *held* unchanged.

So by choosing ``Δ_t`` from the input, a single SSM can both capture and ignore —
content-based gating that a *time-invariant* model simply cannot express. That is
the whole idea behind Mamba's "selective" state space.
"""
from __future__ import annotations

import math

from .ssm import ssm_scan


def discretize(deltas, A=-1.0, B=1.0):
    """Zero-order-hold discretization → per-step ``(ā_t, b̄_t)`` from ``Δ_t``."""
    abar: list[float] = []
    bbar: list[float] = []
    for dt in deltas:
        a = math.exp(dt * A)
        abar.append(a)
        bbar.append((a - 1.0) / A * B)
    return abar, bbar


def sample_and_hold(values, gates, *, delta_write=12.0, A=-1.0, B=1.0, C=1.0):
    """A selective SSM that captures ``value`` where ``gate==1`` and holds it
    everywhere else.

    The gate drives the (input-dependent) timestep: ``Δ_t = delta_write`` on a
    write, ``0`` on a hold. With a large ``delta_write`` the output equals the
    exact sample-and-hold of ``values`` at the ``gates``.
    """
    deltas = [delta_write if g else 0.0 for g in gates]
    abar, bbar = discretize(deltas, A=A, B=B)
    y, _ = ssm_scan(values, abar, bbar, c=C, d=0.0)
    return y
