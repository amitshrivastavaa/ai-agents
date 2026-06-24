# conformal — distribution-free prediction intervals (with a proof)

> A Gaussian Process gives you error bars *if you believe its model*. **Conformal
> prediction** gives you error bars with a **guarantee that holds for any model
> and any data distribution**. Wrap any regressor: fit it, measure its errors on a
> held-out **calibration** set, and take the `(1−α)` quantile of those errors as
> the interval half-width. Then `ŷ(x) ± q` contains the true value with
> probability **at least `1 − α`** — assuming only that the data is exchangeable.
> No Gaussian assumption, no asymptotics. And the guarantee is exactly testable.

One of the hottest ideas in trustworthy ML; the assumption-light cousin of the
lab's [`gp`](../gp/). Offline, deterministic.

## Quick start

```sh
python -m labs.conformal.demo
python -m labs.conformal.cli coverage
python -m labs.conformal.cli band --adaptive
```

```
The guarantee, not a fluke — coverage over 40 fresh random splits:
   α=0.05 target 0.95   measured 0.949
   α=0.1  target 0.90   measured 0.899
   α=0.2  target 0.80   measured 0.796
```

## How it works (`conformal.py`)

**Split conformal** in three steps:

1. Fit any model on a **training** split (here a k-NN regressor — the point is the
   calibration, not the model).
2. On a held-out **calibration** split, compute the nonconformity score of each
   point — how wrong the model was, `|y − ŷ|`.
3. Take `q = ⌈(n+1)(1−α)⌉ / n` empirical quantile of those scores.

Then the interval `[ŷ(x) − q, ŷ(x) + q]` has marginal coverage ≥ `1 − α`. The
proof is a one-line exchangeability argument: the test point's score is equally
likely to land in any rank among the calibration scores, so it exceeds the `(1−α)`
quantile at most an `α` fraction of the time.

## What it shows

- **Coverage on demand.** Across 40 random train/cal/test splits, the empirical
  coverage lands on `1 − α` for every `α` — 0.95, 0.90, 0.80 — *regardless of the
  heteroscedastic, non-Gaussian noise*. That's the distribution-free guarantee in
  action.
- **Tighter `α` ⇒ wider intervals**, monotonically — you pay for confidence in
  width.
- **Adaptive (normalized) conformal** divides the score by a local difficulty
  estimate, so intervals **narrow where the data is clean and widen where it's
  noisy** — same coverage, more informative bars.

## Tests

```sh
python -m unittest labs.conformal.tests.test_conformal -v
```

7 tests: the conformal quantile is the right order statistic (and `∞` with too
few points), marginal coverage matches `1 − α` across splits, smaller `α` gives
wider intervals, adaptive intervals widen with the noise while keeping coverage,
and it's deterministic.
