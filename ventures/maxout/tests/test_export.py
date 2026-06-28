import unittest

from ventures.maxout.export import build_data
from ventures.maxout.sample_data import sample_dataset


class TestExport(unittest.TestCase):
    def setUp(self):
        self.data = build_data(*sample_dataset())

    def test_top_level_shape(self):
        for key in ("weeks", "available", "byWeek", "agentPerformance",
                    "perRepo", "trend", "kindLabels"):
            self.assertIn(key, self.data)

    def test_every_week_has_sections(self):
        for w in self.data["weeks"]:
            wk = self.data["byWeek"][w]
            self.assertIn("utilization", wk)
            self.assertIn("value", wk)
            self.assertIn("byKind", wk)

    def test_json_serializable(self):
        import json
        json.dumps(self.data)   # must not raise

    def test_trend_matches_weeks(self):
        self.assertEqual([t["week"] for t in self.data["trend"]], self.data["weeks"])


if __name__ == "__main__":
    unittest.main()
