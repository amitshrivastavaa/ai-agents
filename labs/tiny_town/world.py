"""The town: its map, its locations, and its residents.

Geometry is deliberately tiny — locations sit on a small grid only so the
``--watch`` view can draw an ASCII map. The social simulation keys off *named
locations* (who is at the Cafe at noon), not pixel positions.
"""
from __future__ import annotations

from dataclasses import dataclass, field

GRID_W, GRID_H = 18, 9

PHASES = ("morning", "forenoon", "noon", "afternoon", "evening", "night")


@dataclass(frozen=True)
class Location:
    name: str
    x: int
    y: int
    glyph: str
    kind: str  # home | work | food | leisure | study


LOCATIONS: dict[str, Location] = {
    loc.name: loc for loc in (
        Location("Home_A", 1, 1, "🏠", "home"),
        Location("Home_B", 16, 1, "🏠", "home"),
        Location("Home_C", 1, 7, "🏠", "home"),
        Location("Office", 8, 2, "🏢", "work"),
        Location("Library", 14, 6, "📚", "study"),
        Location("Cafe", 9, 4, "☕", "food"),
        Location("Park", 4, 5, "🌳", "leisure"),
        Location("Market", 15, 3, "🛒", "food"),
    )
}


@dataclass
class Agent:
    name: str
    initial: str
    traits: frozenset[str]
    home: str
    work: str
    # mutable simulation state
    location: str = ""
    relationships: dict[str, float] = field(default_factory=dict)
    met_counts: dict[str, int] = field(default_factory=dict)
    visited: set[str] = field(default_factory=set)
    memory: object = None  # an agent_memory.MemoryStore, attached at sim start

    def rel(self, other: str) -> float:
        return self.relationships.get(other, 0.0)


AGENTS: list[Agent] = [
    Agent("Alice", "A", frozenset({"outgoing", "foodie"}), "Home_A", "Office"),
    Agent("Bram", "B", frozenset({"bookish", "quiet"}), "Home_B", "Library"),
    Agent("Cleo", "C", frozenset({"athletic", "outgoing"}), "Home_A", "Office"),
    Agent("Dex", "D", frozenset({"foodie", "quiet"}), "Home_B", "Market"),
    Agent("Wren", "W", frozenset({"bookish", "athletic"}), "Home_C", "Library"),
]


def fresh_agents() -> list[Agent]:
    """A deep-ish copy of the roster with clean simulation state."""
    return [
        Agent(a.name, a.initial, a.traits, a.home, a.work)
        for a in AGENTS
    ]


WORLD = LOCATIONS
