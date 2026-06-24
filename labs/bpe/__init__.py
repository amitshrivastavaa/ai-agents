"""bpe — a byte-level Byte-Pair Encoding tokenizer, from scratch.

The first thing every LLM does to your text: chop it into tokens. This builds
the GPT-style tokenizer from first principles — start from raw bytes, then
repeatedly merge the most frequent adjacent pair into a new token until the
vocabulary is full. Common chunks (" the", "ing", "tion") become single tokens,
so text compresses; and because it operates on bytes, ``decode(encode(x)) == x``
for *any* input, exactly.

Fully offline, deterministic, no dependencies. (Homage to Karpathy's minbpe.)
"""
from .bpe import BPETokenizer
from .corpus import CORPUS

__all__ = ["BPETokenizer", "CORPUS"]
