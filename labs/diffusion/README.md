# diffusion — turn noise into a shape, the way diffusion models do

> Start from pure noise and walk it, step by step, into samples that match a
> target distribution — the inference process at the heart of every diffusion
> model (Stable Diffusion & friends), here on 2-D shapes you can watch form in
> ASCII. Noise becomes a ring, a spiral, clusters, a grid.

The offline trick: a diffusion model's only learned part is the **score**
`∇log p(x)`. For a target that's a mixture of Gaussian modes the score is
*analytic*, so we run the **real sampler — annealed Langevin dynamics** — with
no training at all. Fully offline, deterministic.

## Quick start

```sh
python -m labs.diffusion.demo
python -m labs.diffusion.cli sample --target ring
python -m labs.diffusion.cli sample --target spiral --n 400
python -m labs.diffusion.cli list
```

```
target 'ring': 300 samples, after annealed Langevin from noise

                -:       -.
             . -+:-     :-+-:
       : .:-     ..      .::   .-..-
       .-::=:                 . ---=
       .                        .   .
     .+--.                        :---:
    -= -- .                       :+=..
         -+::                . .-+-:. :
               =*=@-.   -*++-
  mean distance to nearest mode: 9.2 → 0.83
```

## How it works

A diffusion model generates by reversing a noising process, and the only thing
it needs is the **score** of the (noise-smoothed) data density. For an
equal-weight Gaussian mixture with means `μ_k` and variance `v`,

```
∇log p(x) = Σ_k softmax_k(−‖x−μ_k‖²/2v) · (μ_k − x) / v
```

— a responsibility-weighted pull toward the modes. Smoothing the data with noise
`σ` just inflates the variance to `v = σ₀² + σ²`, which is exactly what a trained
denoiser approximates at each noise level.

**Annealed Langevin dynamics** then samples: start from large-noise samples and,
for a decreasing schedule of noise levels `σ`, take Langevin steps

```
x ← x + (α/2)·score_σ(x) + √α · z,     α ∝ σ²
```

Large noise first lets samples find the right basins; shrinking noise sharpens
them onto the modes. The samples go from ~9 units away from the nearest mode (pure
noise) to ~0.8 (≈ the per-mode spread) — they've become the shape.

This *is* a diffusion model's sampling loop; a real one only differs by learning
`score_σ` with a network instead of writing it down.

## Tests

```sh
python -m unittest labs.diffusion.tests.test_diffusion -v
```
