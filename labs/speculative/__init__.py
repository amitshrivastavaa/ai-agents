"""speculative — lossless LLM speedup by drafting and verifying.

The trick behind fast LLM serving: a small, cheap **draft** model guesses the
next few tokens, and the big **target** model checks them all in a single pass,
keeping the longest prefix it agrees with and correcting the first miss. The
output is *identical* to running the target alone — but it takes far fewer
expensive target calls, because several tokens are confirmed per call.

Built from scratch on n-gram language models (a fast bigram draft, an accurate
4-gram target). It shows the two things that matter: the speculative output
exactly matches pure target decoding, and it needs ~2× fewer target calls.
Fully offline, deterministic.
"""
from .ngram import NgramModel
from .speculative import SpecResult, speculative_decode, target_greedy

__all__ = ["NgramModel", "SpecResult", "speculative_decode", "target_greedy"]
