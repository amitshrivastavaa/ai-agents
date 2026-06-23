"""tiny_town — a tiny generative-agent social simulation.

A handful of townspeople, each with a personality, a daily routine, and a
persistent memory, move around a small world, run into each other, hold short
conversations, and form relationships over several days. Friendships and
rivalries *emerge* from trait compatibility and who keeps bumping into whom —
nobody scripts them.

A miniature, fully-offline homage to Stanford's *Generative Agents*
("Smallville"). Each resident's memory is an :class:`labs.agent_memory.MemoryStore`,
so the town is also a demo of the lab's pieces composing. Deterministic via the
shared seeded RNG; a real model can write the dialogue when one is available.
"""
from .sim import Simulation, run
from .world import AGENTS, WORLD, Agent, Location

__all__ = ["Simulation", "run", "AGENTS", "WORLD", "Agent", "Location"]
