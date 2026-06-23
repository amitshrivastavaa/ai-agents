# prompt_evolver — evolve your prompts with a genetic algorithm

> Automated prompt engineering as evolution. Treat a prompt as a genome of
> instruction directives, breed a population across generations, and let
> accuracy on a labeled task select the winners. Out comes a prompt that beats
> your hand-written seed — and you can read exactly why.

Inspired by DSPy / evolutionary prompt search. Runs **fully offline** with the
standard library; set `ANTHROPIC_API_KEY` to score prompts against a real model
instead of the deterministic executors.

## Quick start

```sh
python -m labs.prompt_evolver.demo                       # evolve both tasks
python -m labs.prompt_evolver.cli run --task sentiment   # one task, full report
python -m labs.prompt_evolver.cli run --task slugify --json
python -m labs.prompt_evolver.cli list
```

Example run:

```
baseline prompt : ['use_formal_tone', 'be_concise']
baseline fitness: 0.451
evolved  prompt : ['sarcasm', 'handle_negation', 'intensifiers']
evolved  fitness: 0.970   (+0.519 improvement)
best-per-gen     : ▁▁▁▄▄████████████████████  0.95 → 0.97
```

## The trick: prompts that actually *do* something offline

Without a model, how can a prompt have a measurable fitness? Each **directive**
isn't just text — it toggles real behavior in a tiny deterministic **executor**
for the task. So a prompt's accuracy is a genuine function of its content, which
is exactly the gradient a genetic algorithm needs.

Two tasks ship:

- **`sentiment`** — classify text positive/negative. Directives like
  `handle_negation`, `intensifiers`, and `sarcasm` switch on real logic in the
  classifier; `invert_polarity` is *harmful* and `use_formal_tone` is a no-op.
  The GA learns to include the first three and drop the rest → **0.45 → 0.97**.
- **`slugify`** — turn text into a URL slug. Here **order matters**: accents must
  be folded *before* punctuation is stripped. The GA discovers a working
  pipeline ordering, not just a set → **0.77 → 0.96**, with exact-match outputs.

## How the GA works

- **Genome** = an ordered, duplicate-free list of directive ids = a prompt.
- **Fitness** = task accuracy − a small length penalty (so concise prompts win
  ties — automated prompt *minimization* for free).
- **Selection** = tournament; **crossover** = one-point on the ordered genomes
  (then de-dupe); **mutation** = add / remove / swap a directive; **elitism**
  carries the best forward. All seeded via `_kernel`'s RNG → fully reproducible.

The winning genome is rendered back into a real prompt you could paste into a
model (see the "evolved prompt" block in the report).

## Add your own task

Implement `directives`, `baseline()`, `evaluate(genome)`, and `render(genome)`
(see `tasks.py`). Register it in `TASKS` and the CLI/optimizer pick it up.

## Tests

```sh
python -m unittest labs.prompt_evolver.tests.test_evolve -v
```
