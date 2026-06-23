"""Tests for agent_os — offline, stdlib only.

    python -m unittest labs.agent_os.tests.test_kernel -v
"""
from __future__ import annotations

import unittest

from labs.agent_os.cli import run_workload
from labs.agent_os.kernel import Kernel, Outcome, Task, TaskState


class SchedulerTests(unittest.TestCase):
    def test_respects_dependencies(self):
        order = []
        k = Kernel(max_workers=4)
        for kind in ("a", "b", "c"):
            k.register(kind, (lambda kk: (lambda ctx: order.append(kk) or Outcome()))(kind))
        k.add(Task("a", "a"))
        k.add(Task("b", "b", deps=frozenset({"a"})))
        k.add(Task("c", "c", deps=frozenset({"b"})))
        k.run()
        self.assertEqual(order, ["a", "b", "c"])

    def test_independent_tasks_run_same_step(self):
        k = Kernel(max_workers=3)
        k.register("x", lambda ctx: Outcome())
        for i in range(3):
            k.add(Task(f"t{i}", "x"))
        report = k.run()
        self.assertEqual(len(report.schedule), 1)       # all three in one step
        self.assertEqual(len(report.schedule[0]), 3)

    def test_priority_ordering(self):
        seen = []
        k = Kernel(max_workers=1)
        k.register("x", lambda ctx: seen.append(ctx.task.id) or Outcome())
        k.add(Task("low", "x", priority=1))
        k.add(Task("high", "x", priority=9))
        k.run()
        self.assertEqual(seen[0], "high")

    def test_failure_cancels_downstream(self):
        k = Kernel()
        k.register("boom", lambda ctx: Outcome(ok=False, detail="nope"))
        k.register("noop", lambda ctx: Outcome())
        k.add(Task("boom", "boom"))
        k.add(Task("after", "noop", deps=frozenset({"boom"})))
        report = k.run()
        self.assertEqual(report.tasks["boom"].state, TaskState.FAILED)
        self.assertEqual(report.tasks["after"].state, TaskState.CANCELLED)

    def test_retry_then_succeed(self):
        k = Kernel()
        k.register("flaky", lambda ctx: Outcome(ok=False, retry=True)
                   if ctx.task.attempts < 2 else Outcome(ok=True))
        k.add(Task("flaky", "flaky", max_attempts=2))
        report = k.run()
        self.assertEqual(report.tasks["flaky"].state, TaskState.DONE)
        self.assertEqual(report.tasks["flaky"].attempts, 2)

    def test_dependency_cycle_is_cancelled_not_hung(self):
        k = Kernel(max_steps=50)
        k.register("x", lambda ctx: Outcome())
        k.add(Task("a", "x", deps=frozenset({"b"})))
        k.add(Task("b", "x", deps=frozenset({"a"})))
        report = k.run()
        self.assertFalse(report.timed_out)
        self.assertEqual(report.tasks["a"].state, TaskState.CANCELLED)
        self.assertEqual(report.tasks["b"].state, TaskState.CANCELLED)

    def test_spawned_tasks_execute(self):
        k = Kernel()
        k.register("parent", lambda ctx: (ctx.spawn(Task("child", "child")), Outcome())[1])
        k.register("child", lambda ctx: ctx.write("child_ran", True) or Outcome())
        k.add(Task("parent", "parent"))
        report = k.run()
        self.assertTrue(report.blackboard.get("child_ran"))


class WorkloadTests(unittest.TestCase):
    def test_report_produces_artifact(self):
        _, report = run_workload("report", goal="Are AI agents overhyped?")
        self.assertTrue(report.succeeded)
        self.assertIn("report", report.blackboard)
        self.assertIn("Risks", report.blackboard["report"])
        # plan + 4 research + synthesize + write = 7 tasks
        self.assertEqual(len(report.tasks), 7)

    def test_report_fans_out_research_in_parallel(self):
        _, report = run_workload("report", workers=4)
        # one of the steps should dispatch multiple research tasks at once
        self.assertTrue(any(len(step) > 1 for step in report.schedule))

    def test_ci_retries_and_succeeds(self):
        _, report = run_workload("ci")
        self.assertTrue(report.succeeded)
        self.assertEqual(report.tasks["test"].attempts, 2)
        self.assertEqual(report.blackboard.get("deploy"), "released to prod")

    def test_ci_broken_cancels_downstream(self):
        _, report = run_workload("ci_broken")
        self.assertFalse(report.succeeded)
        self.assertEqual(report.tasks["build"].state, TaskState.FAILED)
        self.assertEqual(report.tasks["test"].state, TaskState.CANCELLED)
        self.assertEqual(report.tasks["deploy"].state, TaskState.CANCELLED)

    def test_deterministic(self):
        a = run_workload("report", seed="z")[1].to_dict()
        b = run_workload("report", seed="z")[1].to_dict()
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
