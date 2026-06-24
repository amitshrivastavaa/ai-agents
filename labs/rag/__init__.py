"""rag — retrieval-augmented generation, from scratch.

The dominant pattern for grounding answers in your own documents: index a
knowledge base, retrieve the passages most relevant to a question, and answer
*only* from what was retrieved — with citations, and an honest "I don't know"
when nothing relevant turns up.

Built end to end with no dependencies: a **TF-IDF** index from first principles
(term frequencies × inverse document frequencies, cosine similarity), top-k
retrieval, an extractive grounded answer with a source citation, and abstention
below a relevance threshold (the anti-hallucination guarantee). A real model can
synthesize the answer when ``ANTHROPIC_API_KEY`` is set; offline it's
extractive. Deterministic.
"""
from .index import Chunk, TfidfIndex
from .rag import Answer, RAG
from .corpus import KNOWLEDGE_BASE

__all__ = ["Chunk", "TfidfIndex", "Answer", "RAG", "KNOWLEDGE_BASE"]
