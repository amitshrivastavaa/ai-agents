"""The memory store: embeddings, retrieval, reflection, and persistence.

Everything here is pure standard library. Embeddings are a *hashing vectorizer*
(the signed feature-hashing trick) so similar text lands near in vector space
without a model or numpy. Retrieval follows the Generative Agents scoring —
relevance, importance, and recency, each min-max normalized across candidates,
then summed with tunable weights.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

from .._kernel import headline, keywords, stable_seed, tokens

EPISODIC = "episodic"
SEMANTIC = "semantic"

# Salient cue words bump auto-importance — emotionally/biographically weighty.
_SALIENT = frozenset("""
    love loved loves hate hated died death born birth married marriage divorce
    fired hired promoted quit resigned won lost first never always forever scared
    afraid terrified excited thrilled dream dreams goal goals broke breakup moved
    baby wedding funeral diagnosis surgery accident proposed engaged graduated
    failed succeeded breakthrough betrayed promise secret regret proud heartbroken
""".split())


@dataclass
class Memory:
    id: int
    text: str
    kind: str               # EPISODIC | SEMANTIC
    importance: float       # 1..10
    created_tick: int
    last_access_tick: int
    source_ids: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "kind": self.kind,
            "importance": self.importance,
            "created_tick": self.created_tick,
            "last_access_tick": self.last_access_tick,
            "source_ids": self.source_ids,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Memory":
        return cls(
            id=d["id"], text=d["text"], kind=d["kind"],
            importance=float(d["importance"]),
            created_tick=int(d["created_tick"]),
            last_access_tick=int(d["last_access_tick"]),
            source_ids=list(d.get("source_ids", [])),
        )


@dataclass
class Scored:
    """A retrieved memory with its score and component breakdown."""
    memory: Memory
    score: float
    relevance: float
    importance: float
    recency: float


# ------------------------------- embeddings ----------------------------------
def embed(text: str, dims: int) -> list[float]:
    """Signed feature-hashing embedding of ``text``, L2-normalized.

    Each unigram and adjacent bigram votes ``+1``/``-1`` into a hashed bucket.
    Deterministic across processes (seeds come from hashlib, not ``hash()``).
    """
    vec = [0.0] * dims
    toks = tokens(text)
    grams = list(toks)
    grams += [f"{a}_{b}" for a, b in zip(toks, toks[1:])]  # bigrams add signal
    for gram in grams:
        idx = stable_seed("idx", gram) % dims
        sign = 1.0 if stable_seed("sign", gram) % 2 else -1.0
        vec[idx] += sign
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec
    return [x / norm for x in vec]


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))  # inputs are already normalized


def _minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-12:
        return [0.5] * len(values)  # all equal → neutral, no spurious ordering
    return [(v - lo) / (hi - lo) for v in values]


# ------------------------------- the store -----------------------------------
class MemoryStore:
    """A growing, persistent memory with relevance/importance/recency recall."""

    def __init__(
        self,
        path: str | None = None,
        *,
        dims: int = 256,
        recency_decay: float = 0.97,
        reflect_threshold: float = 25.0,
        # (relevance, importance, recency). The Generative-Agents paper weights
        # these equally for *behavior*; for query-driven recall we lean on
        # relevance so search feels like search. Tune per use case.
        weights: tuple[float, float, float] = (1.5, 0.8, 0.8),
        brain=None,
    ):
        self.path = path
        self.dims = dims
        self.recency_decay = recency_decay
        self.reflect_threshold = reflect_threshold
        self.w_rel, self.w_imp, self.w_rec = weights
        self.brain = brain

        self._tick = 0
        self._next_id = 0
        self._memories: list[Memory] = []
        self._since_reflect = 0.0
        self._vec_cache: dict[int, list[float]] = {}

        if path and os.path.exists(path):
            self.load()

    # -- internals --
    def _advance(self) -> int:
        self._tick += 1
        return self._tick

    def _vec(self, mem: Memory) -> list[float]:
        cached = self._vec_cache.get(mem.id)
        if cached is None:
            cached = embed(mem.text, self.dims)
            self._vec_cache[mem.id] = cached
        return cached

    @staticmethod
    def auto_importance(text: str) -> float:
        cues = len(set(tokens(text)) & _SALIENT)
        score = 3.0 + 2.0 * cues + (1.0 if len(text) > 90 else 0.0)
        return max(1.0, min(10.0, score))

    # -- writing --
    def observe(self, text: str, *, importance: float | None = None,
                tick: int | None = None) -> Memory:
        """Record an episodic observation; auto-scores importance if omitted."""
        text = text.strip()
        if not text:
            raise ValueError("cannot observe empty text")
        t = self._advance() if tick is None else tick
        imp = self.auto_importance(text) if importance is None else float(importance)
        mem = Memory(self._next_id, text, EPISODIC, imp, t, t)
        self._next_id += 1
        self._memories.append(mem)
        self._since_reflect += imp
        return mem

    # -- reading --
    def recall(self, query: str, *, k: int = 5, kinds: tuple[str, ...] | None = None,
               touch: bool = False) -> list[Scored]:
        """Return the top-``k`` memories by relevance + importance + recency."""
        cands = [m for m in self._memories if kinds is None or m.kind in kinds]
        if not cands:
            return []
        qv = embed(query, self.dims)
        now = self._tick
        rel_raw = [max(0.0, _cosine(qv, self._vec(m))) for m in cands]
        imp_raw = [m.importance for m in cands]
        rec_raw = [self.recency_decay ** (now - m.last_access_tick) for m in cands]
        rel, imp, rec = _minmax(rel_raw), _minmax(imp_raw), _minmax(rec_raw)

        scored = [
            Scored(m, self.w_rel * r + self.w_imp * i + self.w_rec * c, r, i, c)
            for m, r, i, c in zip(cands, rel, imp, rec)
        ]
        scored.sort(key=lambda s: s.score, reverse=True)
        top = scored[:k]
        if touch:  # retrieval refreshes recency, Generative-Agents style
            for s in top:
                s.memory.last_access_tick = now
        return top

    def working_set(self, n: int = 7) -> list[Memory]:
        """The ``n`` most recent episodic memories — the live context window."""
        episodic = [m for m in self._memories if m.kind == EPISODIC]
        return sorted(episodic, key=lambda m: m.created_tick, reverse=True)[:n]

    # -- reflection (consolidation into semantic memory) --
    def reflect(self, *, max_insights: int = 3, force: bool = False) -> list[Memory]:
        """Distill recent episodes into semantic insights when warranted.

        Triggers once accumulated importance since the last reflection crosses
        ``reflect_threshold`` (or when ``force``). Offline, an insight names a
        recurring theme and cites examples; online, the model writes it.
        """
        if not force and self._since_reflect < self.reflect_threshold:
            return []
        episodic = [m for m in self._memories if m.kind == EPISODIC]
        if len(episodic) < 3:
            return []
        self._since_reflect = 0.0
        recent = sorted(episodic, key=lambda m: m.created_tick, reverse=True)[:15]

        if self.brain is not None:
            try:
                return self._reflect_llm(recent, max_insights)
            except Exception:
                pass  # fall through to offline

        # offline: cluster recent memories by shared salient keyword.
        kw_to_mems: dict[str, list[Memory]] = {}
        for m in recent:
            for kw in keywords(m.text, limit=8):
                kw_to_mems.setdefault(kw, []).append(m)
        ranked = sorted(
            kw_to_mems.items(),
            key=lambda kv: (len(kv[1]), sum(x.importance for x in kv[1])),
            reverse=True,
        )
        insights: list[Memory] = []
        for kw, mems in ranked:
            if len(mems) < 2:
                continue
            examples = "; ".join(headline(x.text, width=48) for x in mems[:2])
            text = f'Recurring theme "{kw}": {examples}.'
            imp = min(10.0, sum(x.importance for x in mems) / len(mems) + 1.0)
            insights.append(self._add_semantic(text, imp, [x.id for x in mems]))
            if len(insights) >= max_insights:
                break
        return insights

    def _reflect_llm(self, recent: list[Memory], max_insights: int) -> list[Memory]:
        block = "\n".join(f"- {m.text}" for m in recent)
        prompt = (
            "From these recent observations about a person, infer up to "
            f"{max_insights} higher-level insights about them (patterns, values, "
            "relationships). Respond ONLY as JSON: "
            '{"insights": [<short sentences>]}\n\n' + block
        )
        data = self.brain.complete_json(prompt, temperature=0.5)
        out: list[Memory] = []
        for text in data.get("insights", [])[:max_insights]:
            out.append(self._add_semantic(str(text).strip(), 6.0, [m.id for m in recent]))
        return out

    def _add_semantic(self, text: str, importance: float, sources: list[int]) -> Memory:
        t = self._advance()
        mem = Memory(self._next_id, text, SEMANTIC, importance, t, t, sources)
        self._next_id += 1
        self._memories.append(mem)
        return mem

    # -- introspection --
    def stats(self) -> dict:
        episodic = sum(1 for m in self._memories if m.kind == EPISODIC)
        semantic = sum(1 for m in self._memories if m.kind == SEMANTIC)
        return {
            "tick": self._tick,
            "total": len(self._memories),
            "episodic": episodic,
            "semantic": semantic,
            "since_reflect": round(self._since_reflect, 2),
            "reflect_threshold": self.reflect_threshold,
            "ready_to_reflect": self._since_reflect >= self.reflect_threshold,
        }

    def all_memories(self) -> list[Memory]:
        return list(self._memories)

    # -- persistence --
    def to_dict(self) -> dict:
        return {
            "version": 1,
            "tick": self._tick,
            "next_id": self._next_id,
            "dims": self.dims,
            "since_reflect": self._since_reflect,
            "memories": [m.to_dict() for m in self._memories],
        }

    def save(self, path: str | None = None) -> str:
        target = path or self.path
        if not target:
            raise ValueError("no path to save to; pass save(path) or set store path")
        os.makedirs(os.path.dirname(os.path.abspath(target)), exist_ok=True)
        tmp = target + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)
        os.replace(tmp, target)  # atomic
        self.path = target
        return target

    def load(self, path: str | None = None) -> None:
        target = path or self.path
        with open(target, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        self._tick = int(data.get("tick", 0))
        self._next_id = int(data.get("next_id", 0))
        self.dims = int(data.get("dims", self.dims))
        self._since_reflect = float(data.get("since_reflect", 0.0))
        self._memories = [Memory.from_dict(d) for d in data.get("memories", [])]
        self._vec_cache.clear()  # embeddings recomputed lazily on demand
        if self._next_id <= max((m.id for m in self._memories), default=-1):
            self._next_id = max((m.id for m in self._memories), default=-1) + 1
