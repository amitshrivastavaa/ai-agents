"""The CartPole environment (the standard Barto/Sutton / Gym CartPole-v1).

State is (x, x_dot, theta, theta_dot). Each step pushes the cart left or right;
the episode ends when the pole tips past 12° or the cart leaves the track, and
survives at most ``max_steps`` — so longer balancing = higher reward.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .._kernel import rng

GRAVITY = 9.8
MASS_CART = 1.0
MASS_POLE = 0.1
TOTAL_MASS = MASS_CART + MASS_POLE
LENGTH = 0.5                      # half the pole's length
POLEMASS_LENGTH = MASS_POLE * LENGTH
FORCE_MAG = 10.0
TAU = 0.02                        # seconds between updates

X_LIMIT = 2.4
THETA_LIMIT = 12 * math.pi / 180  # 12 degrees in radians


@dataclass
class CartPole:
    max_steps: int = 500
    x: float = 0.0
    x_dot: float = 0.0
    theta: float = 0.0
    theta_dot: float = 0.0
    steps: int = 0

    def reset(self, *, seed: str = "cp") -> list[float]:
        r = rng(seed)
        self.x, self.x_dot, self.theta, self.theta_dot = (
            r.uniform(-0.05, 0.05) for _ in range(4))
        self.steps = 0
        return self.state()

    def state(self) -> list[float]:
        return [self.x, self.x_dot, self.theta, self.theta_dot]

    def step(self, action: int):
        """action: 0 = push left, 1 = push right. Returns (state, reward, done)."""
        force = FORCE_MAG if action == 1 else -FORCE_MAG
        ct, st = math.cos(self.theta), math.sin(self.theta)
        temp = (force + POLEMASS_LENGTH * self.theta_dot ** 2 * st) / TOTAL_MASS
        theta_acc = (GRAVITY * st - ct * temp) / (
            LENGTH * (4.0 / 3.0 - MASS_POLE * ct ** 2 / TOTAL_MASS))
        x_acc = temp - POLEMASS_LENGTH * theta_acc * ct / TOTAL_MASS

        self.x += TAU * self.x_dot
        self.x_dot += TAU * x_acc
        self.theta += TAU * self.theta_dot
        self.theta_dot += TAU * theta_acc
        self.steps += 1

        done = (abs(self.x) > X_LIMIT or abs(self.theta) > THETA_LIMIT
                or self.steps >= self.max_steps)
        return self.state(), 1.0, done

    def rollout(self, policy, *, seed: str = "cp") -> int:
        """Run one episode under ``policy``; return the number of steps balanced."""
        state = self.reset(seed=seed)
        total = 0
        done = False
        while not done:
            state, reward, done = self.step(policy.act(state))
            total += int(reward)
        return total
