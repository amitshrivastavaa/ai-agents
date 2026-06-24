"""In-context induction task: a random block of tokens, repeated."""
from __future__ import annotations

from .._kernel import rng
from .induction import predict


def repeat_pattern(n_symbols=8, block=4, repeats=3, seed="task"):
    """A block of ``block`` *distinct* tokens (so each has a unique successor),
    repeated ``repeats`` times — the canonical in-context induction sequence."""
    r = rng("induction-task", seed, n_symbols, block, repeats)
    alphabet = [chr(ord("a") + i) for i in range(n_symbols)]
    blk = r.sample(alphabet, block)               # distinct → unambiguous induction
    return "".join(blk * repeats)


def induction_accuracy(text, predictor=predict, strength=12.0, *, warmup_blocks=1,
                       block=None):
    """Fraction of correctly predicted next-tokens in the *repeated* region.

    The first ``warmup_blocks`` of tokens are skipped (nothing to induct from yet);
    after that, a correct circuit should predict each next token from the pattern.
    """
    toks = [c for c in text if c != " "]
    preds = predictor(text, strength)
    start = (block or 0) * warmup_blocks
    correct = total = 0
    for i in range(start, len(toks) - 1):
        total += 1
        if preds[i] == toks[i + 1]:
            correct += 1
    return correct / total if total else 0.0
