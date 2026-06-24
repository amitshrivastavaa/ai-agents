"""naivebayes — a multinomial Naive Bayes text classifier, from scratch.

The workhorse of text classification (spam filters, sentiment, topic labeling).
"Naive" because it assumes words are conditionally independent given the class —
false, yet it works strikingly well. Score a document by ``log P(c) + Σ count(w)·
log P(w|c)`` with **Laplace smoothing**, pick the best class. Pure counting and
logs: no iteration, no gradients, and it's interpretable — you can read the most
distinctive words it learned per class.

Offline, deterministic. The probabilistic-NLP counterpart to the lab's `tree`
(geometric) and `lsh`/`rag` (retrieval) classifiers.
"""
from .nb import MultinomialNB
from .data import corpus, split, tokenize

__all__ = ["MultinomialNB", "corpus", "split", "tokenize"]
