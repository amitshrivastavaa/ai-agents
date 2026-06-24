"""A TF-IDF index built from scratch: chunk, weight, and retrieve by cosine.

Each document is split into sentence chunks. A chunk's vector weights every term
by ``tf · idf`` — frequent-in-this-chunk but rare-across-the-corpus terms score
highest — and is L2-normalized, so cosine similarity is just a dot product.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

from .._kernel import tokens


@dataclass
class Chunk:
    id: int
    doc_id: str
    doc_title: str
    text: str


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 3]


@dataclass
class TfidfIndex:
    chunks: list[Chunk] = field(default_factory=list)
    idf: dict[str, float] = field(default_factory=dict)
    vectors: list[dict[str, float]] = field(default_factory=list)

    def build(self, docs: list[dict]) -> "TfidfIndex":
        """``docs`` is a list of {id, title, text}."""
        self.chunks = []
        cid = 0
        for d in docs:
            for sent in _sentences(d["text"]):
                self.chunks.append(Chunk(cid, d["id"], d["title"], sent))
                cid += 1

        n = len(self.chunks)
        df: dict[str, int] = {}
        chunk_tokens = []
        for c in self.chunks:
            toks = tokens(c.text)
            chunk_tokens.append(toks)
            for term in set(toks):
                df[term] = df.get(term, 0) + 1
        # smoothed idf
        self.idf = {t: math.log((n + 1) / (df_t + 1)) + 1.0 for t, df_t in df.items()}
        self.vectors = [self._vectorize(toks) for toks in chunk_tokens]
        return self

    def _vectorize(self, toks: list[str]) -> dict[str, float]:
        tf: dict[str, float] = {}
        for t in toks:
            tf[t] = tf.get(t, 0.0) + 1.0
        vec = {t: f * self.idf.get(t, 0.0) for t, f in tf.items() if t in self.idf}
        norm = math.sqrt(sum(w * w for w in vec.values())) or 1.0
        return {t: w / norm for t, w in vec.items()}

    @staticmethod
    def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
        small, big = (a, b) if len(a) < len(b) else (b, a)
        return sum(w * big.get(t, 0.0) for t, w in small.items())

    def query(self, text: str, *, k: int = 3) -> list[tuple[Chunk, float]]:
        qv = self._vectorize(tokens(text))
        scored = [(c, self._cosine(qv, v)) for c, v in zip(self.chunks, self.vectors)]
        scored.sort(key=lambda cs: cs[1], reverse=True)
        return scored[:k]
