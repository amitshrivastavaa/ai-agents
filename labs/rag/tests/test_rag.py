"""Tests for rag — offline, stdlib only.

    python -m unittest labs.rag.tests.test_rag -v
"""
from __future__ import annotations

import unittest

from labs.rag.corpus import KNOWLEDGE_BASE
from labs.rag.index import TfidfIndex
from labs.rag.rag import RAG


class IndexTests(unittest.TestCase):
    def setUp(self):
        self.idx = TfidfIndex().build(KNOWLEDGE_BASE)

    def test_chunks_and_vocab_built(self):
        self.assertGreater(len(self.idx.chunks), len(KNOWLEDGE_BASE))   # sentence chunks
        self.assertGreater(len(self.idx.idf), 20)
        self.assertEqual(len(self.idx.vectors), len(self.idx.chunks))

    def test_vectors_are_normalized(self):
        import math
        for v in self.idx.vectors:
            if v:
                norm = math.sqrt(sum(w * w for w in v.values()))
                self.assertAlmostEqual(norm, 1.0, places=6)

    def test_retrieves_the_right_document(self):
        top = self.idx.query("light energy chlorophyll plants", k=1)[0][0]
        self.assertEqual(top.doc_id, "photosynthesis")
        top = self.idx.query("three-way handshake reliable bytes", k=1)[0][0]
        self.assertEqual(top.doc_id, "tcp")

    def test_idf_downweights_common_terms(self):
        # a term in many chunks has lower idf than a rare one
        commons = sorted(self.idx.idf.values())
        self.assertLess(commons[0], commons[-1])


class RAGTests(unittest.TestCase):
    def setUp(self):
        self.rag = RAG(KNOWLEDGE_BASE)

    def test_grounded_answer_cites_correct_source(self):
        a = self.rag.answer("How do plants convert light into energy?")
        self.assertTrue(a.grounded)
        self.assertIn("Photosynthesis", a.citations)
        self.assertGreater(a.confidence, self.rag.threshold)

    def test_abstains_when_out_of_knowledge_base(self):
        for q in ("What is the capital of France?", "How do I bake bread?"):
            a = self.rag.answer(q)
            with self.subTest(q=q):
                self.assertFalse(a.grounded)
                self.assertEqual(a.citations, [])
                self.assertIn("couldn't find", a.text)

    def test_answer_is_grounded_in_a_retrieved_chunk(self):
        a = self.rag.answer("What is crema?")
        self.assertTrue(a.grounded)
        retrieved_texts = " ".join(t for t, _ in a.sources)
        self.assertIn("crema", retrieved_texts.lower())

    def test_threshold_controls_abstention(self):
        strict = RAG(KNOWLEDGE_BASE, threshold=0.99)
        self.assertFalse(strict.answer("How do plants make energy?").grounded)
        lenient = RAG(KNOWLEDGE_BASE, threshold=0.0)
        self.assertTrue(lenient.answer("How do plants make energy?").grounded)

    def test_deterministic(self):
        a = self.rag.answer("Why is the moon tidally locked?").text
        b = self.rag.answer("Why is the moon tidally locked?").text
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
