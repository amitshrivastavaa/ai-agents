"""Expression trees: build them, evaluate them, print them, and recombine them.

A node is a variable ``x``, a constant, or an operator applied to children.
Operators are *protected* (division by ~zero returns 1, results are clamped) so
that any random tree evaluates to a finite number — essential when the search
is throwing millions of random formulas at the data.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

# name -> (arity, function); all protected against blow-ups
OPS = {
    "+": (2, lambda a, b: a + b),
    "-": (2, lambda a, b: a - b),
    "*": (2, lambda a, b: a * b),
    "/": (2, lambda a, b: a / b if abs(b) > 1e-6 else 1.0),
    "sin": (1, lambda a: math.sin(a)),
    "neg": (1, lambda a: -a),
}
CONSTS = [-2.0, -1.0, 0.5, 1.0, 2.0, 3.0]
_CLAMP = 1e6


@dataclass
class Expr:
    kind: str                       # "var" | "const" | "op"
    value: float = 0.0              # for const
    op: str = ""                    # for op
    children: list = field(default_factory=list)


def evaluate(node: Expr, x: float) -> float:
    if node.kind == "var":
        return x
    if node.kind == "const":
        return node.value
    fn = OPS[node.op][1]
    args = [evaluate(c, x) for c in node.children]
    try:
        v = fn(*args)
    except (OverflowError, ValueError, ZeroDivisionError):
        return _CLAMP
    if v != v or v == float("inf") or v == float("-inf"):   # NaN / inf
        return _CLAMP
    return max(-_CLAMP, min(_CLAMP, v))


def to_string(node: Expr) -> str:
    if node.kind == "var":
        return "x"
    if node.kind == "const":
        v = node.value
        return str(int(v)) if v == int(v) else f"{v:g}"
    if node.op == "neg":
        return f"-({to_string(node.children[0])})"
    if node.op == "sin":
        return f"sin({to_string(node.children[0])})"
    a, b = (to_string(c) for c in node.children)
    return f"({a} {node.op} {b})"


def size(node: Expr) -> int:
    return 1 + sum(size(c) for c in node.children)


def clone(node: Expr) -> Expr:
    return Expr(node.kind, node.value, node.op, [clone(c) for c in node.children])


def simplify(node: Expr, passes: int = 4) -> Expr:
    """Light, semantics-preserving cleanup for prettier display."""
    for _ in range(passes):
        node = _simplify_once(node)
    return node


def _simplify_once(n: Expr) -> Expr:
    if n.kind in ("var", "const"):
        return n
    ch = [_simplify_once(c) for c in n.children]
    n = Expr("op", op=n.op, children=ch)
    if all(c.kind == "const" for c in ch):           # constant folding
        return Expr("const", value=evaluate(n, 0.0))
    if n.op == "neg" and ch[0].kind == "op" and ch[0].op == "neg":
        return ch[0].children[0]                      # --a → a
    if n.op == "*":
        a, b = ch
        for u, v in ((a, b), (b, a)):
            if u.kind == "const" and u.value == 0:
                return Expr("const", value=0.0)
            if u.kind == "const" and u.value == 1:
                return v
            if u.kind == "const" and u.value == -1:
                return Expr("op", op="neg", children=[v])
    if n.op == "+":
        a, b = ch
        if a.kind == "const" and a.value == 0:
            return b
        if b.kind == "const" and b.value == 0:
            return a
    if n.op == "-" and ch[1].kind == "const" and ch[1].value == 0:
        return ch[0]
    if n.op == "/" and ch[1].kind == "const" and ch[1].value == 1:
        return ch[0]
    return n


def random_tree(r, *, depth: int = 0, max_depth: int = 4) -> Expr:
    leaf_chance = 0.3 if depth < max_depth else 1.0
    if depth >= max_depth or r.random() < leaf_chance:
        if r.random() < 0.6:
            return Expr("var")
        return Expr("const", value=r.choice(CONSTS))
    op = r.choice(list(OPS))
    arity = OPS[op][0]
    return Expr("op", op=op, children=[random_tree(r, depth=depth + 1, max_depth=max_depth)
                                       for _ in range(arity)])


def subtree_at(node: Expr, idx: int) -> Expr:
    """Return the idx-th node in pre-order (matching ``replace_at``)."""
    counter = [0]
    found = [node]

    def rec(n: Expr) -> bool:
        if counter[0] == idx:
            found[0] = n
            return True
        counter[0] += 1
        return any(rec(c) for c in n.children)

    rec(node)
    return found[0]


def replace_at(node: Expr, idx: int, new: Expr) -> Expr:
    """Return a copy of ``node`` with its idx-th (pre-order) node replaced."""
    counter = [0]

    def rec(n: Expr) -> Expr:
        cur = counter[0]
        counter[0] += 1
        if cur == idx:
            return clone(new)
        return Expr(n.kind, n.value, n.op, [rec(c) for c in n.children])

    return rec(node)
