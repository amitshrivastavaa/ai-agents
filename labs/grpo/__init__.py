"""grpo — Group Relative Policy Optimization, from scratch.

The reinforcement-learning algorithm behind the reasoning-model wave
(DeepSeek-R1 and RLVR — RL from verifiable rewards), reduced to its essence:

* a **verifiable-reward task** (prompts with checkable correct answers),
* a **softmax policy** π(a|s),
* the **GRPO update** — sample a group of responses, turn rewards into
  advantages by subtracting the *group mean* and normalizing (no value network),
  and take a policy-gradient step.

The payoff, measured: GRPO's centered, normalized advantage is far lower-variance
than vanilla REINFORCE, so it solves the task ~2.5× faster — the property that
lets it scale to real reasoning models. The policy-gradient capstone of this
lab's RL thread (``bandits`` → ``qlearning`` → ``grpo``). Offline, deterministic.
"""
from .task import VerifiableTask
from .policy import SoftmaxPolicy, softmax
from .train import (train, group_advantages, mean_correct_prob, accuracy,
                    steps_to_threshold)

__all__ = [
    "VerifiableTask", "SoftmaxPolicy", "softmax",
    "train", "group_advantages", "mean_correct_prob", "accuracy",
    "steps_to_threshold",
]
