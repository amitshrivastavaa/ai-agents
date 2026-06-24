"""A generated sentiment corpus — positive vs negative 'reviews'.

Each review is mostly shared filler words plus a few class-signal words, with a
little cross-class noise so the task isn't trivial. Deterministic.
"""
from __future__ import annotations

import re

from .._kernel import rng

POS = ("great love excellent amazing wonderful best brilliant enjoyed fantastic "
       "perfect recommend beautiful gripping superb delightful charming stellar").split()
NEG = ("terrible awful boring worst hate disappointing poor waste bad dull "
       "annoying broken bland forgettable tedious lifeless clunky mediocre").split()
FILLER = ("the a movie film was this that story plot watch time really very it and "
          "of to is i with about for on characters scene end").split()


def tokenize(text):
    return re.findall(r"[a-z']+", text.lower())


def _doc(r, signal, other):
    n = r.randint(12, 22)
    words = []
    for _ in range(n):
        x = r.random()
        if x < 0.55:
            words.append(r.choice(FILLER))
        elif x < 0.92:
            words.append(r.choice(signal))          # this class's words
        else:
            words.append(r.choice(other))           # a little cross-class noise
    return words


def corpus(n=400, seed="nb"):
    """Return (docs, labels) — labels are 'pos'/'neg'."""
    r = rng("nb-corpus", seed, n)
    docs, labels = [], []
    for _ in range(n):
        if r.random() < 0.5:
            docs.append(_doc(r, POS, NEG))
            labels.append("pos")
        else:
            docs.append(_doc(r, NEG, POS))
            labels.append("neg")
    return docs, labels


def split(docs, labels, frac=0.7, seed="s"):
    r = rng("nb-split", seed, len(docs))
    idx = list(range(len(docs)))
    r.shuffle(idx)
    cut = int(len(docs) * frac)
    tr, te = idx[:cut], idx[cut:]
    return ([docs[i] for i in tr], [labels[i] for i in tr],
            [docs[i] for i in te], [labels[i] for i in te])
