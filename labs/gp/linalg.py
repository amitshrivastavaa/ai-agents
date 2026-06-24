"""Cholesky factorization and triangular solves — the numerically right way to
invert a symmetric positive-definite kernel matrix.

A GP needs ``K⁻¹y`` and ``K⁻¹k*``; with ``K = L·Lᵀ`` (``L`` lower-triangular) those
are two cheap triangular solves and never form the inverse explicitly.
"""
from __future__ import annotations

import math


def cholesky(A):
    """Lower-triangular ``L`` with ``L·Lᵀ = A`` for symmetric positive-definite A."""
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                d = A[i][i] - s
                if d <= 0:
                    raise ValueError("matrix not positive-definite")
                L[i][j] = math.sqrt(d)
            else:
                L[i][j] = (A[i][j] - s) / L[j][j]
    return L


def solve_lower(L, b):
    """Solve ``L·y = b`` (forward substitution)."""
    n = len(b)
    y = [0.0] * n
    for i in range(n):
        y[i] = (b[i] - sum(L[i][k] * y[k] for k in range(i))) / L[i][i]
    return y


def solve_upper_T(L, y):
    """Solve ``Lᵀ·x = y`` (back substitution, using ``L`` in place of ``Lᵀ``)."""
    n = len(y)
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (y[i] - sum(L[k][i] * x[k] for k in range(i + 1, n))) / L[i][i]
    return x


def chol_solve(L, b):
    """Solve ``K·x = b`` where ``K = L·Lᵀ``."""
    return solve_upper_T(L, solve_lower(L, b))
