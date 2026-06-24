# speculative — lossless LLM speedup by drafting and verifying

> The trick that makes today's LLM serving fast. A small, cheap **draft** model
> guesses the next few tokens; the big, accurate **target** model checks them all
> in a *single* pass — keeping the longest prefix it agrees with and correcting
> the first miss. The output is **identical** to running the target alone, but it
> costs far fewer expensive target calls, because several tokens get confirmed per
> call.

Built from scratch on back-off n-gram language models (a fast bigram **draft**,
an accurate 4-gram **target**). Fully offline, deterministic. It demonstrates the
two properties that matter: the speculative output exactly matches pure target
decoding, and it needs ~2× fewer target calls.

## Quick start

```sh
python -m labs.speculative.demo
python -m labs.speculative.cli run --prompt "A good agent" --steps 40 --k 4
python -m labs.speculative.cli compare
```

```
Pure target decoding — one expensive target call per token:
  a good agent plans before it acts , remembers what worked , and avoids ...
  → 40 target calls for 40 tokens.

Speculative decoding — a bigram draft guesses, the 4-gram target verifies:
  a good agent plans before it acts , remembers what worked , and avoids ...
  → 18 target calls for 40 tokens (2.22× fewer).
  → output identical to pure target decoding: True
```

## How it works

One round of the loop (`speculative.py`):

1. **Draft** proposes `k` tokens greedily — `k` cheap calls.
2. **Target** verifies positions `0..k` in *one* (conceptually parallel) call: at
   each position it computes its own greedy next-token given the *accepted*
   prefix so far.
3. **Accept** the draft tokens that match the target's choice, stopping at the
   first disagreement; **correct** that position with the target's token (or, if
   all `k` matched, append the target's bonus token).
4. Repeat from the new, longer prefix.

Because every emitted token is either one the target *itself* would have greedily
chosen, or the target's own correction, the result is provably the same sequence
pure greedy target decoding produces — only computed in fewer target calls. This
is exactly the acceptance rule behind production speculative decoding (Leviathan
et al., 2023; Chen et al., 2023), specialized to greedy/argmax decoding.

The n-gram models (`ngram.py`) use **back-off**: try the longest context, fall
back to shorter ones until a match is found, ties broken alphabetically for full
determinism — no training loop, no randomness.

## Why the speedup is real

Each target call confirms a *block*: `n_accepted + 1` tokens for one call. The
more often the cheap draft agrees with the target, the bigger the blocks and the
fewer the calls. Here the bigram draft and 4-gram target agree often enough to
average ~1.2 accepted draft tokens per round, turning 40 target calls into 18.

`compare` sweeps `k` and prints target-calls / speedup / lossless for each — the
text never changes, only the call count does:

```sh
python -m labs.speculative.cli compare
```

## Tests

```sh
python -m unittest labs.speculative.tests.test_speculative -v
```

9 tests: n-gram tokenization / determinism / back-off, and — the heart of it —
that speculative output equals pure target output for every `k ∈ {1,2,3,4,6,8}`
(lossless), with fewer target calls than tokens (speedup > 1).
