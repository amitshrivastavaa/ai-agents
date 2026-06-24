# hmm — Hidden Markov Models (Viterbi + forward-backward), from scratch

> A Markov chain over states you **can't** see, each emitting an observation you
> **can**. Given the observations, three exact dynamic-programming algorithms
> answer three different questions — and this MVP builds all three and *proves*
> them correct against brute-force enumeration of every possible path.

The classic of probabilistic sequence modeling (speech, bioinformatics, POS
tagging), shown on the canonical **dishonest casino**. Offline, deterministic,
all in log space so long sequences don't underflow.

## Quick start

```sh
python -m labs.hmm.demo
python -m labs.hmm.cli casino --n 200
python -m labs.hmm.cli decode --rolls 6661345266666654
```

```
  rolls   4335...3566661544136...   (you see only these)
  true    ················███████████████·········   █ = loaded die
  viterbi ················███████████████·········   recovered hidden path
  P(load) ▁▁▁▁▁▁▁▂▄▆▇█████▇▇▆▅▃▂▁▁   forward-backward posterior
  decode accuracy: 96%
```

## The three algorithms (`model.py`)

| Question | Algorithm | Returns |
| --- | --- | --- |
| *What hidden path is most likely?* | **Viterbi** (max-product DP) | the single best state sequence |
| *How likely are these observations?* | **forward** (sum-product DP) | `log P(observations)` |
| *What's the state distribution at each step?* | **forward-backward** | per-position posterior `P(state \| all obs)` |

Viterbi keeps, for each step and state, the best score reachable and a
back-pointer, then traces the winner back. Forward sums instead of maxes.
Forward-backward multiplies a forward pass by a backward pass to get a smoothed
posterior. Everything is in **log space** with a `logsumexp` so a 600-roll
sequence (probability ~`10⁻²⁰⁰`) never underflows.

## The dishonest casino

A dealer secretly switches between a fair die and a loaded one (`P(6)=0.5`),
staying with each for a while (95% / 90% self-transition). You see only the rolls;
the hidden state is which die. Viterbi recovers the loaded stretches at ~80–95%
accuracy, and the forward-backward posterior shows *where it's sure* — tall over a
clear loaded run, low in the brief excursions too short to commit to.

## Proven correct, not just plausible

`brute.py` enumerates **every** hidden path for short sequences. The tests assert:

- Viterbi's path == the exhaustively-searched best path (and same log-prob),
- the forward algorithm's `log P(obs)` == the log of the summed path probabilities.

So the fast `O(N·S²)` DP gives provably the same answer as the `O(Sᴺ)` brute force.

## Tests

```sh
python -m unittest labs.hmm.tests.test_hmm -v
```

8 tests: Viterbi == brute force, forward == brute force, posteriors sum to 1,
`logsumexp` correctness, obvious sequences (all 6s → all loaded), casino decode
accuracy > 70%, no underflow on 600 rolls, determinism.
