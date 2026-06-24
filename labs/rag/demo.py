"""Demo: grounded answers with citations, and honest abstention.

    python -m labs.rag.demo
"""
from __future__ import annotations

from .corpus import KNOWLEDGE_BASE
from .rag import RAG


def main() -> int:
    rag = RAG(KNOWLEDGE_BASE)
    print(f"Knowledge base: {len(KNOWLEDGE_BASE)} documents, "
          f"{len(rag.index.chunks)} sentence chunks.\n")

    in_kb = [
        "How do plants turn light into energy?",
        "Which protocol guarantees reliable, ordered delivery?",
        "Why do we only ever see one side of the Moon?",
        "What makes transformers more scalable than RNNs?",
    ]
    print("── Questions answered from the knowledge base (with citations) ──\n")
    for q in in_kb:
        a = rag.answer(q)
        print(f"  Q: {q}")
        print(f"  A: {a.text}")
        print(f"     (confidence {a.confidence:.2f})\n")

    out_kb = ["What is the capital of France?", "How do I fix a flat tyre?"]
    print("── Questions NOT in the knowledge base — it abstains, never guesses ──\n")
    for q in out_kb:
        a = rag.answer(q)
        print(f"  Q: {q}\n  A: {a.text}\n")

    print("Retrieve, then answer only from what was retrieved — with a citation,")
    print("and an honest 'I don't know' when nothing relevant is found. That")
    print("grounding is what separates RAG from a model guessing on its own.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
