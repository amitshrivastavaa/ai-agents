"""neuroevolution — evolve a neural-net controller, with no gradients at all.

The classic CartPole: a pole hinged on a cart that must be kept upright by
pushing the cart left or right. Instead of training the controller with
backprop, we **evolve** it — a population of tiny neural networks, the ones that
balance longest get to reproduce (with mutation), and over a few generations a
network that keeps the pole up for the full episode emerges.

Gradient-free reinforcement learning (an evolution strategy) on the iconic
control benchmark. Fully offline, deterministic, with an ASCII view of the
balancing cart. The 2026 "agents that improve themselves" theme, from scratch.
"""
from .cartpole import CartPole
from .evolve import EvolveResult, evolve
from .policy import Policy

__all__ = ["CartPole", "Policy", "evolve", "EvolveResult"]
