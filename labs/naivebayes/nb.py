"""Multinomial Naive Bayes — the classic text classifier.

"Naive" because it assumes words are independent given the class — wrong, but it
works remarkably well. For a document, score each class by its log-prior plus the
log-likelihood of every word, and pick the best:

    score(c) = log P(c) + Σ_w count(w)·log P(w | c)

Word probabilities use **Laplace (add-α) smoothing** so a word never seen in a
class doesn't zero out the whole product. Everything is counts and logs — no
iteration, no gradients.
"""
from __future__ import annotations

import math


class MultinomialNB:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.classes = []
        self.vocab = set()
        self.log_prior = {}
        self.word_count = {}        # class -> {word: count}
        self.total = {}             # class -> total word count

    def fit(self, docs, labels):
        self.classes = sorted(set(labels))
        self.vocab = set(w for d in docs for w in d)
        self.word_count = {c: {} for c in self.classes}
        self.total = {c: 0 for c in self.classes}
        doc_count = {c: 0 for c in self.classes}
        for d, c in zip(docs, labels):
            doc_count[c] += 1
            wc = self.word_count[c]
            for w in d:
                wc[w] = wc.get(w, 0) + 1
                self.total[c] += 1
        n = len(docs)
        self.log_prior = {c: math.log(doc_count[c] / n) for c in self.classes}
        return self

    def _log_likelihood(self, w, c):
        v = len(self.vocab)
        return math.log((self.word_count[c].get(w, 0) + self.alpha) /
                        (self.total[c] + self.alpha * v))

    def score(self, doc):
        return {c: self.log_prior[c] + sum(self._log_likelihood(w, c)
                                           for w in doc if w in self.vocab)
                for c in self.classes}

    def predict(self, docs):
        return [max(self.score(d).items(), key=lambda kv: kv[1])[0] for d in docs]

    def top_words(self, c, k=8):
        """Most *distinctive* words for class ``c`` by log-odds vs the others."""
        others = [o for o in self.classes if o != c]
        scored = []
        for w in self.vocab:
            here = self._log_likelihood(w, c)
            elsewhere = max(self._log_likelihood(w, o) for o in others)
            scored.append((w, here - elsewhere))
        return [w for w, _ in sorted(scored, key=lambda kv: kv[1], reverse=True)[:k]]
