"""The RAG pipeline: retrieve relevant chunks, then answer only from them.

Offline the answer is *extractive* — the retrieved sentence most relevant to the
question, returned with its source citation. Below a relevance threshold the
system **abstains** instead of guessing, which is the whole point of grounding:
no source, no answer. With a model attached the same retrieved context can be
synthesized into prose, but the grounding and abstention are unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass

from .index import Chunk, TfidfIndex


@dataclass
class Answer:
    text: str
    grounded: bool
    citations: list[str]            # doc titles the answer draws on
    sources: list[tuple[str, float]]  # (chunk text, score) actually retrieved
    confidence: float


class RAG:
    def __init__(self, docs, *, threshold: float = 0.06, brain=None):
        self.index = TfidfIndex().build(docs)
        self.threshold = threshold
        self.brain = brain

    def retrieve(self, question: str, *, k: int = 3):
        return self.index.query(question, k=k)

    def answer(self, question: str, *, k: int = 3) -> Answer:
        hits = self.retrieve(question, k=k)
        top_score = hits[0][1] if hits else 0.0
        if not hits or top_score < self.threshold:
            return Answer(
                "I couldn't find that in the knowledge base.",
                grounded=False, citations=[],
                sources=[(c.text, s) for c, s in hits[:k]], confidence=top_score,
            )
        if self.brain is not None:
            try:
                return self._answer_llm(question, hits)
            except Exception:
                pass
        # extractive: the single most relevant retrieved sentence, with citation
        best_chunk, best_score = hits[0]
        citations = list(dict.fromkeys(c.doc_title for c, s in hits
                                       if s >= self.threshold))
        return Answer(
            f"{best_chunk.text}  [source: {best_chunk.doc_title}]",
            grounded=True, citations=citations,
            sources=[(c.text, s) for c, s in hits], confidence=best_score,
        )

    def _answer_llm(self, question: str, hits) -> Answer:
        context = "\n".join(f"- {c.text}" for c, _ in hits)
        prompt = (
            "Answer the question using ONLY the context below. If the context "
            "doesn't contain the answer, say you don't know.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
        )
        text = self.brain.complete(prompt, temperature=0.2).strip()
        citations = list(dict.fromkeys(c.doc_title for c, s in hits if s >= self.threshold))
        return Answer(text, grounded=True, citations=citations,
                      sources=[(c.text, s) for c, s in hits], confidence=hits[0][1])
