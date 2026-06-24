# qlearning — learn to navigate from reward alone

> No model of the world, no planning: the agent just acts, sees the reward, and
> nudges its value estimates. Over many episodes a Q-table fills in, a policy
> emerges, and on the classic **cliff-walking** world it finds the optimal route
> — watch the value function light up and the policy arrows snap into place.

Tabular **Q-learning** (model-free reinforcement learning). The RL counterpart
to the lab's `world_model` (which *plans*) and `neuroevolution` (which
*evolves*). Fully offline, deterministic, and checked against value iteration
(the dynamic-programming optimum).

## Quick start

```sh
python -m labs.qlearning.demo
python -m labs.qlearning.cli train --map cliff --watch
python -m labs.qlearning.cli train --map maze --episodes 600 --watch
python -m labs.qlearning.cli list
```

```
'cliff' — learning from reward, no model of the world
  reward/episode: ▁▁▁▂▂▂▂▂▂▃▃▃▄▅▅▅▆▆▇▇▇  -116 → -9
  greedy policy : reaches goal in 9 steps          (optimal)
  V(start)      : learned -0.1 vs optimal -0.1      (matches value iteration)

→→↓→→↓↓↓        ← the learned policy: up and over the cliff, then down to G
↓→→→→→↓↓
→→→→→→→↓
SXXXXXXG        ← S start · X cliff · G goal
```

## How it works

The agent keeps a table `Q(s, a)` and, after every move, applies the
**temporal-difference** update

```
Q(s,a) ← Q(s,a) + α · ( r + γ·maxₐ' Q(s',a') − Q(s,a) )
```

It explores with an ε-greedy policy (ε annealed from 1.0 → 0.05 across training),
so early episodes wander into the cliff for −100, and later ones exploit what
they've learned. No transition model is ever built — the world is a black box
that returns `(next state, reward, done)`.

Maps (legend `S` start · `G` goal · `#` wall · `X` pit · `.` floor): `cliff`
(the Sutton & Barto cliff-walk), `maze`, and `rooms`. Every step costs −1, the
goal pays +10, a pit pays −100.

## It learns the optimum

Q-learning's `V(start) = max_a Q(start, a)` converges to the value computed by
**value iteration** (`dp.py`, the DP optimum), and its greedy policy reaches the
goal in the optimal number of steps. The `--watch` view shows the policy as
arrows and the value function as a brightness heatmap that flows toward the goal.

## Tests

```sh
python -m unittest labs.qlearning.tests.test_qlearning -v
```
