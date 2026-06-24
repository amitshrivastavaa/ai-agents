"""Speculative decoding: draft k tokens, verify in one target pass, repeat.

Correctness comes from only *accepting* a draft token when the target's own
greedy choice agrees, and *correcting* at the first disagreement — so the output
is exactly what running the target alone would produce, while spending one target
call per accepted *block* instead of per token.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .ngram import NgramModel


@dataclass
class SpecResult:
    tokens: list[str]
    target_calls: int
    draft_calls: int
    accepted_per_round: list[int]
    steps: int

    @property
    def speedup(self) -> float:
        return self.steps / self.target_calls if self.target_calls else 1.0

    @property
    def acceptance_rate(self) -> float:
        if not self.accepted_per_round:
            return 0.0
        return sum(self.accepted_per_round) / len(self.accepted_per_round)


def target_greedy(target: NgramModel, prompt: list[str], steps: int):
    """Baseline: pure greedy target decoding — one target call per token."""
    tokens = target.generate(prompt, steps)
    return tokens, steps


def speculative_decode(draft: NgramModel, target: NgramModel, prompt: list[str],
                       steps: int, *, k: int = 4) -> SpecResult:
    tokens = list(prompt)
    target_calls = draft_calls = 0
    accepted: list[int] = []
    produced = 0

    while produced < steps:
        # 1) draft proposes k tokens cheaply
        draft_seq = []
        cur = list(tokens)
        for _ in range(k):
            t = draft.greedy_next(cur)
            draft_seq.append(t)
            cur.append(t)
            draft_calls += 1

        # 2) target verifies all positions in a single (parallel) call
        target_calls += 1
        n_accept = 0
        correction = None
        for i in range(k):
            tgt = target.greedy_next(tokens + draft_seq[:i])
            if tgt == draft_seq[i]:
                n_accept += 1
            else:
                correction = tgt
                break
        if correction is None:                      # all k matched → get the bonus token
            correction = target.greedy_next(tokens + draft_seq[:k])

        block = draft_seq[:n_accept] + [correction]
        tokens += block
        produced += len(block)
        accepted.append(n_accept)

    tokens = tokens[: len(prompt) + steps]
    return SpecResult(tokens, target_calls, draft_calls, accepted, steps)
