"""world_model — plan by simulating before you act.

An agent in a small grid world chooses what to do by *imagining* the
consequences of action sequences in an internal model of the world, then
committing to the move that looks best — instead of reacting greedily and
walking into the lava.

Three planners share one environment so you can compare "react" vs "reason":

* **reactive** — greedy toward the goal, no lookahead (steps into hazards).
* **lookahead** — searches the model for the optimal safe path (perfect plan).
* **mcts** — Monte-Carlo Tree Search: rolls out imagined futures and picks the
  move with the best simulated return (the world-model + reasoning flavor).

Fully offline and deterministic (rollouts are seeded).
"""
from .env import GridWorld, MAPS, get_map
from .planners import LookaheadPlanner, MCTSPlanner, ReactivePlanner, get_planner
from .runner import Episode, compare, run_episode

__all__ = [
    "GridWorld", "MAPS", "get_map",
    "ReactivePlanner", "LookaheadPlanner", "MCTSPlanner", "get_planner",
    "Episode", "run_episode", "compare",
]
