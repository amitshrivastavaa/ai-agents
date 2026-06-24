"""A back-off n-gram language model with deterministic greedy decoding."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+|[.,!?;]", text.lower())


@dataclass
class NgramModel:
    order: int = 4
    # ctx[L][context_tuple] = {next_token: count}
    ctx: list[dict] = field(default_factory=list)
    unigram: dict = field(default_factory=dict)

    def train(self, text: str) -> "NgramModel":
        toks = tokenize(text)
        self.ctx = [dict() for _ in range(self.order)]   # context lengths 0..order-1
        self.unigram = {}
        for i, tok in enumerate(toks):
            self.unigram[tok] = self.unigram.get(tok, 0) + 1
            for L in range(self.order):
                if i - L < 0:
                    continue
                context = tuple(toks[i - L:i])
                table = self.ctx[L].setdefault(context, {})
                table[tok] = table.get(tok, 0) + 1
        return self

    @staticmethod
    def _argmax(table: dict) -> str:
        # highest count, ties broken alphabetically → fully deterministic
        return min(table.items(), key=lambda kv: (-kv[1], kv[0]))[0]

    def greedy_next(self, tokens: list[str]) -> str:
        """The most likely next token, backing off to shorter contexts."""
        for L in range(self.order - 1, -1, -1):
            context = tuple(tokens[-L:]) if L > 0 else ()
            table = self.ctx[L].get(context)
            if table:
                return self._argmax(table)
        return self._argmax(self.unigram)

    def generate(self, prompt: list[str], steps: int) -> list[str]:
        tokens = list(prompt)
        for _ in range(steps):
            tokens.append(self.greedy_next(tokens))
        return tokens
