"""Tests for agent_memory — offline, stdlib only.

    python -m unittest labs.agent_memory.tests.test_memory -v
"""
from __future__ import annotations

import math
import os
import tempfile
import unittest

from labs.agent_memory.memory import EPISODIC, SEMANTIC, MemoryStore, embed


class EmbeddingTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(embed("the climbing trip was great", 128),
                         embed("the climbing trip was great", 128))

    def test_unit_norm(self):
        v = embed("trail running by the river", 256)
        self.assertAlmostEqual(math.sqrt(sum(x * x for x in v)), 1.0, places=6)

    def test_similar_text_closer_than_unrelated(self):
        a = embed("I love climbing and bouldering outdoors", 256)
        climb = embed("went bouldering and climbing at the gym", 256)
        tax = embed("quarterly tax filing spreadsheet deadline", 256)
        dot = lambda x, y: sum(p * q for p, q in zip(x, y))
        self.assertGreater(dot(a, climb), dot(a, tax))


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.s = MemoryStore(dims=256)
        self.s.observe("I went rock climbing in the mountains", importance=5)
        self.s.observe("Filed my quarterly taxes today", importance=5)
        self.s.observe("Bouldering session at the gym with friends", importance=5)

    def test_relevant_memory_ranks_first(self):
        hits = self.s.recall("climbing and bouldering", k=3)
        self.assertIn("climbing", hits[0].memory.text.lower() + hits[1].memory.text.lower())
        top_text = hits[0].memory.text.lower()
        self.assertTrue("climb" in top_text or "boulder" in top_text)

    def test_importance_breaks_ties(self):
        s = MemoryStore(dims=256)
        s.observe("note about project alpha", importance=2, tick=1)
        s.observe("note about project alpha", importance=9, tick=1)
        hits = s.recall("project alpha", k=2)
        self.assertEqual(hits[0].memory.importance, 9)

    def test_recency_breaks_ties(self):
        s = MemoryStore(dims=256)
        old = s.observe("status meeting about widgets", importance=5)
        for _ in range(20):  # advance time
            s.observe("unrelated filler observation here", importance=1)
        new = s.observe("status meeting about widgets", importance=5)
        hits = s.recall("status meeting about widgets", k=2)
        self.assertEqual(hits[0].memory.id, new.id)
        self.assertNotEqual(hits[0].memory.id, old.id)


class ReflectionTests(unittest.TestCase):
    def test_reflection_triggers_and_creates_semantic(self):
        s = MemoryStore(dims=256, reflect_threshold=10.0)
        for _ in range(4):
            s.observe("Climbing trip planning with Sara, so excited", importance=4)
        insights = s.reflect()
        self.assertTrue(insights)
        self.assertTrue(all(m.kind == SEMANTIC for m in insights))
        self.assertTrue(all(m.source_ids for m in insights))

    def test_no_reflection_below_threshold(self):
        s = MemoryStore(dims=256, reflect_threshold=100.0)
        s.observe("a small note", importance=2)
        self.assertEqual(s.reflect(), [])


class PersistenceTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "store.json")
            s = MemoryStore(path=path, dims=128)
            s.observe("I adopted a rescue dog named Pixel", importance=8)
            s.observe("Pixel learned to sit today", importance=4)
            s.save()

            s2 = MemoryStore(path=path, dims=128)
            self.assertEqual(len(s2.all_memories()), 2)
            hits = s2.recall("the dog", k=1)
            self.assertIn("pixel", hits[0].memory.text.lower())

    def test_save_is_atomic_and_reloads_counters(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "store.json")
            s = MemoryStore(path=path)
            for i in range(5):
                s.observe(f"observation number {i}", importance=3)
            s.save()
            s2 = MemoryStore(path=path)
            m = s2.observe("a fresh one after reload", importance=3)
            self.assertEqual(m.id, 5)  # next_id continued, no collision


if __name__ == "__main__":
    unittest.main()
