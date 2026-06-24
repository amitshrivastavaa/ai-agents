# grpo — Group Relative Policy Optimization, from scratch

> The reinforcement-learning algorithm behind the **reasoning-model wave**
> (DeepSeek-R1, and RLVR — RL from *verifiable rewards*), stripped to its
> essence. For each prompt you sample a **group** of responses from the current
> policy, score them with a checkable reward, and turn the scores into advantages
> by subtracting the **group mean** — no value network, no critic, the group is
> its own baseline. Then take a policy-gradient step. This MVP builds it and
> *measures* why the group baseline matters.

The policy-gradient capstone of this lab's RL thread:
[`bandits`](../bandits/) (one state) → [`qlearning`](../qlearning/) (values) →
**grpo** (policy gradient). Offline, stdlib-only, deterministic.

## Quick start

```sh
python -m labs.grpo.demo
python -m labs.grpo.cli train --contexts 6 --actions 6 --method grpo
python -m labs.grpo.cli compare          # GRPO vs REINFORCE
```

```
Learning curve — mean probability on the correct answer, over training:
   chance 0.17  ▂▃▄▅▆▇▇▇██████████████████████████  0.99 final

   accuracy: 100%   (solved all 6 prompts from a binary reward alone)

   GRPO (group baseline)    reaches 95% in  132 steps (avg)
   REINFORCE (no baseline)  reaches 95% in  325 steps (avg)
```

## The GRPO update

A softmax policy `π(a|s)` has one logit vector per prompt (`policy.py`). The
gradient of `log π(a|s)` w.r.t. the logits is just `onehot(a) − π(·|s)`. GRPO
(`train.py`) does, per prompt `s`:

1. **Sample a group** of `G` responses `a₁…a_G ~ π(·|s)`.
2. **Score** them with the verifiable reward `rᵢ ∈ {0,1}`.
3. **Group-relative advantage** — center and normalize *within the group*:

   ```
   Âᵢ = (rᵢ − mean(r)) / (std(r) + ε)
   ```

4. **Policy-gradient step**:

   ```
   θ_s ← θ_s + lr · (1/G) Σᵢ  Âᵢ · (onehot(aᵢ) − π(·|s))
   ```

Responses that beat their groupmates are reinforced; below-average ones are
pushed down. There is no learned baseline to maintain — that's GRPO's
simplification over actor-critic methods (PPO).

## Why the group baseline — the measured payoff

The comparison is apples-to-apples: the same samples and task, the only change is
the advantage. **REINFORCE** uses the raw reward (`Âᵢ = rᵢ`), so it only ever
pushes *rewarded* actions up and its gradient has high variance. **GRPO**'s
centered, normalized advantage is much lower-variance, so it converges **~2.5×
faster** to the same solution (averaged over seeds, at several task sizes). Lower
gradient variance is exactly what lets GRPO train stably at the scale of real
reasoning models.

> Scope: this is the policy-optimization core on a clean verifiable task. The KL
> penalty to a reference policy that production GRPO adds (to keep the policy near
> a pretrained model) is omitted here — there's no pretrained model to stay near,
> and the point is to *learn* the verified answer.

## Tests

```sh
python -m unittest labs.grpo.tests.test_grpo -v
```

9 tests: softmax/policy mechanics, the advantage is centered and unit-variance
(and zero when a group ties), the reward is verifiable, GRPO solves the task to
100% accuracy from binary reward, the learning curve rises far above chance, and
— the crux — GRPO converges in well under REINFORCE's steps. Deterministic.
