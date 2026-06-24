# ssm — a selective state-space model (Mamba), from scratch

> State-space models (S4, **Mamba**) are the leading **linear-time** alternative
> to the Transformer: they read a sequence in `O(n)` instead of attention's
> `O(n²)`. This MVP builds the scalar SSM core and demonstrates the two facts
> that make the family work — the **duality** (a recurrence that is secretly a
> convolution) and **selectivity** (Mamba's one idea: let the dynamics depend on
> the input, so the model can *choose what to remember*).

Pure stdlib, single channel, fully deterministic. The companion to this lab's
[`attention`](../attention/) MVP — the two competing ways to model a sequence.

## Quick start

```sh
python -m labs.ssm.demo
python -m labs.ssm.cli duality            # recurrence == convolution
python -m labs.ssm.cli hold --seed mamba  # selective copy: Mamba vs best LTI
python -m labs.ssm.cli kernel --a 0.9 --b 0.1
```

```
2) Selective copy — capture the value at each ↑write, hold it, ignore the rest:

   writes : t=0:+0.75  t=8:-0.18  t=16:-0.88
   gate   ↑·······↑·······↑·······
   target ▇▇▇▇▇▇▇▇▄▄▄▄▄▄▄▄▁▁▁▁▁▁▁▁   (the sample-and-hold we want)
   MAMBA  ▇▇▇▇▇▇▇▇▄▄▄▄▄▄▄▄▁▁▁▁▁▁▁▁   selective SSM,   MSE = 2.4e-11
   LTI    ██▇▇▇▆▆▆▅▅▅▅▅▅▅▅▁▁▁▂▂▂▃▃   best fixed (a,b),  MSE = 0.058
```

## 1. The SSM and its duality

A single-channel state-space model is the linear recurrence (`ssm.py`):

```
h_t = a·h_{t-1} + b·x_t          y_t = c·h_t + d·x_t        (h_{-1} = 0)
```

When the parameters are constant — a **linear time-invariant** (LTI) model —
unrolling the recurrence shows it is *exactly* a causal convolution with the
kernel `K[k] = c·b·aᵏ` (the impulse response):

```
y_t = d·x_t + Σ_k  (c·b·aᵏ)·x_{t-k}
```

So one model has two faces: a **recurrence** that runs in `O(n)` at inference,
and a **convolution** that trains in parallel over the whole sequence. `ssm_scan`
and `ssm_conv` agree to machine precision (~1e-16) — that equivalence is what S4
exploits. With `a < 1` the kernel decays: a stable, finite-memory filter (an EMA
is just `a=0.9, b=0.1`).

## 2. Why selectivity matters (the Mamba idea)

The LTI convolution view has a catch: the *same* kernel is applied everywhere, so
the model can't make a **content-dependent** decision like "remember *this* token,
ignore the next ten." That is the **selective-copy** task, and it's exactly where
fixed SSMs fail and attention has always won.

Mamba fixes it by making the discretization timestep `Δ_t` a **function of the
input**, via zero-order hold (`selective.py`):

```
ā_t = exp(Δ_t·A)            b̄_t = (ā_t − 1)/A · B           (A < 0)
```

- **Δ_t large** → `ā_t→0, b̄_t→B`: *overwrite* the state with the new input.
- **Δ_t = 0**   → `ā_t=1,  b̄_t=0`: *hold* the state unchanged.

Driving `Δ_t` from a write-gate gives a perfect **sample-and-hold**: capture the
value on a write, hold it across the gap. The selective SSM matches the target to
`~1e-11`.

## The honest baseline

We give the time-invariant model every advantage — the gate-masked input *and* a
grid search over **both** of its constant parameters `(a, b)` — and it still can't
(`best_lti`): holding wants `a≈1`, capturing wants `a≈0`, and one constant `a`
can't be both. Its best mean-squared error sits ~9 orders of magnitude above the
selective model's. Selectivity isn't a tuning detail; it's a different capability.

## Tests

```sh
python -m unittest labs.ssm.tests.test_ssm -v
```

10 tests: the duality (`scan == conv`) across parameter sets, impulse response =
kernel, EMA smoothing, the discretization regimes (overwrite vs hold), near-exact
sample-and-hold, and the crux — selective beats the *best possible* LTI by >50×
on every seed.
