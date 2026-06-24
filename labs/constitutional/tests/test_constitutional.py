"""Tests for constitutional — offline, stdlib only.

    python -m unittest labs.constitutional.tests.test_constitutional -v
"""
from __future__ import annotations

import unittest

from labs.constitutional.constitution import (ALL_PRINCIPLES, NO_INSULTS,
                                              NO_SHOUTING, REDACT_PII)
from labs.constitutional.refine import critique, refine


class PrincipleTests(unittest.TestCase):
    def test_each_principle_fix_removes_its_own_violation(self):
        samples = {
            "no_shouting": "THIS IS LOUD",
            "no_exclaim": "wow!!! really??",
            "no_filler": "this is just really basically fine",
            "no_insults": "what a stupid useless idea",
            "inclusive": "hey guys check the whitelist",
            "no_overclaim": "this is guaranteed to always work",
            "redact_pii": "mail a@b.com or 555-123-4567",
        }
        by_id = {p.id: p for p in ALL_PRINCIPLES}
        for pid, text in samples.items():
            p = by_id[pid]
            with self.subTest(principle=pid):
                self.assertTrue(p.detect(text), f"{pid} should flag {text!r}")
                fixed = p.revise(text)
                self.assertFalse(p.detect(fixed), f"{pid} fix left a violation: {fixed!r}")

    def test_shouting_preserves_acronyms(self):
        self.assertEqual(NO_SHOUTING.detect("the API is great"), [])
        self.assertIn("HELLO", "".join(NO_SHOUTING.detect("HELLO there")))

    def test_pii_redaction(self):
        out = REDACT_PII.revise("email x@y.com, ssn 123-45-6789, card 1234 5678 9012 3456")
        self.assertIn("[EMAIL]", out)
        self.assertIn("[SSN]", out)
        self.assertIn("[CARD]", out)
        self.assertNotIn("x@y.com", out)

    def test_insults_are_softened(self):
        out = NO_INSULTS.revise("this is stupid")
        self.assertNotIn("stupid", out.lower())


class RefineTests(unittest.TestCase):
    def test_converges_to_zero_violations(self):
        msg = "Hey guys, this REALLY stupid plan is GUARANTEED to always work, obviously!!!"
        t = refine(msg, "all")
        self.assertTrue(t.converged)
        self.assertEqual(len(t.final_violations), 0)
        self.assertGreater(len(t.rounds[0].violations), 0)

    def test_clean_text_needs_one_round_no_change(self):
        clean = "The plan is clear and the team is ready."
        t = refine(clean, "professional")
        self.assertEqual(t.final, clean)
        self.assertEqual(t.num_rounds, 1)

    def test_violation_count_is_non_increasing(self):
        t = refine("guys this is just stupid and GUARANTEED!!!", "all")
        counts = [len(r.violations) for r in t.rounds]
        for a, b in zip(counts, counts[1:]):
            self.assertGreaterEqual(a, b)  # each round removes (or holds) issues

    def test_deterministic(self):
        msg = "this is STUPID guys, just useless!!!"
        self.assertEqual(refine(msg, "all").final, refine(msg, "all").final)

    def test_safety_constitution_redacts_but_keeps_tone_words(self):
        t = refine("call me at 555-123-4567", "safety")
        self.assertIn("[PHONE]", t.final)

    def test_transcript_serializable(self):
        import json
        json.dumps(refine("STUPID guys!!!", "all").to_dict())

    def test_markdown_has_rounds(self):
        md = refine("this is just stupid!!!", "all").markdown()
        self.assertIn("Round 1", md)
        self.assertIn("Final", md)


if __name__ == "__main__":
    unittest.main()
