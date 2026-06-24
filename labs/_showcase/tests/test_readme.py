"""Tests for the README MVP-table parser — offline, stdlib only.

    python -m unittest labs._showcase.tests.test_readme -v
"""
from __future__ import annotations

import unittest

from labs._showcase.readme import parse_readme

SAMPLE = """\
# labs

| MVP | What it is | Inspired by |
| --- | --- | --- |
| [`agent_swarm`](agent_swarm/) | A panel of agents debates and votes. | the viral *TradingAgents* firm |
| [`hopfield`](hopfield/) | Associative memory from corrupted cues. | Hopfield networks (Nobel 2024) |

_(more landing through the night)_
"""


class ParseReadmeTests(unittest.TestCase):
    def test_extracts_each_lab(self):
        out = parse_readme(SAMPLE)
        self.assertEqual(set(out), {"agent_swarm", "hopfield"})

    def test_tagline_and_inspired_by(self):
        out = parse_readme(SAMPLE)
        self.assertEqual(out["hopfield"]["tagline"],
                         "Associative memory from corrupted cues.")
        self.assertEqual(out["hopfield"]["inspired_by"],
                         "Hopfield networks (Nobel 2024)")

    def test_ignores_header_separator_and_prose(self):
        out = parse_readme(SAMPLE)
        self.assertNotIn("MVP", out)
        self.assertNotIn("---", out)
        self.assertEqual(len(out), 2)
