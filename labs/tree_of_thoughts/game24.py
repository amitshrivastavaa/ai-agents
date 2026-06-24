"""The Game of 24: exact state space, expansion, and a ground-truth solver.

A *state* is a tuple of remaining numbers (as exact ``Fraction``s). A *step*
combines two of them with an operator, shrinking the state by one. Reaching the
single number 24 wins. Everything is exact, so divisions like ``8/(3 - 8/3)``
resolve correctly instead of drowning in float error.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

TARGET = Fraction(24)


@dataclass(frozen=True)
class Step:
    a: Fraction
    op: str
    b: Fraction
    result: Fraction

    def __str__(self) -> str:
        def fmt(x: Fraction) -> str:
            return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
        return f"{fmt(self.a)} {self.op} {fmt(self.b)} = {fmt(self.result)}"


State = tuple[Fraction, ...]


def to_state(numbers) -> State:
    return tuple(sorted(Fraction(n) for n in numbers))


def _combine(a: Fraction, b: Fraction):
    """All distinct (x, op, y, result) tuples where ``x op y == result``."""
    yield a, "+", b, a + b
    yield a, "*", b, a * b
    yield a, "-", b, a - b
    if a != b:
        yield b, "-", a, b - a  # the other order, only when it differs
    if b != 0:
        yield a, "/", b, a / b
    if a != 0 and a != b:
        yield b, "/", a, b / a


def expand(state: State):
    """Yield (child_state, Step) for every way to combine two numbers."""
    n = len(state)
    seen: set[tuple] = set()
    for i in range(n):
        for j in range(i + 1, n):
            a, b = state[i], state[j]
            rest = [state[k] for k in range(n) if k != i and k != j]
            for x, op, y, res in _combine(a, b):
                child = tuple(sorted(rest + [res]))
                key = (child, x, op, y, res)
                if key in seen:
                    continue
                seen.add(key)
                yield child, Step(x, op, y, res)


def is_goal(state: State) -> bool:
    return len(state) == 1 and state[0] == TARGET


def exact_solve(numbers) -> list[Step] | None:
    """Ground-truth DFS: return a winning sequence of steps, or None."""
    start = to_state(numbers)

    def dfs(state: State, path: list[Step]) -> list[Step] | None:
        if is_goal(state):
            return path
        if len(state) == 1:
            return None
        for child, step in expand(state):
            got = dfs(child, path + [step])
            if got is not None:
                return got
        return None

    return dfs(start, [])


def reachable(numbers) -> bool:
    return exact_solve(numbers) is not None


def expression(path: list[Step]) -> str:
    """Render a solution path as a readable chain of moves."""
    return "  →  ".join(str(s) for s in path)
