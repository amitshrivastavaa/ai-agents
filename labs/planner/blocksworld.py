"""The blocks-world domain: grounded actions and a few classic problems."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations

from .strips import Action


def ground_actions(blocks) -> list[Action]:
    """Every grounded pickup/putdown/stack/unstack over ``blocks``."""
    actions = []
    for x in blocks:
        actions.append(Action(
            f"pickup({x})",
            pre=frozenset({("clear", x), ("ontable", x), ("handempty",)}),
            add=frozenset({("holding", x)}),
            delete=frozenset({("clear", x), ("ontable", x), ("handempty",)})))
        actions.append(Action(
            f"putdown({x})",
            pre=frozenset({("holding", x)}),
            add=frozenset({("ontable", x), ("clear", x), ("handempty",)}),
            delete=frozenset({("holding", x)})))
    for x, y in permutations(blocks, 2):
        actions.append(Action(
            f"stack({x},{y})",
            pre=frozenset({("holding", x), ("clear", y)}),
            add=frozenset({("on", x, y), ("clear", x), ("handempty",)}),
            delete=frozenset({("holding", x), ("clear", y)})))
        actions.append(Action(
            f"unstack({x},{y})",
            pre=frozenset({("on", x, y), ("clear", x), ("handempty",)}),
            add=frozenset({("holding", x), ("clear", y)}),
            delete=frozenset({("on", x, y), ("clear", x), ("handempty",)})))
    return actions


@dataclass
class Problem:
    name: str
    blocks: tuple
    init: frozenset
    goal: frozenset


def _tower(blocks):
    """init facts for a single tower blocks[0] on blocks[1] on ... on table."""
    facts = {("handempty",), ("clear", blocks[0]), ("ontable", blocks[-1])}
    for upper, lower in zip(blocks, blocks[1:]):
        facts.add(("on", upper, lower))
    return frozenset(facts)


PROBLEMS = {
    # the Sussman anomaly: C on A, A and B on the table; want A on B on C
    "sussman": Problem(
        "sussman", ("A", "B", "C"),
        init=frozenset({("on", "C", "A"), ("ontable", "A"), ("ontable", "B"),
                        ("clear", "C"), ("clear", "B"), ("handempty",)}),
        goal=frozenset({("on", "A", "B"), ("on", "B", "C")})),
    # invert a tower: A/B/C  ->  C/B/A
    "reverse": Problem(
        "reverse", ("A", "B", "C"),
        init=_tower(("A", "B", "C")),
        goal=frozenset({("on", "C", "B"), ("on", "B", "A")})),
    # build a 4-tower from scattered blocks
    "build4": Problem(
        "build4", ("A", "B", "C", "D"),
        init=frozenset({("ontable", "A"), ("ontable", "B"), ("ontable", "C"),
                        ("ontable", "D"), ("clear", "A"), ("clear", "B"),
                        ("clear", "C"), ("clear", "D"), ("handempty",)}),
        goal=frozenset({("on", "A", "B"), ("on", "B", "C"), ("on", "C", "D")})),
}


def get_problem(name: str) -> Problem:
    try:
        return PROBLEMS[name]
    except KeyError:
        raise KeyError(f"unknown problem {name!r}; choose from {sorted(PROBLEMS)}") from None
