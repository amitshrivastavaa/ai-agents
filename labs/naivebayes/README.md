# naivebayes — a Naive Bayes text classifier, from scratch

> The workhorse behind spam filters, sentiment, and topic labeling — and it's
> almost embarrassingly simple. Score each class by its log-prior plus the
> log-likelihood of every word in the document, and pick the winner. "Naive"
> because it pretends words are independent given the class (they aren't), yet it
> works strikingly well — *and* it's interpretable: you can read off the most
> distinctive words it learned per class.

Pure counting and logs — no iteration, no gradients. Offline, deterministic.

## Quick start

```sh
python -m labs.naivebayes.demo
python -m labs.naivebayes.cli eval
python -m labs.naivebayes.cli classify --text "a brilliant and moving film"
python -m labs.naivebayes.cli words
```

```
  test accuracy : 95%     majority guess: 46%

What it learned — most distinctive words per class (log-odds):
  POS →  enjoyed brilliant excellent perfect great stellar love superb
  NEG →  mediocre annoying terrible disappointing worst awful bad waste

  👍 POS (margin 4.3)  "an absolutely wonderful film, the best story…"
  👎 NEG (margin 7.3)  "a boring waste of time, terrible acting…"
  👍 POS (margin 0.0)  "the movie was great but the ending felt disappointing"   ← genuinely mixed
```

## How it works (`nb.py`)

```
score(c) = log P(c)  +  Σ_w∈doc  log P(w | c)
P(w | c) = (count(w, c) + α) / (total_words(c) + α·|V|)     # Laplace smoothing
```

- **Fit** is one pass of counting: per-class word counts, totals, and document
  priors.
- **Smoothing** (`α=1`) gives every word a sliver of probability in every class,
  so a word never seen in a class can't zero out the whole product — and a totally
  novel word just contributes equally to all classes (no evidence).
- **`top_words`** ranks words by **log-odds** (`log P(w|c) − log P(w|other)`), which
  surfaces the *distinctive* words, not the filler — the model's explanation of
  itself.

## What it shows

- **Real signal, not the prior** — ~95% test accuracy on generated sentiment
  reviews vs ~50% for always-guess-the-majority.
- **Interpretable** — the top-words lists are exactly the positive/negative
  vocabulary, recovered from data.
- **Calibrated-ish margins** — a clear review gets a big score gap; a genuinely
  mixed "great but disappointing" review comes out near a tie.
- **Robust to unseen words** and **improves with data** (30 → 300 docs lifts
  accuracy), and it's deterministic.

## Tests

```sh
python -m unittest labs.naivebayes.tests.test_naivebayes -v
```

7 tests: accuracy beats the majority baseline by a wide margin, the top words are
the real class vocabulary (and disjoint across classes), smoothing handles unseen
words without crashing, signal words swing the prediction, more data helps,
tokenization, and determinism.
