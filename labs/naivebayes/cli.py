"""CLI for the naive Bayes lab.

    python -m labs.naivebayes.cli eval
    python -m labs.naivebayes.cli classify --text "a brilliant and moving film"
    python -m labs.naivebayes.cli words
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter

from .nb import MultinomialNB
from .data import corpus, split, tokenize


def _acc(yh, y):
    return sum(1 for a, b in zip(yh, y) if a == b) / len(y)


def _trained(seed="cli", n=500):
    docs, labels = corpus(n=n, seed=seed)
    Xtr, ytr, Xte, yte = split(docs, labels, seed=seed)
    return MultinomialNB(alpha=1.0).fit(Xtr, ytr), (Xte, yte, ytr)


def _cmd_eval(args) -> int:
    nb, (Xte, yte, ytr) = _trained(args.seed)
    maj = Counter(ytr).most_common(1)[0][0]
    print(f"# naive Bayes sentiment eval  (alpha={nb.alpha})\n")
    print(f"  test accuracy   : {_acc(nb.predict(Xte), yte) * 100:.1f}%")
    print(f"  majority baseline: {_acc([maj] * len(yte), yte) * 100:.1f}%")
    print(f"  vocabulary size : {len(nb.vocab)} words")
    return 0


def _cmd_classify(args) -> int:
    nb, _ = _trained(args.seed)
    doc = tokenize(args.text)
    s = nb.score(doc)
    pred = max(s.items(), key=lambda kv: kv[1])[0]
    print(f"# classify: {args.text!r}\n")
    for c in nb.classes:
        print(f"  log-score[{c}] = {s[c]:8.2f}")
    print(f"\n  → {pred.upper()}   (margin {abs(s['pos'] - s['neg']):.1f})")
    return 0


def _cmd_words(args) -> int:
    nb, _ = _trained(args.seed)
    print("# most distinctive words per class (log-odds)\n")
    for c in nb.classes:
        print(f"  {c.upper():4} →  " + "  ".join(nb.top_words(c, args.k)))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="naivebayes", description="Multinomial Naive Bayes text classifier.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("eval", help="train + report accuracy")
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_eval)

    p = sub.add_parser("classify", help="classify a sentence")
    p.add_argument("--text", default="a brilliant and moving film, the best i have seen")
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_classify)

    p = sub.add_parser("words", help="top words per class")
    p.add_argument("--k", type=int, default=10)
    p.add_argument("--seed", default="cli")
    p.set_defaults(func=_cmd_words)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
