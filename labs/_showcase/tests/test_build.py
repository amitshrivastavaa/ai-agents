"""Tests for the showcase build orchestrator — offline, stdlib only.

    python -m unittest labs._showcase.tests.test_build -v
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from labs._showcase.build import build, collect, main
from labs._showcase.discover import discover_labs
from labs._showcase.themes import THEME_MAP

REQUIRED_KEYS = {"name", "theme", "tagline", "inspired_by", "demo", "source_url"}


class CollectTests(unittest.TestCase):
    def test_collect_one_lab_has_required_keys(self):
        data = collect(names=["hopfield"])
        self.assertIn("themes", data)
        self.assertEqual(len(data["labs"]), 1)
        entry = data["labs"][0]
        self.assertEqual(REQUIRED_KEYS, set(entry))
        self.assertEqual(entry["name"], "hopfield")
        self.assertEqual(entry["theme"], "classical")
        self.assertTrue(entry["demo"].strip())
        self.assertTrue(entry["tagline"])
        self.assertTrue(entry["source_url"].endswith("/hopfield"))


class BuildTests(unittest.TestCase):
    def test_build_writes_site(self):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "site"
            build(out, names=["hopfield"])
            data = json.loads((out / "data.json").read_text())
            self.assertEqual(len(data["labs"]), 1)
            for f in ("index.html", "style.css", "app.js"):
                self.assertTrue((out / f).is_file(), f)

    def test_main_returns_zero(self):
        with tempfile.TemporaryDirectory() as d:
            rc = main(["--out", str(Path(d) / "site")])
            self.assertEqual(rc, 0)


class CoverageTests(unittest.TestCase):
    def test_theme_map_has_no_stale_entries(self):
        # The map may lag behind discovery: a newly-landed lab that isn't mapped
        # yet falls back to the "classical" theme (see theme_for), so the site
        # keeps auto-growing without a forced edit. What we DO guard against is a
        # stale entry — a map key that no longer corresponds to a real lab.
        discovered = set(discover_labs())
        stale = set(THEME_MAP) - discovered
        self.assertEqual(stale, set(), f"stale theme-map entries (no such lab): {stale}")
