"""Demo: watch the colony find the ring, then beat nearest-neighbor.

    python -m labs.swarm.demo
"""
from __future__ import annotations

from .aco import AntColony
from .render import plot_tour, sparkline
from .tsp import get_instance, nearest_neighbor, optimal, tour_length


def main() -> int:
    print("On a ring of 12 cities, the optimal tour IS the perimeter.")
    circle = get_instance("circle")
    res = AntColony().solve(circle)
    opt = optimal(circle)
    print(f"  ACO found {res.best_length:.1f} (optimal {opt:.1f}) — "
          f"{(res.best_length / opt - 1) * 100:.1f}% over optimal\n")
    print(plot_tour(circle, res.best_tour))

    print("\n" + "=" * 50)
    print("On 15 scattered cities, ACO beats the greedy heuristic:\n")
    tsp = get_instance("random15")
    nn = tour_length(nearest_neighbor(tsp), tsp.dist)
    res = AntColony().solve(tsp)
    print(f"  nearest-neighbor: {nn:.1f}")
    print(f"  ant colony      : {res.best_length:.1f}  ({(1 - res.best_length / nn) * 100:+.1f}%)")
    print(f"  convergence     : {sparkline(res.history)}")
    print()
    print(plot_tour(tsp, res.best_tour))
    print("\nNo ant sees the whole map — the short tour emerges from pheromone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
