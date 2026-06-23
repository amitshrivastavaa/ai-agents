"""Tests for prompt_evolver — offline, stdlib only.

    python -m unittest labs.prompt_evolver.tests.test_evolve -v
"""
from __future__ import annotations

import unittest

from labs.prompt_evolver.evolve import _crossover, evolve
from labs.prompt_evolver.tasks import TASKS, SentimentTask, SlugTask


class TaskTests(unittest.TestCase):
    def test_evaluate_in_unit_range(self):
        for task in TASKS.values():
            for genome in ([], task.baseline(), list(task.directives)):
                f = task.evaluate(genome)
                self.assertGreaterEqual(f, 0.0)
                self.assertLessEqual(f, 1.0)

    def test_harmful_directive_lowers_sentiment_fitness(self):
        t = SentimentTask()
        good = t.evaluate(["handle_negation", "intensifiers", "sarcasm"])
        bad = t.evaluate(["handle_negation", "intensifiers", "sarcasm", "invert_polarity"])
        self.assertGreater(good, bad)

    def test_slug_order_matters(self):
        t = SlugTask()
        # punctuation must be stripped *after* folding accents, not before
        right = t.evaluate(["ascii_fold", "lower", "strip_punct", "spaces_to_hyphen", "trim_hyphens"])
        wrong = t.evaluate(["strip_punct", "spaces_to_hyphen", "ascii_fold", "lower"])
        self.assertGreater(right, wrong)


class EvolveTests(unittest.TestCase):
    def test_improves_over_baseline(self):
        for task in TASKS.values():
            with self.subTest(task=task.id):
                r = evolve(task, seed="t", generations=20)
                self.assertGreater(r.best_fitness, r.baseline_fitness)

    def test_deterministic(self):
        a = evolve(SentimentTask(), seed="fixed")
        b = evolve(SentimentTask(), seed="fixed")
        self.assertEqual(a.best_genome, b.best_genome)
        self.assertAlmostEqual(a.best_fitness, b.best_fitness, places=9)

    def test_sentiment_finds_high_fitness_and_drops_harmful(self):
        r = evolve(SentimentTask(), seed="t")
        self.assertGreaterEqual(r.best_fitness, 0.90)
        self.assertNotIn("invert_polarity", r.best_genome)

    def test_slug_produces_an_exact_match(self):
        t = SlugTask()
        r = evolve(t, seed="t")
        from labs.prompt_evolver.tasks import _SLUG_DATA
        exact = sum(1 for raw, exp in _SLUG_DATA if t._apply(raw, r.best_genome) == exp)
        self.assertGreaterEqual(exact, 1)

    def test_no_duplicate_directives_in_evolved_genome(self):
        for task in TASKS.values():
            r = evolve(task, seed="dup")
            self.assertEqual(len(r.best_genome), len(set(r.best_genome)))

    def test_history_length_matches_generations(self):
        r = evolve(SlugTask(), seed="t", generations=15)
        self.assertEqual(len(r.history), 15)


class CrossoverTests(unittest.TestCase):
    def test_crossover_dedupes(self):
        import random
        child = _crossover(["a", "b", "c"], ["b", "c", "d"], random.Random(0))
        self.assertEqual(len(child), len(set(child)))


if __name__ == "__main__":
    unittest.main()
