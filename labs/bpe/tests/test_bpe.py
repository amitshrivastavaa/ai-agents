"""Tests for bpe — offline, stdlib only.

    python -m unittest labs.bpe.tests.test_bpe -v
"""
from __future__ import annotations

import unittest

from labs.bpe.bpe import BPETokenizer, get_stats, merge
from labs.bpe.corpus import CORPUS


class PrimitiveTests(unittest.TestCase):
    def test_get_stats_counts_pairs(self):
        self.assertEqual(get_stats([1, 2, 1, 2, 3]), {(1, 2): 2, (2, 1): 1, (2, 3): 1})

    def test_merge_replaces_pair(self):
        self.assertEqual(merge([1, 2, 1, 2, 3], (1, 2), 99), [99, 99, 3])

    def test_merge_handles_overlap_edges(self):
        self.assertEqual(merge([1, 1, 1], (1, 1), 9), [9, 1])


class TrainTests(unittest.TestCase):
    def setUp(self):
        self.tok = BPETokenizer().train(CORPUS, vocab_size=400)

    def test_vocab_and_merge_counts(self):
        self.assertEqual(self.tok.vocab_size, 400)
        self.assertEqual(len(self.tok.merges), 144)

    def test_learned_tokens_are_decodable_subwords(self):
        learned = self.tok.learned_tokens()
        self.assertTrue(learned)
        for idx, s in learned:
            self.assertGreaterEqual(idx, 256)
            self.assertIsInstance(s, str)

    def test_training_is_deterministic(self):
        a = BPETokenizer().train(CORPUS, vocab_size=350).merges
        b = BPETokenizer().train(CORPUS, vocab_size=350).merges
        self.assertEqual(a, b)

    def test_no_merges_at_256(self):
        t = BPETokenizer().train(CORPUS, vocab_size=256)
        self.assertEqual(len(t.merges), 0)
        self.assertEqual(t.encode("agent"), list("agent".encode("utf-8")))


class RoundTripTests(unittest.TestCase):
    def setUp(self):
        self.tok = BPETokenizer().train(CORPUS, vocab_size=400)

    def test_roundtrip_ascii(self):
        for s in ["agent", "An intelligent agent plans ahead.", "", "x", "   "]:
            self.assertEqual(self.tok.decode(self.tok.encode(s)), s)

    def test_roundtrip_unicode_and_emoji(self):
        for s in ["café — déjà vu", "naïve résumé", "🤖🧠✨", "mixed 🤖 café text"]:
            self.assertEqual(self.tok.decode(self.tok.encode(s)), s)

    def test_roundtrip_full_corpus(self):
        self.assertEqual(self.tok.decode(self.tok.encode(CORPUS)), CORPUS)


class CompressionTests(unittest.TestCase):
    def test_more_vocab_compresses_at_least_as_well(self):
        comps = [BPETokenizer().train(CORPUS, vocab_size=v).compression(CORPUS)
                 for v in (256, 300, 400, 512)]
        self.assertEqual(comps[0], 1.0)              # 256 = raw bytes
        for a, b in zip(comps, comps[1:]):
            self.assertGreaterEqual(b, a)            # monotonically improves

    def test_encoding_beats_raw_bytes(self):
        tok = BPETokenizer().train(CORPUS, vocab_size=400)
        text = "agents plan and learn from memory"
        self.assertLess(len(tok.encode(text)), len(text.encode("utf-8")))


if __name__ == "__main__":
    unittest.main()
