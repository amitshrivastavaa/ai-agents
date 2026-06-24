"""Tests for the showcase theme map — offline, stdlib only.

    python -m unittest labs._showcase.tests.test_themes -v
"""
from __future__ import annotations

import unittest

from labs._showcase.themes import THEME_MAP, THEMES, theme_for


class ThemeTests(unittest.TestCase):
    def test_every_mapped_theme_is_defined(self):
        for name, theme in THEME_MAP.items():
            self.assertIn(theme, THEMES, f"{name} -> unknown theme {theme!r}")

    def test_themes_have_label_and_accent(self):
        for tid, meta in THEMES.items():
            self.assertIn("label", meta)
            self.assertIn("accent", meta)
            self.assertTrue(meta["accent"].startswith("#"), tid)

    def test_theme_for_defaults_to_classical(self):
        self.assertEqual(theme_for("totally_new_lab"), "classical")
        self.assertEqual(theme_for("hopfield"), "classical")
        self.assertEqual(theme_for("agent_swarm"), "agents")
