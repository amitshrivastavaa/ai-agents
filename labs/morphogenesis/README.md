# morphogenesis — self-organizing, self-healing patterns

> Two virtual chemicals diffuse and react on a grid. From a tiny seed, the whole
> field organizes itself into spots, stripes, mazes, or dividing "cells" — and
> if you cut a hole in a formed pattern, **it grows back**. No controller, no
> training: structure and repair emerge from local rules.

Turing's morphogenesis (the Gray-Scott reaction-diffusion system) — the same
lineage that leads to **Growing Neural Cellular Automata**. Fully offline, fast
in pure Python, deterministic, rendered as shaded ASCII.

## Quick start

```sh
python -m labs.morphogenesis.demo                       # grow, damage, heal
python -m labs.morphogenesis.cli run --pattern mitosis --frames 3
python -m labs.morphogenesis.cli run --pattern coral --steps 4000
python -m labs.morphogenesis.cli run --pattern maze --heal
python -m labs.morphogenesis.cli list
```

## The model

Fields `U` and `V` on a toroidal grid evolve by

```
U' = U + (Du·∇²U − U·V² + F·(1−U)) · dt
V' = V + (Dv·∇²V + U·V² − (F+k)·V) · dt
```

`U` is fed in at rate `F`, `V` removed at rate `F+k`, and `U + 2V → 3V` is the
reaction. The Laplacian `∇²` is a 3×3 stencil. Tiny changes to `(F, k)` produce
wildly different morphologies — the same equations, different worlds:

| pattern | (F, k) | looks like |
| --- | --- | --- |
| `mitosis` | 0.0367, 0.0649 | dividing cells / bacteria splitting |
| `coral` | 0.0545, 0.0620 | branching coral growth |
| `maze` | 0.0290, 0.0570 | a winding maze of stripes |
| `spots` | 0.0250, 0.0600 | isolated spots |
| `holes` | 0.0390, 0.0580 | negative spots |

## Self-healing

```
… formed pattern …        … wipe a hole …          … 1600 steps later …
·%#+#%·  ·%##·             ·%#+#%·                   ·%#+#%·  ·%##·
·%**#%·  ·%##·             ·%             ·          ·%**#%·  ·%%%·
.**+*#·   ···             ·*             .          .**+*#·   ·:·
```

Wipe a rectangle back to the resting state and keep iterating: neighboring
pattern invades the gap and the morphology **regrows** — the dynamics are
attractors, so damage is just a perturbation they recover from. That self-repair
is exactly the headline property of Growing Neural CA, here for free from the
chemistry. (`run --heal` or the demo show it.)

## Tests

```sh
python -m unittest labs.morphogenesis.tests.test_morphogenesis -v
```
