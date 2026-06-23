"""Tests for the agent_swarm deliberation engine — all offline, stdlib only.

    python -m unittest labs.agent_swarm.tests.test_engine -v
"""
from __future__ import annotations

import unittest

from labs.agent_swarm.engine import _topic_signal, deliberate
from labs.agent_swarm.personas import PANELS, get_panel


class TopicSignalTests(unittest.TestCase):
    def test_positive_wording_reads_positive(self):
        self.assertGreater(_topic_signal("record growth, strong demand, durable moat"), 0.2)

    def test_negative_wording_reads_negative(self):
        self.assertLess(_topic_signal("lawsuit, declining margins, crowded and overvalued"), -0.2)

    def test_signal_is_deterministic(self):
        q = "Adopt event sourcing for the orders service?"
        self.assertEqual(_topic_signal(q), _topic_signal(q))


class DeliberationTests(unittest.TestCase):
    def test_runs_for_every_panel(self):
        for pid, panel in PANELS.items():
            with self.subTest(panel=pid):
                result = deliberate(panel, "Should we proceed with the proposal?")
                self.assertEqual(len(result.openings), len(panel.personas))
                self.assertEqual(len(result.revised), len(panel.personas))
                # each persona critiques two others
                self.assertEqual(len(result.critiques), 2 * len(panel.personas))
                self.assertIn(result.decision.verdict,
                              [label for _, label in panel.verdicts])

    def test_deterministic_verdict(self):
        panel = get_panel("trading")
        q = "Go long the stock into a record-demand, strong-momentum quarter?"
        a = deliberate(panel, q).decision
        b = deliberate(panel, q).decision
        self.assertEqual(a.verdict, b.verdict)
        self.assertAlmostEqual(a.score, b.score, places=9)

    def test_bullish_question_beats_bearish_question(self):
        panel = get_panel("trading")
        bull = deliberate(panel, "Record growth, strong demand, breakout momentum, durable moat").decision
        bear = deliberate(panel, "Lawsuit, declining demand, overvalued, crowded, froth, debt").decision
        self.assertGreater(bull.score, bear.score)

    def test_confidence_and_consensus_in_unit_range(self):
        result = deliberate(get_panel("product"), "Ship the AI auto-reply feature?")
        d = result.decision
        self.assertGreaterEqual(d.confidence, 0.0)
        self.assertLessEqual(d.confidence, 1.0)
        self.assertGreaterEqual(d.consensus, 0.0)
        self.assertLessEqual(d.consensus, 1.0)

    def test_record_is_json_serializable(self):
        import json
        result = deliberate(get_panel("vc"), "Lead the seed round in the startup?")
        json.dumps(result.record())  # must not raise

    def test_transcript_contains_key_sections(self):
        md = deliberate(get_panel("hiring"), "Hire the candidate?").transcript_md()
        for section in ("Opening statements", "Cross-examination", "Revised vote",
                        "Moderator synthesis", "Verdict"):
            self.assertIn(section, md)


if __name__ == "__main__":
    unittest.main()
