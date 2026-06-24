"""Tests for lab discovery + demo capture — offline, stdlib only.

    python -m unittest labs._showcase.tests.test_discover -v
"""
from __future__ import annotations

import unittest

from labs._showcase.discover import capture_demo, discover_labs


class DiscoverTests(unittest.TestCase):
    def test_finds_known_labs(self):
        names = discover_labs()
        self.assertIn("hopfield", names)
        self.assertIn("agent_swarm", names)

    def test_skips_private_packages(self):
        names = discover_labs()
        self.assertNotIn("_kernel", names)
        self.assertNotIn("_showcase", names)

    def test_sorted(self):
        names = discover_labs()
        self.assertEqual(names, sorted(names))


class CaptureTests(unittest.TestCase):
    def test_capture_returns_nonempty_output(self):
        out = capture_demo("hopfield")
        self.assertTrue(out.strip())

    def test_capture_raises_on_unknown_lab(self):
        with self.assertRaises(RuntimeError):
            capture_demo("does_not_exist_xyz")
