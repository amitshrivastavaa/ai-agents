import unittest

from ventures.maxout.analytics import (agent_performance, by_kind, latest_week,
                                       per_repo, streak, trend, utilization,
                                       value_summary, weeks)
from ventures.maxout.model import CREDIT_USD, Task
from ventures.maxout.sample_data import sample_dataset


def T(week="2026-W20", repo="api", kind="bug_fix", status="merged", credits=100.0, **kw):
    return Task(week=week, repo=repo, kind=kind, status=status, credits=credits, **kw)


class TestUtilization(unittest.TestCase):
    def test_used_idle_and_usd(self):
        tasks = [T(credits=300), T(credits=200, status="failed")]
        u = utilization(tasks, {"2026-W20": 1000}, "2026-W20")
        self.assertEqual(u["used"], 500.0)
        self.assertEqual(u["idle"], 500.0)
        self.assertAlmostEqual(u["pct"], 0.5)
        self.assertAlmostEqual(u["usd_equiv"], round(500 * CREDIT_USD, 2))

    def test_wasted_counts_failed_and_rejected(self):
        tasks = [T(credits=100, status="merged"),
                 T(credits=50, status="rejected"),
                 T(credits=40, status="failed")]
        u = utilization(tasks, {"2026-W20": 1000}, "2026-W20")
        self.assertEqual(u["wasted_credits"], 90.0)   # rejected + failed, not merged


class TestValue(unittest.TestCase):
    def test_acceptance_and_value_only_on_merged(self):
        tasks = [
            T(status="merged", kind="bug_fix", bugs_fixed=1, minutes_saved=60),
            T(status="open", kind="tests", coverage_delta=2.0, minutes_saved=30),
            T(status="rejected", kind="docs"),
            T(status="failed", kind="perf", credits=80),
        ]
        v = value_summary(tasks, "2026-W20")
        self.assertEqual(v["prs_opened"], 3)          # merged + open + rejected (not failed)
        self.assertEqual(v["prs_merged"], 1)
        self.assertEqual(v["failed"], 1)
        self.assertAlmostEqual(v["acceptance_rate"], 1 / 3, places=4)
        self.assertEqual(v["bugs_fixed"], 1)
        self.assertEqual(v["tests_coverage_delta"], 0.0)  # the tests task was 'open', not merged
        self.assertAlmostEqual(v["hours_saved"], 1.0)

    def test_failed_burns_credits_no_value(self):
        v = value_summary([T(status="failed", credits=120)], "2026-W20")
        self.assertEqual(v["prs_opened"], 0)
        self.assertEqual(v["hours_saved"], 0.0)


class TestStreak(unittest.TestCase):
    def test_streak_counts_recent_weeks_over_target(self):
        tasks = [T(week="2026-W20", credits=900), T(week="2026-W21", credits=500),
                 T(week="2026-W22", credits=850)]
        av = {"2026-W20": 1000, "2026-W21": 1000, "2026-W22": 1000}
        self.assertEqual(streak(tasks, av, 0.8), 1)   # W22 ok, W21 (50%) breaks it


class TestSample(unittest.TestCase):
    def setUp(self):
        self.tasks, self.available = sample_dataset()

    def test_six_weeks(self):
        self.assertEqual(len(weeks(self.tasks)), 6)

    def test_utilization_climbs(self):
        tr = trend(self.tasks, self.available)
        self.assertLess(tr[0]["pct"], tr[-1]["pct"])      # under-use -> maxed-out story
        self.assertGreater(tr[-1]["pct"], 0.85)

    def test_latest_week_ships_value(self):
        v = value_summary(self.tasks, latest_week(self.tasks))
        self.assertGreater(v["prs_merged"], 0)
        self.assertGreater(v["hours_saved"], 0)

    def test_agent_perf_rates_bounded(self):
        ap = agent_performance(self.tasks)
        self.assertTrue(ap)
        self.assertTrue(all(0.0 <= d["acceptance_rate"] <= 1.0 for d in ap.values()))

    def test_by_kind_and_per_repo_nonempty(self):
        self.assertTrue(by_kind(self.tasks, latest_week(self.tasks)))
        self.assertEqual(set(per_repo(self.tasks)), {"api", "web", "infra"})


if __name__ == "__main__":
    unittest.main()
