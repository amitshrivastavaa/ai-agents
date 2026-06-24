# gp — Gaussian Process regression (curve fitting that knows what it doesn't know)

> Most regressors hand you a number. A **Gaussian Process** hands you a number
> *and an honest error bar*. It puts a prior over functions, conditions on the
> data, and returns a posterior **mean and variance** in closed form — and that
> variance shrinks to the noise floor at the data and swells back to the prior
> away from it. The result, drawn as a confidence band, pinches at every
> observation and balloons in the gaps: calibrated uncertainty you can trust.

Closed-form, no training loop, no randomness. Complements the lab's Bayesian
[`kalman`](../kalman/) filter (uncertainty over time → uncertainty over space).

## Quick start

```sh
python -m labs.gp.demo
python -m labs.gp.cli fit --length 1.0
python -m labs.gp.cli uncertainty
```

```
  o=data  ━=mean  ·=true sin  ░=95% band      (note the gap x≈2.4–7)
  |             o━━━o░      ░░░░░░░░░░░░░░░░░░░░     ░━o━━o░░░░░░░░|
  |░         ░━━░   ░━━o░░░░░░░░░░░░░░░░░░░░░░░░░░░o━━░   ░━━━░░░░░|
  |░░      ░━o          ━━━░░░░░░░░░░░░░░░░░░░░░░━━░        ░░━━━░░|
  ...
  x=0.6  mean +0.56  ±0.06   (on a data point)
  x=4.7  mean −0.04  ±1.96   (middle of the gap → full prior uncertainty)
```

## How it works

With an RBF (squared-exponential) kernel `k(x,x') = σ²·exp(−(x−x')²/2ℓ²)`, the GP
posterior at a test point `x*` is exact (`gp.py`):

```
mean(x*) = k*ᵀ K⁻¹ y
var(x*)  = k(x*,x*) − k*ᵀ K⁻¹ k*          K = k(X,X) + σ_n²·I
```

The only linear algebra is a **Cholesky** factor `K = L·Lᵀ` (`linalg.py`), after
which `K⁻¹y` and `K⁻¹k*` are two triangular solves — never forming the inverse.
The **lengthscale `ℓ`** sets how far correlations reach: longer `ℓ` → smoother
fits that fill gaps more confidently; shorter `ℓ` → wigglier fits that distrust
the space between points.

## What it shows

- **Interpolation with error bars.** The mean passes through the (noisy) data; the
  ±2σ band is ~0 there and grows between and beyond points.
- **It knows what it doesn't know.** In the data gap and past the last point the
  mean reverts to the prior (0) and the variance returns to `σ²` — the model
  reports maximum uncertainty exactly where it has no evidence.
- **The lengthscale dial.** A longer lengthscale lowers the variance inside a gap
  (more correlation reaches across it) — a checkable property, not a vibe.
- **Exact & deterministic** — closed-form, same answer every run.

## Tests

```sh
python -m unittest labs.gp.tests.test_gp -v
```

10 tests: Cholesky reconstructs `K` (and rejects non-PD), the triangular solve is
correct, the GP interpolates the training data, variance is ~noise at the data and
~prior far away, the mean reverts to the prior far off, variance stays in
`[0, σ²]`, a longer lengthscale fills gaps more confidently, and it's deterministic.
