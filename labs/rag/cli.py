"""CLI for the from-scratch RAG system.

    python -m labs.rag.cli ask "How do plants make energy from light?"
    python -m labs.rag.cli ask "What is the capital of France?"   # abstains
    python -m labs.rag.cli retrieve "reliable ordered delivery"
    python -m labs.rag.cli stats
"""
from __future__ import annotations

import argparse
import sys

from .._kernel import get_brain, mode
from .corpus import KNOWLEDGE_BASE
from .rag import RAG


def _rag():
    return RAG(KNOWLEDGE_BASE, brain=(get_brain() if mode() == "online" else None))


def _cmd_ask(args) -> int:
    rag = _rag()
    q = " ".join(args.question)
    a = rag.answer(q, k=args.k)
    print(f"Q: {q}\n")
    if a.grounded:
        print(f"A: {a.text}")
        print(f"\n   confidence {a.confidence:.2f} · cited: {', '.join(a.citations)}")
    else:
        print(f"A: {a.text}  (abstained — nothing relevant above threshold)")
    print("\n   retrieved passages:")
    for text, score in a.sources:
        print(f"     [{score:4.2f}] {text[:74]}")
    return 0


def _cmd_retrieve(args) -> int:
    rag = _rag()
    for c, s in rag.retrieve(" ".join(args.query), k=args.k):
        print(f"  [{s:4.2f}] ({c.doc_title}) {c.text}")
    return 0


def _cmd_stats(_args) -> int:
    idx = RAG(KNOWLEDGE_BASE).index
    docs = len({c.doc_id for c in idx.chunks})
    print(f"  documents : {docs}")
    print(f"  chunks    : {len(idx.chunks)} (sentence-level)")
    print(f"  vocabulary: {len(idx.idf)} terms")
    print(f"  mode      : {mode()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rag", description="Retrieval-augmented generation grounded in a knowledge base.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("ask")
    p.add_argument("question", nargs="+")
    p.add_argument("-k", type=int, default=3)
    p.set_defaults(func=_cmd_ask)

    p = sub.add_parser("retrieve")
    p.add_argument("query", nargs="+")
    p.add_argument("-k", type=int, default=3)
    p.set_defaults(func=_cmd_retrieve)

    sub.add_parser("stats").set_defaults(func=_cmd_stats)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
