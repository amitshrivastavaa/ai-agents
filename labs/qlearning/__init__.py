"""qlearning — an agent that learns to navigate a world from reward alone.

No model of the world, no planning ahead: the agent just acts, sees the reward,
and nudges its value estimates with the temporal-difference rule

    Q(s,a) ← Q(s,a) + α · ( r + γ·maxₐ' Q(s',a') − Q(s,a) ).

Over many episodes the Q-table fills in, a policy emerges (greedy on Q), and on
the classic *cliff-walking* world it discovers the optimal route. Watch the
value function light up and the policy arrows snap into place in ASCII.

The reinforcement-learning counterpart to the lab's `world_model` (which plans)
and `neuroevolution` (which evolves). Fully offline, deterministic, and checked
against value iteration (the dynamic-programming optimum).
"""
from .agent import QLearningAgent, train
from .gridworld import GridWorld, MAPS, get_map
from .dp import value_iteration

__all__ = ["QLearningAgent", "train", "GridWorld", "MAPS", "get_map", "value_iteration"]
