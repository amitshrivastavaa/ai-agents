"""STRIPS actions and the state-transition functions.

A *fact* is a tuple like ``("on", "A", "B")``; a *state* is a frozenset of facts.
An :class:`Action` is applicable when its preconditions hold, and applying it
deletes its delete-effects and adds its add-effects.
"""
from __future__ import annotations

from dataclasses import dataclass

Fact = tuple
State = frozenset


@dataclass(frozen=True)
class Action:
    name: str
    pre: frozenset
    add: frozenset
    delete: frozenset

    def __str__(self) -> str:
        return self.name


def applicable(action: Action, state: State) -> bool:
    return action.pre <= state


def apply_action(action: Action, state: State) -> State:
    return (state - action.delete) | action.add


def satisfies(state: State, goal: State) -> bool:
    return goal <= state
