"""swarm — Ant Colony Optimization for the Traveling Salesman Problem.

A colony of simple ants finds short tours through *stigmergy*: each ant builds a
tour, biased toward nearby cities and edges already rich in pheromone; shorter
tours then deposit more pheromone, so good edges reinforce and the whole colony
converges on a near-optimal route — no ant ever sees the whole map.

A miniature, fully-offline take on swarm intelligence (ACO; ANTS 2026).
Deterministic via the shared seeded RNG; renders the emerging tour in ASCII.
"""
from .aco import AntColony, ACOResult
from .tsp import TSP, INSTANCES, get_instance, nearest_neighbor, optimal, tour_length

__all__ = [
    "AntColony", "ACOResult",
    "TSP", "INSTANCES", "get_instance", "nearest_neighbor", "optimal", "tour_length",
]
