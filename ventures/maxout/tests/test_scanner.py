import os
import tempfile
import unittest

from ventures.maxout.runner import ClaudeCodeRunner
from ventures.maxout.scanner import scan_repo

SAMPLE = '''x = 1


def foo(a):
    try:
        return a
    except:
        pass


# TODO: handle the empty case
'''


class TestScanner(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "mod.py"), "w", encoding="utf-8") as f:
            f.write(SAMPLE)

    def test_finds_each_signal(self):
        kinds = {i.kind for i in scan_repo(self.d)}
        self.assertIn("docs", kinds)    # module + public foo lack docstrings
        self.assertIn("todo", kinds)    # the TODO marker
        self.assertIn("bug", kinds)     # bare except
        self.assertIn("tests", kinds)   # no test file for mod.py

    def test_clean_module_is_quiet(self):
        clean = os.path.join(self.d, "clean.py")
        with open(clean, "w", encoding="utf-8") as f:
            f.write('"""A clean module."""\n')
        # the only thing flagged for a documented, empty module is "no test file"
        kinds = [i.kind for i in scan_repo(self.d) if i.path.endswith("clean.py")]
        self.assertEqual(kinds, ["tests"])

    def test_dry_run_records_open_tasks(self):
        items = scan_repo(self.d)
        runner = ClaudeCodeRunner(self.d, week="2026-W26")
        tasks = runner.run_backlog(items, dry_run=True, budget_credits=10000)
        self.assertTrue(tasks)
        self.assertTrue(all(t.status == "open" for t in tasks))
        self.assertEqual(tasks[0].week, "2026-W26")

    def test_budget_stops_the_backlog(self):
        items = scan_repo(self.d)
        runner = ClaudeCodeRunner(self.d, week="2026-W26")
        tasks = runner.run_backlog(items, dry_run=True, budget_credits=1)  # nothing fits
        self.assertEqual(tasks, [])


if __name__ == "__main__":
    unittest.main()
