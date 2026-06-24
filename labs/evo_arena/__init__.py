"""evo_arena — co-evolving strategies in the Iterated Prisoner's Dilemma.

Two things in one small world:

* an **Axelrod tournament** — classic strategies (Tit-for-Tat, Grim, Pavlov,
  Always-Defect, …) play everyone round-robin and we tally the scores;
* an **evolutionary arena** — a population evolves over generations, the fitter
  strategies reproduce, and you watch cooperation *emerge* (or get invaded).

The evolution comes in two flavours: replicator dynamics over the named
strategies, and a genetic algorithm over *memory-one* strategies that can
rediscover Tit-for-Tat and Pavlov from random genomes. A miniature, offline
take on 2026's multi-agent-evolution wave (CORAL/SAGE). Deterministic.
"""
from .arena import coevolve_memory1, replicator, tournament
from .game import play_match
from .strategies import STRATEGIES, Memory1, get_strategy

__all__ = [
    "play_match", "tournament", "replicator", "coevolve_memory1",
    "STRATEGIES", "Memory1", "get_strategy",
]
