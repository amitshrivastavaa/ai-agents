"""Demo: a naive Bayes sentiment classifier, and what it learned.

    python -m labs.naivebayes.demo
"""
from __future__ import annotations

from .nb import MultinomialNB
from .data import corpus, split, tokenize


def _acc(yh, y):
    return sum(1 for a, b in zip(yh, y) if a == b) / len(y)


EXAMPLES = [
    "an absolutely wonderful film, the best story i have ever enjoyed",
    "a boring waste of time, terrible acting and a dull broken plot",
    "the movie was really great but the ending felt a bit disappointing",
]


def main() -> int:
    docs, labels = corpus(n=500, seed="demo")
    Xtr, ytr, Xte, yte = split(docs, labels, seed="demo")
    nb = MultinomialNB(alpha=1.0).fit(Xtr, ytr)

    print("Naive Bayes — the classic text classifier, counts and logs only.\n")
    print(f"Trained on {len(Xtr)} generated movie reviews (pos / neg).")
    from collections import Counter
    maj = Counter(ytr).most_common(1)[0][0]
    print(f"  test accuracy : {_acc(nb.predict(Xte), yte) * 100:.0f}%")
    print(f"  majority guess: {_acc([maj] * len(yte), yte) * 100:.0f}%   "
          f"(it's learning real signal, not the prior)\n")

    print("What it learned — the most *distinctive* words per class (log-odds):")
    print("  POS →  " + "  ".join(nb.top_words("pos", 8)))
    print("  NEG →  " + "  ".join(nb.top_words("neg", 8)))

    print("\nClassify new reviews (margin = how far apart the class scores are):")
    for text in EXAMPLES:
        doc = tokenize(text)
        s = nb.score(doc)
        pred = max(s.items(), key=lambda kv: kv[1])[0]
        margin = abs(s["pos"] - s["neg"])
        mark = {"pos": "👍", "neg": "👎"}[pred]
        print(f'  {mark} {pred.upper():3} (margin {margin:4.1f})  "{text[:54]}"')

    print("\nUnseen words don't break it: Laplace smoothing gives every word a tiny")
    print("probability in every class, so a novel word just adds no evidence either way.")
    print("And it keeps improving with data:")
    for ntr in (30, 100, 300):
        d, l = corpus(n=ntr + 150, seed="curve")
        xt, yt, xv, yv = split(d, l, frac=ntr / (ntr + 150), seed="curve")
        a = _acc(MultinomialNB().fit(xt, yt).predict(xv), yv)
        print(f"   {len(xt):>3} train docs → {a * 100:.0f}% test accuracy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
