"""The byte-pair encoding tokenizer.

Training: encode the corpus as UTF-8 bytes (256 base tokens), then repeatedly
find the most frequent adjacent pair and mint a new token for it, recording the
merge. Encoding replays the merges in the order they were learned; decoding just
concatenates each token's bytes — so a byte-level BPE round-trips any text
exactly.
"""
from __future__ import annotations


def get_stats(ids: list[int], counts: dict | None = None) -> dict[tuple[int, int], int]:
    counts = counts if counts is not None else {}
    for pair in zip(ids, ids[1:]):
        counts[pair] = counts.get(pair, 0) + 1
    return counts


def merge(ids: list[int], pair: tuple[int, int], idx: int) -> list[int]:
    out: list[int] = []
    i = 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            out.append(idx)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


class BPETokenizer:
    def __init__(self) -> None:
        self.merges: dict[tuple[int, int], int] = {}
        self.vocab: dict[int, bytes] = {i: bytes([i]) for i in range(256)}

    @property
    def vocab_size(self) -> int:
        return len(self.vocab)

    def train(self, text: str, vocab_size: int = 400) -> "BPETokenizer":
        assert vocab_size >= 256, "vocab must include the 256 base byte tokens"
        num_merges = vocab_size - 256
        ids = list(text.encode("utf-8"))
        self.merges = {}
        self.vocab = {i: bytes([i]) for i in range(256)}
        for i in range(num_merges):
            stats = get_stats(ids)
            if not stats:
                break
            # most frequent pair; ties broken deterministically by pair value
            pair = max(stats, key=lambda p: (stats[p], -p[0], -p[1]))
            if stats[pair] < 2:
                break  # nothing worth merging
            idx = 256 + i
            ids = merge(ids, pair, idx)
            self.merges[pair] = idx
            self.vocab[idx] = self.vocab[pair[0]] + self.vocab[pair[1]]
        return self

    def encode(self, text: str) -> list[int]:
        ids = list(text.encode("utf-8"))
        while len(ids) >= 2:
            stats = get_stats(ids)
            # apply the merge that was learned earliest (lowest new-token id)
            pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges:
                break
            ids = merge(ids, pair, self.merges[pair])
        return ids

    def decode(self, ids: list[int]) -> str:
        data = b"".join(self.vocab[i] for i in ids)
        return data.decode("utf-8", errors="replace")

    def token_str(self, idx: int) -> str:
        return self.vocab[idx].decode("utf-8", errors="replace")

    def learned_tokens(self) -> list[tuple[int, str]]:
        """The merged (non-byte) tokens, in the order they were learned."""
        return [(idx, self.token_str(idx)) for idx in sorted(self.vocab) if idx >= 256]

    def compression(self, text: str) -> float:
        raw = len(text.encode("utf-8"))
        return raw / max(1, len(self.encode(text)))
