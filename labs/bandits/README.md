# bandits — the multi-armed bandit (exploration vs exploitation)

> The cleanest model of the oldest dilemma in decision-making: **explore** to
> learn which option is best, or **exploit** what you already believe? K arms,
> each a coin with a hidden win-rate; every pull you pick one and see only its
> reward. This MVP pits five classic policies against each other and scores them
> by **regret** — the reward lost versus an oracle that always plays the best arm.

The stateless root of reinforcement learning (one state, K actions) — the
companion to this lab's [`qlearning`](../qlearning/). Offline, stdlib-only,
deterministic; results averaged over many seeds for smooth curves.

## Quick start

```sh
python -m labs.bandits.demo
python -m labs.bandits.cli compare --horizon 2000 --runs 60
python -m labs.bandits.cli pulls --policy Thompson
```

```
   policy         regret over time                  final  optimal-pulls
   random         ▁▁▁▂▂▂▂▃▃▃▃▄▄▄▄▅▅▅▅▆▆▆▆▇▇▇▇███    580.7      19.9%
   greedy         ▁▁▁▂▂▂▂▂▃▃▃▃▃▄▄▄▄▄▅▅▅▅▅▅▆▆▆▆▆▇    470.2      25.0%
   ε-greedy(.1)   ▁▁▁▁▁▁▁▁▁▁▁▁▁▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂     75.9      88.4%
   UCB1           ▁▁▁▁▁▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂    107.7      81.1%
   Thompson       ▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁     25.1      95.4%
```

## The five policies (`policies.py`)

| Policy | Rule | Regret |
| --- | --- | --- |
| **Random** | pull uniformly at random | linear (worst) |
| **Greedy** | always pull the best-looking arm | linear — fixates on the first arm that pays |
| **ε-greedy** | greedy, but explore at random an ε fraction of the time | linear, shallow slope (the fixed-ε tax) |
| **UCB1** | pull `argmax(mean + √(2·ln t / n))` — optimism under uncertainty | **logarithmic** (Auer et al. 2002) |
| **Thompson** | keep a Beta posterior per arm, sample each, pull the winner | **logarithmic**, best constant |

## What the curves show

Regret here is *expected* regret — the summed true gaps `best_prob − prob[chosen]`
— so the curve measures decision quality, not reward luck, and comes out smooth.

- **random** and **greedy** climb at a constant slope: their regret is **linear**,
  so the per-pull penalty never goes away. Greedy is the cautionary tale —
  exploiting too early it can lock onto a suboptimal arm and never find out.
- **ε-greedy** explores a fixed 10% forever: it learns the best arm fast, but the
  curve never fully flattens because it keeps throwing away one pull in ten.
- **UCB1** and **Thompson** explore *less as they grow more certain*, so their
  regret is **sublinear** — the curve bends over and goes nearly flat. Thompson
  here sends ~95% of pulls to the best arm and all but stops losing.

`pulls` shows where a single run spends its budget — Thompson puts the
overwhelming majority of pulls on the true best arm once it's confident.

## Tests

```sh
python -m unittest labs.bandits.tests.test_bandits -v
```

12 tests: bandit mechanics (binary rewards, gaps, empirical-mean convergence),
each policy's update rule (UCB1 tries every arm once; Thompson's posterior), and
the headline results — the dumb policies are linear, Thompson is sublinear and
best, the learners dominate on optimal-arm rate, all fully deterministic.
