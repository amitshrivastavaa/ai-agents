"""Tests that the static frontend ships the expected hooks — stdlib only.

    python -m unittest labs._showcase.tests.test_static -v
"""
from __future__ import annotations

import unittest
from pathlib import Path

STATIC = Path(__file__).resolve().parents[1] / "static"


class StaticAssetTests(unittest.TestCase):
    def test_files_exist(self):
        for f in ("index.html", "style.css", "app.js"):
            self.assertTrue((STATIC / f).is_file(), f)

    def test_index_wires_assets(self):
        html = (STATIC / "index.html").read_text()
        self.assertIn("style.css", html)
        self.assertIn("app.js", html)
        self.assertIn('id="app"', html)

    def test_app_js_loads_data_and_has_views(self):
        js = (STATIC / "app.js").read_text()
        self.assertIn("data.json", js)
        self.assertIn("renderLauncher", js)
        self.assertIn("renderSession", js)

    def test_app_js_renders_plain_english_layer(self):
        js = (STATIC / "app.js").read_text()
        self.assertIn("DATA.hero", js)       # landing hero (what/why/how)
        self.assertIn("l.plain", js)         # plain description on cards
        self.assertIn("themeBlurb", js)      # per-theme room blurb

    def test_style_uses_accent_variable(self):
        css = (STATIC / "style.css").read_text()
        self.assertIn("--accent", css)
