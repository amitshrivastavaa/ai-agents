# flow — flow matching / rectified flow, from scratch

> The generative method that **replaced diffusion** at the frontier (Stable
> Diffusion 3, Flux). Instead of slowly reversing a noisy diffusion process, you
> learn a **velocity field** and integrate a *deterministic* ODE that flows a
> Gaussian straight onto the data. This MVP builds it with the **analytic**
> marginal velocity for an empirical target — no training, exactly as the lab's
> [`diffusion`](../diffusion/) MVP uses the analytic score — and shows the payoff:
> it lands on the target in ~16 deterministic steps.

Fully offline, deterministic; renders noise → shape in ASCII.

## Quick start

```sh
python -m labs.flow.demo
python -m labs.flow.cli sample --target ring --steps 16
python -m labs.flow.cli steps --target spiral      # error vs #steps
python -m labs.flow.cli list
```

```
Start: Gaussian noise            After 16 ODE steps:
 |        ·  ·         |          |           • • •           |
 |     ·········       |          |       • •       • •       |
 |      ········       |          |     •               •     |
 |     ············    |          |    •                 •    |
 |      ··········     |          |     •               •     |
 |          ··  ·      |          |       • •       • •       |
                                   on-ring RMSE = 0.000, 100% of modes covered
```

## How it works

Rectified flow interpolates each data point `x₁` with noise `x₀ ~ N(0,I)` along a
straight line `x_t = (1−t)·x₀ + t·x₁`, whose velocity is the constant `x₁ − x₀`.
The field that generates the *marginal* path is the posterior expectation
`v(x,t) = E[x₁ − x₀ | x_t = x]`. For a target supported on a finite data set this
is **analytic** (`field.py`):

```
wₖ(x,t) ∝ exp(−‖x − t·yₖ‖² / 2(1−t)²)     # posterior over which data point
ŷ(x,t)  = Σₖ wₖ·yₖ                         # the "denoiser" — posterior mean
v(x,t)  = (ŷ(x,t) − x) / (1 − t)
```

Sampling (`sample.py`) is just integrating `dx/dt = v(x,t)` from `t=0` to `t=1`
with Euler (or midpoint/RK2) — **no noise injected along the way**, unlike
diffusion's Langevin dynamics. At `t=0` no mode is chosen yet, so the field
points at the data centroid; as `t→1` the posterior sharpens and each trajectory
commits to a data point.

## What it shows

- **It lands on the data.** Across ring / clusters / grid / moons / spiral, the
  nearest-data RMSE falls to ~0 and **all modes are covered** (no collapse).
- **Few steps suffice.** Error vs. step count drops fast and is essentially zero
  by **16 steps** — the selling point of a straight-path ODE. A noisy Langevin
  diffusion sampler (the `diffusion` MVP) needs far more steps for similar targets.
- **Trajectories are nearly straight** — mean path-length / displacement ≈ 1.12
  (1.0 = a perfect line), the "rectified" in rectified flow.
- **Deterministic** — same seed, same samples, every run.

## Tests

```sh
python -m unittest labs.flow.tests.test_flow -v
```

10 tests: the base is N(0,I), the posterior weights form a distribution, the
denoiser → nearest point as `t→1` and → centroid at `t=0`, generation lands on
every target with near-total mode coverage, more steps reduce error, ring samples
sit at the exact target radius, trajectories are near-straight, midpoint also
converges — all deterministic.
