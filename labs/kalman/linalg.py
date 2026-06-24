"""Tiny matrix algebra (pure stdlib) — just enough for a Kalman filter.

Matrices are lists of rows; vectors are flat lists.
"""
from __future__ import annotations


def eye(n: int):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def transpose(A):
    return [list(col) for col in zip(*A)]


def matmul(A, B):
    n, k, m = len(A), len(B), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) for j in range(m)]
            for i in range(n)]


def matadd(A, B):
    return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def matsub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def matvec(A, x):
    return [sum(aij * xj for aij, xj in zip(row, x)) for row in A]


def vecadd(a, b):
    return [ai + bi for ai, bi in zip(a, b)]


def vecsub(a, b):
    return [ai - bi for ai, bi in zip(a, b)]


def inv(A):
    """Inverse by Gauss-Jordan elimination with partial pivoting."""
    n = len(A)
    M = [list(row) + e for row, e in zip(A, eye(n))]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[piv][col]) < 1e-12:
            raise ValueError("singular matrix")
        M[col], M[piv] = M[piv], M[col]
        d = M[col][col]
        M[col] = [v / d for v in M[col]]
        for r in range(n):
            if r != col:
                f = M[r][col]
                M[r] = [a - f * b for a, b in zip(M[r], M[col])]
    return [row[n:] for row in M]


def trace(A):
    return sum(A[i][i] for i in range(len(A)))
