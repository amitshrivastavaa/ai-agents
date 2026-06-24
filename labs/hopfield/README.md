# hopfield — associative memory that completes corrupted patterns

> Store a few patterns; hand the network a noisy or half-erased one and it
> settles back into the clean original. Watch a smudged glyph snap into focus.

A miniature, fully-offline take on **associative memory** — the Hopfield network
(Nobel Prize in Physics, 2024) and its **modern dense** descendant (the
"Hopfield ≈ attention" connection). Deterministic, rendered in ASCII.

## Quick start

```sh
python -m labs.hopfield.demo
python -m labs.hopfield.cli recall --glyph X --noise 0.3
python -m labs.hopfield.cli recall --glyph H --occlude 0.5 --net modern
python -m labs.hopfield.cli sweep
python -m labs.hopfield.cli list
```

```
Hand it a 30%-corrupted X and it settles back to the clean attractor:

target X   30% noise   recalled
#·····#   ······#    #·····#
·#···#·   ·#·····    ·#···#·
··#·#··   ··#····    ··#·#··
···#···   ·#·····    ···#···
··#·#··   #####··    ··#·#··
·#···#·   ·#··##·    ·#···#·
#·····#   ##·····    #·····#

  → recalled 'X', overlap 100%, energy -7 → -27 (monotonic descent)
```

## How it works

A pattern is a vector of ±1 over the 49 neurons of a 7×7 grid. Two memories:

- **classic** — Hebbian weights `W = Σ pₖpₖᵀ` (zero diagonal). Recall does
  asynchronous sign-updates `sᵢ ← sign(Σⱼ Wᵢⱼ sⱼ)`, which is **gradient descent on
  an energy** `E = -½ sᵀWs` that only ever decreases — so a corrupted cue rolls
  downhill into the nearest stored attractor.
- **modern** — dense associative memory: `out = Σ softmax(β·⟨pₖ, cue⟩) pₖ`, then
  binarized. That softmax is exactly attention over the stored patterns, giving
  far higher capacity and sharper recall.

## The result: modern is more robust

```
 noise   classic    modern
   20%      0.98      1.00
   30%      0.86      0.93
   40%      0.70      0.81
   50%      0.62      0.71
```

(avg overlap-to-target across all glyphs). Both recover clean and lightly-noised
patterns perfectly; as corruption rises, the modern dense memory degrades far
more gracefully — the capacity advantage that links Hopfield networks to the
attention in today's transformers.

## Try it

`recall --occlude 0.5` erases the bottom half of a glyph and recovers it from the
top half alone; `--net modern` switches memories; `sweep` reproduces the table.
Add your own 7×7 glyph to `patterns.py` and it joins the stored set.

## Tests

```sh
python -m unittest labs.hopfield.tests.test_hopfield -v
```
