"""Tests for repo_cartographer — offline, stdlib only.

    python -m unittest labs.repo_cartographer.tests.test_cartographer -v
"""
from __future__ import annotations

import os
import tempfile
import unittest

from labs.repo_cartographer.graph import CodeGraph, Module
from labs.repo_cartographer.scan import scan

_PKG = {
    "__init__.py": "from .a import A\n",
    "a.py": "from .b import B\nclass A: pass\n",
    "b.py": "import os\nfrom .util import helper\nclass B: pass\n",
    "util.py": "def helper():\n    return 1\n",
    "c.py": "from .a import A\n",          # depends on a (-> b -> util)
    "cyc1.py": "from .cyc2 import two\n",
    "cyc2.py": "from .cyc1 import one\n",  # cyc1 <-> cyc2
}


def _write_pkg(root: str) -> str:
    pkg = os.path.join(root, "pkg")
    os.makedirs(pkg)
    for fname, src in _PKG.items():
        with open(os.path.join(pkg, fname), "w", encoding="utf-8") as fh:
            fh.write(src)
    return pkg


class ScanTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        pkg = _write_pkg(self._tmp.name)
        self.g = scan(pkg)

    def tearDown(self):
        self._tmp.cleanup()

    def test_modules_named_with_package_prefix(self):
        self.assertIn("pkg.a", self.g.modules)
        self.assertIn("pkg", self.g.modules)  # __init__ -> package node
        self.assertTrue(self.g.modules["pkg"].is_package)

    def test_relative_imports_resolved(self):
        self.assertEqual(self.g.out_edges("pkg.a"), {"pkg.b"})
        self.assertEqual(self.g.out_edges("pkg.b"), {"pkg.util"})

    def test_external_imports_tracked_not_edged(self):
        self.assertIn("os", self.g.modules["pkg.b"].imports_external)
        self.assertNotIn("os", self.g.out_edges("pkg.b"))

    def test_transitive_dependencies(self):
        self.assertEqual(self.g.dependencies_of("pkg.c"), {"pkg.a", "pkg.b", "pkg.util"})

    def test_impact_is_reverse_closure(self):
        impacted = self.g.impact_of("pkg.util")
        self.assertIn("pkg.b", impacted)
        self.assertIn("pkg.a", impacted)
        self.assertIn("pkg.c", impacted)

    def test_cycle_detected(self):
        cycles = self.g.cycles()
        self.assertTrue(any(set(c) == {"pkg.cyc1", "pkg.cyc2"} for c in cycles))

    def test_centrality_and_symbols(self):
        top = dict(self.g.central())
        self.assertGreaterEqual(top["pkg.util"], 1)
        self.assertEqual(self.g.find_symbol("A"), [("A", "class", "pkg.a")])

    def test_mermaid_renders_edges(self):
        mer = self.g.to_mermaid()
        self.assertIn("flowchart LR", mer)
        self.assertIn("-->", mer)


class GraphUnitTests(unittest.TestCase):
    def test_orphans(self):
        g = CodeGraph()
        g.add(Module("root", "root.py", imports_internal={"leaf"}))
        g.add(Module("leaf", "leaf.py"))
        self.assertEqual(g.orphans(), ["root"])  # leaf is imported, root is not


class SelfScanTests(unittest.TestCase):
    """The cartographer maps its own labs/ home."""

    def setUp(self):
        target = "labs" if os.path.isdir("labs") else \
            os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.g = scan(target)

    def test_finds_many_modules(self):
        self.assertGreater(len(self.g.modules), 20)

    def test_kernel_is_among_most_central(self):
        top_names = [n for n, _ in self.g.central(3)]
        self.assertIn("labs._kernel", top_names)

    def test_relative_kernel_imports_resolved(self):
        # tiny_town.sim does `from .._kernel import ...` and `from ..agent_memory ...`
        deps = self.g.out_edges("labs.tiny_town.sim")
        self.assertIn("labs._kernel", deps)
        self.assertIn("labs.agent_memory", deps)


if __name__ == "__main__":
    unittest.main()
