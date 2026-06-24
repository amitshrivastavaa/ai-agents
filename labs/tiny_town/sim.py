"""The simulation: routines move residents around; co-location sparks talk;
talk builds (or strains) relationships; reflection forms opinions.

Everything is deterministic given ``(seed, days)``. Conversations are templated
offline and persona/location-aware; with a real model attached each line could
be generated instead (the encounter shape is identical).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

from .._kernel import pick, rng
from ..agent_memory import MemoryStore
from .world import LOCATIONS, PHASES, Agent, fresh_agents


def _clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def choose_location(agent: Agent, phase: str) -> str:
    t = agent.traits
    if phase in ("morning", "night"):
        return agent.home
    if phase == "forenoon":
        return agent.work
    if phase == "noon":
        return "Cafe" if ("foodie" in t or "outgoing" in t) else "Market"
    if phase == "afternoon":
        if "athletic" in t:
            return "Park"
        if "bookish" in t:
            return "Library"
        return agent.work
    # evening
    if "outgoing" in t or "foodie" in t:
        return "Cafe"
    if "athletic" in t:
        return "Park"
    return "Library"


def base_affinity(a: Agent, b: Agent) -> float:
    shared = len(a.traits & b.traits)
    jitter = (rng("affinity", *sorted((a.name, b.name))).random() - 0.5) * 0.4
    return _clamp(0.35 * shared - 0.15 + jitter)


def choose_topic(a: Agent, b: Agent, loc: str) -> str:
    shared = a.traits & b.traits
    kind = LOCATIONS[loc].kind
    if kind == "food" or "foodie" in shared:
        pool = ("the new menu", "a recipe they tried", "the best lunch in town")
    elif loc == "Library" or "bookish" in shared:
        pool = ("a book they're reading", "a story idea", "a strange article")
    elif loc == "Park" or "athletic" in shared:
        pool = ("a morning run", "training plans", "the trail up the hill")
    elif "outgoing" in (a.traits | b.traits):
        pool = ("weekend plans", "town gossip", "a party they're hosting")
    else:
        pool = ("the weather", "work", "nothing much")
    return pick(pool, a.name, b.name, loc)


@dataclass
class Event:
    day: int
    phase: str
    kind: str          # "meet" | "reflect"
    text: str


def _converse(a: Agent, b: Agent, loc: str, phase: str, day: int) -> Event:
    aff = base_affinity(a, b)
    topic = choose_topic(a, b, loc)
    for x, y in ((a, b), (b, a)):
        # relationship eases toward affinity, plus a small "we met again" warmth
        new = _clamp(x.rel(y.name) + 0.25 * (aff - x.rel(y.name)) + 0.05)
        x.relationships[y.name] = new
        x.met_counts[y.name] = x.met_counts.get(y.name, 0) + 1
        importance = 3.0 + 2.0 * abs(aff)
        # Lead with the person + place so reflection clusters on *who* a resident
        # keeps running into (the emergent social insight), not the verb "talked".
        x.memory.observe(
            f"{y.name} at the {loc} — {topic}.",
            importance=importance,
        )
    tone = "warmly" if aff > 0.25 else "politely" if aff > -0.1 else "stiffly"
    return Event(day, phase, "meet",
                 f"{a.name} and {b.name} met at the {loc} and chatted {tone} about {topic}.")


def rel_label(score: float) -> str:
    if score >= 0.55:
        return "close friends"
    if score >= 0.25:
        return "friends"
    if score >= -0.05:
        return "acquaintances"
    return "on tense terms"


@dataclass
class Simulation:
    agents: list[Agent]
    chronicle: list[Event]
    days: int
    boards: list[tuple[int, str, dict[str, list[str]]]] = field(default_factory=list)

    def strongest_bond(self) -> tuple[str, str, float] | None:
        best = None
        for a, b in combinations(self.agents, 2):
            score = (a.rel(b.name) + b.rel(a.name)) / 2
            if best is None or score > best[2]:
                best = (a.name, b.name, score)
        return best

    def to_dict(self) -> dict:
        return {
            "days": self.days,
            "residents": [
                {
                    "name": a.name,
                    "traits": sorted(a.traits),
                    "visited": sorted(a.visited),
                    "relationships": {
                        other: {
                            "score": round(a.rel(other), 3),
                            "label": rel_label(a.rel(other)),
                            "met": a.met_counts.get(other, 0),
                        }
                        for other in sorted(a.relationships)
                    },
                }
                for a in self.agents
            ],
            "events": len(self.chronicle),
        }


def run(days: int = 2, *, seed: str = "town", record_boards: bool = False) -> Simulation:
    agents = fresh_agents()
    for ag in agents:
        ag.memory = MemoryStore(dims=128, reflect_threshold=12.0)

    chronicle: list[Event] = []
    boards: list[tuple[int, str, dict[str, list[str]]]] = []

    for day in range(1, days + 1):
        for phase in PHASES:
            for ag in agents:
                ag.location = choose_location(ag, phase)
                ag.visited.add(ag.location)

            by_loc: dict[str, list[Agent]] = {}
            for ag in agents:
                by_loc.setdefault(ag.location, []).append(ag)

            for loc in sorted(by_loc):
                group = by_loc[loc]
                if len(group) < 2:
                    continue
                for a, b in combinations(group, 2):
                    chronicle.append(_converse(a, b, loc, phase, day))

            if record_boards:
                boards.append((day, phase, {loc: [a.name for a in g]
                                            for loc, g in sorted(by_loc.items())}))

        # end of day: each resident reflects on who they keep meeting
        for ag in agents:
            insights = ag.memory.reflect(force=True)
            if insights:
                chronicle.append(Event(day, "reflect", "reflect",
                                       f"{ag.name} reflects — {insights[0].text}"))

    return Simulation(agents=agents, chronicle=chronicle, days=days, boards=boards)
