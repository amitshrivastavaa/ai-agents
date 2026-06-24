# neuroevolution — balance a pole by evolving a brain, no gradients

> The classic CartPole: keep a hinged pole upright by pushing the cart left or
> right. Instead of training the controller with backprop, we **evolve** it — a
> population of tiny neural nets, the ones that balance longest reproduce (with
> mutation), and within a few generations one that holds the pole for the whole
> episode emerges.

Gradient-free reinforcement learning (an evolution strategy) on the iconic
control benchmark — the counterpart to [`micrograd`](../micrograd/)'s
gradient-based learning. Fully offline, deterministic, with an ASCII view of the
balancing cart.

## Quick start

```sh
python -m labs.neuroevolution.demo                       # random fails, evolved balances
python -m labs.neuroevolution.cli evolve --watch
python -m labs.neuroevolution.cli evolve --pop 30 --gens 25
python -m labs.neuroevolution.cli random --watch         # watch an un-evolved net fail
```

```
best fitness per generation: ▁▁▁████████████████  129 → 500 / 500
generalization (5 unseen starts): 500 steps avg

         O
         |
         |
         |
        ###
=========================================   pole +0.5°, still up at step 120
```

## How it works

- **Environment** (`cartpole.py`) — the standard CartPole-v1 physics: state is
  `(x, ẋ, θ, θ̇)`; each step pushes the cart with ±10 N; the episode ends when the
  pole passes 12° or the cart leaves the track, and lasts at most 500 steps. More
  steps balanced = higher reward.
- **Controller** (`policy.py`) — a tiny `[4 → 6 → 1]` MLP. It only does a forward
  pass (evolution needs no gradients), so it's plain fast float math; the whole
  network is one flat parameter vector.
- **Evolution** (`evolve.py`) — each generation, score every controller by how
  long it balances (averaged over a few shared-seed episodes), keep the elite,
  and refill the population with mutated copies of the best parents (Gaussian
  noise, annealed). No backprop anywhere.

## The result

A **random** controller drops the pole in ~10 steps. After ~4 generations,
evolution finds one that balances the full **500** — and it **generalizes**,
holding the pole on starting states it never trained on. The whole run takes
under a second.

Two paths to a working network, side by side in the lab: `micrograd` descends a
gradient; `neuroevolution` just keeps what survives. Both arrive.

## Tests

```sh
python -m unittest labs.neuroevolution.tests.test_neuroevolution -v
```
