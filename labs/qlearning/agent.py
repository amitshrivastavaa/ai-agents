"""The Q-learning agent and its training loop (model-free, tabular)."""
from __future__ import annotations

from dataclasses import dataclass, field

from .._kernel import rng
from .gridworld import ACTIONS, GridWorld


@dataclass
class QLearningAgent:
    alpha: float = 0.5          # learning rate
    gamma: float = 0.95         # discount
    Q: dict = field(default_factory=dict)

    def q(self, s) -> list[float]:
        return self.Q.setdefault(s, [0.0, 0.0, 0.0, 0.0])

    def value(self, s) -> float:
        return max(self.q(s))

    def greedy_action(self, s) -> int:
        qs = self.q(s)
        return max(range(len(ACTIONS)), key=lambda a: qs[a])

    def act(self, s, epsilon: float, r) -> int:
        if r.random() < epsilon:
            return r.randrange(len(ACTIONS))
        return self.greedy_action(s)

    def update(self, s, a: int, reward: float, s2, done: bool) -> None:
        target = reward + (0.0 if done else self.gamma * self.value(s2))
        self.q(s)[a] += self.alpha * (target - self.q(s)[a])


@dataclass
class TrainResult:
    agent: QLearningAgent
    rewards: list[float]        # total reward per episode (the learning curve)
    episodes: int

    def smoothed(self, window: int = 20) -> list[float]:
        out = []
        for i in range(len(self.rewards)):
            lo = max(0, i - window + 1)
            chunk = self.rewards[lo:i + 1]
            out.append(sum(chunk) / len(chunk))
        return out


def train(env: GridWorld, *, episodes: int = 400, alpha: float = 0.5, gamma: float = 0.95,
          eps_start: float = 1.0, eps_end: float = 0.05, max_steps: int = 200,
          seed: str = "ql") -> TrainResult:
    agent = QLearningAgent(alpha=alpha, gamma=gamma)
    rewards: list[float] = []
    for ep in range(episodes):
        r = rng(seed, ep)
        eps = eps_end + (eps_start - eps_end) * (1 - ep / max(1, episodes - 1))
        s = env.start
        total = 0.0
        for _ in range(max_steps):
            a = agent.act(s, eps, r)
            s2, reward, done = env.step(s, ACTIONS[a])
            agent.update(s, a, reward, s2, done)
            total += reward
            s = s2
            if done:
                break
        rewards.append(total)
    return TrainResult(agent, rewards, episodes)


def evaluate(env: GridWorld, agent: QLearningAgent, *, max_steps: int = 200):
    """Run the greedy policy once; return (reached_goal, steps, total_reward, path)."""
    s = env.start
    path = [s]
    total = 0.0
    for _ in range(max_steps):
        s, reward, done = env.step(s, ACTIONS[agent.greedy_action(s)])
        total += reward
        path.append(s)
        if done:
            return s == env.goal, len(path) - 1, total, path
    return False, max_steps, total, path
