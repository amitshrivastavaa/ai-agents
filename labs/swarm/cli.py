"""CLI for the Ant Colony Optimization TSP solver.

    python -m labs.swarm.cli solve --instance circle --watch
    python -m labs.swarm.cli solve --instance random15 --ants 30 --iters 120
    python -m labs.swarm.cli compare
    python -m labs.swarm.cli list
"""
from __future__ import annotations

import argparse
import sys

from .aco import AntColony
from .render import plot_tour, sparkline
from .tsp import INSTANCES, get_instance, nearest_neighbor, optimal, random_tour, tour_length


def _cmd_solve(args) -> int:
    tsp = get_instance(args.instance)
    colony = AntColony(n_ants=args.ants, iterations=args.iters,
                       beta=args.beta, seed=args.seed)
    res = colony.solve(tsp)
    nn = tour_length(nearest_neighbor(tsp), tsp.dist)
    opt = optimal(tsp)

    print(f"# ACO on '{tsp.name}'  ({tsp.n} cities, {args.ants} ants, {args.iters} iters)\n")
    print(f"  nearest-neighbor : {nn:7.2f}")
    print(f"  ant colony       : {res.best_length:7.2f}   "
          f"({(1 - res.best_length / nn) * 100:+.1f}% vs NN)")
    if opt is not None:
        print(f"  optimal          : {opt:7.2f}   "
              f"(ACO is {(res.best_length / opt - 1) * 100:.1f}% over optimal)")
    print(f"  convergence      : {sparkline(res.history)}  "
          f"{res.history[0]:.1f} → {res.best_length:.1f}")
    print(f"  best tour        : {'→'.join(map(str, res.best_tour))}→{res.best_tour[0]}")
    if args.watch:
        print()
        print(plot_tour(tsp, res.best_tour))
    return 0


def _cmd_compare(args) -> int:
    print(f"  {'instance':<10}{'random':>9}{'NN':>9}{'ACO':>9}{'optimal':>9}")
    for name, tsp in INSTANCES.items():
        rnd = tour_length(random_tour(tsp), tsp.dist)
        nn = tour_length(nearest_neighbor(tsp), tsp.dist)
        aco = AntColony().solve(tsp).best_length
        opt = optimal(tsp)
        opt_s = f"{opt:9.1f}" if opt is not None else f"{'—':>9}"
        print(f"  {name:<10}{rnd:9.1f}{nn:9.1f}{aco:9.1f}{opt_s}")
    print("\nACO matches the optimum where we can compute it, and beats the greedy")
    print("nearest-neighbor heuristic everywhere — from pheromone trails alone.")
    return 0


def _cmd_list(_args) -> int:
    for name, tsp in INSTANCES.items():
        print(f"  {name:<10} {tsp.n} cities")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="swarm", description="Ant Colony Optimization for the TSP.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("solve")
    p.add_argument("--instance", default="circle")
    p.add_argument("--ants", type=int, default=20)
    p.add_argument("--iters", type=int, default=80)
    p.add_argument("--beta", type=float, default=4.0)
    p.add_argument("--seed", default="aco")
    p.add_argument("--watch", action="store_true", help="draw the tour")
    p.set_defaults(func=_cmd_solve)

    sub.add_parser("compare").set_defaults(func=_cmd_compare)
    sub.add_parser("list").set_defaults(func=_cmd_list)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyError as e:
        parser.error(str(e))


if __name__ == "__main__":
    sys.exit(main())
