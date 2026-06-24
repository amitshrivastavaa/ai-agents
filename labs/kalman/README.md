# kalman — the Kalman filter (optimal tracking through noise)

> The estimation algorithm that flies planes, lands rockets, and fuses every
> phone's GPS. Given a linear system driven by noise and observed through noise,
> the Kalman filter keeps a Gaussian belief over the hidden state and updates it
> optimally with each measurement — it is the **minimum-variance estimator** for
> the model, no estimator does better. This MVP tracks a noisy 2-D object and
> shows the payoff: ~40–50% less position error than the raw sensor, beating a
> moving-average smoother, while recovering the **velocity it never measured**.

Fills the lab's state-estimation gap; pure stdlib (its own little matrix algebra),
fully deterministic, with ASCII trajectory plots.

## Quick start

```sh
python -m labs.kalman.demo
python -m labs.kalman.cli track --kind sine --noise 3
python -m labs.kalman.cli gain --kind line
```

```
  Kalman estimate ('o' = filter, '·' = true path):
 |  o   o o··oo                            ··oooo   o       |
 |  oooo·o· o·o·                         ··· o··· oo o      |
 ...
  position RMSE — measurements 4.12 | moving-avg 2.94 | Kalman 2.42  (−41%)
  recovered velocity: vx≈1.0, vy≈0.5 (never directly measured)
```

## How it works

The model (`models.py`) is a constant-velocity tracker: state `x = [px, py, vx, vy]`,
we measure position only (`H` picks out `px, py`).

```
xₖ = F·xₖ₋₁ + process noise (cov Q)          # constant-velocity dynamics
zₖ = H·xₖ   + measurement noise (cov R)       # noisy position reading
```

The filter (`filter.py`) alternates two steps:

- **predict** — `x ← F·x`, `P ← F·P·Fᵀ + Q`. Roll the belief forward; uncertainty
  grows by the process noise.
- **update** — fold in measurement `z`. The **Kalman gain**
  `K = P·Hᵀ·(H·P·Hᵀ + R)⁻¹` weights prediction vs. measurement by their relative
  certainty: `x ← x + K·(z − H·x)`, `P ← (I − K·H)·P`. Uncertainty shrinks.

All the matrix machinery — multiply, transpose, and a Gauss-Jordan **inverse** —
is a ~40-line `linalg.py`; the only inversion is the 2×2 innovation covariance.

## What it shows

- **It denoises optimally.** Filtered position RMSE is ~40–50% below the raw
  sensor's, across a straight line, a sine weave, and a turning arc — and it beats
  a moving-average smoother every time.
- **It estimates the unobserved.** Velocity is never measured, yet the filter
  recovers it (true `vx=1.0, vy=0.5` → estimated ≈ `1.0, 0.5`) from how the
  position evidence accumulates.
- **The gain reaches steady state.** For a fixed model the Kalman gain converges
  to a constant — the algebraic-Riccati fixed point of the optimal filter.
- **Deterministic** — seeded noise, identical every run.

## Tests

```sh
python -m unittest labs.kalman.tests.test_kalman -v
```

9 tests: the matrix inverse (and singular-matrix guard), an update strictly
shrinks the covariance, the gain stays in (0,1) and converges, filtered RMSE beats
both the sensor and the moving average on every trajectory, velocity is recovered
to tolerance, and everything is deterministic.
