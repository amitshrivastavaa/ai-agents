"""Tests for evo_arena — offline, stdlib only.

    python -m unittest labs.evo_arena.tests.test_arena -v
"""
from __future__ import annotations

import unittest

from labs._kernel import rng
from labs.evo_arena.arena import coevolve_memory1, replicator, tournament
from labs.evo_arena.game import play_match
from labs.evo_arena.strategies import Memory1, get_strategy


class GameTests(unittest.TestCase):
    def test_mutual_cooperation_pays_reward(self):
        allc = get_strategy("AllC")
        sa, sb, ca, cb = play_match(allc, allc, 10, rng("x"))
        self.assertEqual(sa, 30)   # 3 per round
        self.assertEqual((ca, cb), (10, 10))

    def test_defector_exploits_cooperator(self):
        sa, sb, *_ = play_match(get_strategy("AllD"), get_strategy("AllC"), 10, rng("x"))
        self.assertEqual(sa, 50)   # temptation every round
        self.assertEqual(sb, 0)

    def test_mutual_defection_is_punished(self):
        alld = get_strategy("AllD")
        sa, sb, *_ = play_match(alld, alld, 10, rng("x"))
        self.assertEqual((sa, sb), (10, 10))  # 1 per round


class StrategyTests(unittest.TestCase):
    def test_tit_for_tat_retaliates_then_forgives(self):
        tft = get_strategy("TitForTat")
        # opponent defected last move -> TFT defects; cooperated -> TFT cooperates
        self.assertEqual(tft(["C"], ["D"], rng("x")), "D")
        self.assertEqual(tft(["D"], ["C"], rng("x")), "C")
        self.assertEqual(tft([], [], rng("x")), "C")  # nice: cooperates first

    def test_grim_never_forgives(self):
        grim = get_strategy("Grim")
        self.assertEqual(grim(["C", "C"], ["C", "D"], rng("x")), "D")

    def test_memory1_tft_genome_behaves_like_tft(self):
        tft = Memory1(1, 1, 0, 1, 0)
        self.assertEqual(tft(["C"], ["D"], rng("x")), "D")
        self.assertEqual(tft(["D"], ["C"], rng("x")), "C")

    def test_memory1_nearest_named(self):
        self.assertTrue(Memory1(1, 1, 0, 1, 0).nearest_named().startswith("TitForTat"))
        self.assertTrue(Memory1(0, 0, 0, 0, 0).nearest_named().startswith("AllD"))


class TournamentTests(unittest.TestCase):
    def test_reciprocators_beat_always_defect(self):
        rows = {r["name"]: r for r in tournament(rounds=100)}
        self.assertEqual(rows["AllC"]["coop_rate"], 1.0)
        self.assertEqual(rows["AllD"]["coop_rate"], 0.0)
        self.assertGreater(rows["TitForTat"]["total"], rows["AllD"]["total"])
        # the top scorer is a cooperative reciprocator, not the pure defector
        top = tournament(rounds=100)[0]["name"]
        self.assertNotEqual(top, "AllD")


class EvolutionTests(unittest.TestCase):
    def test_replicator_drives_defection_extinct(self):
        hist = replicator(generations=60, rounds=80)
        self.assertLess(hist[-1]["AllD"], 0.02)
        self.assertGreater(hist[-1]["TitForTat"], hist[0]["TitForTat"])

    def test_replicator_is_deterministic(self):
        self.assertEqual(replicator(generations=20), replicator(generations=20))

    def test_coevolution_paths_diverge_by_seed(self):
        emerge = coevolve_memory1(generations=24, rounds=80, seed="s")
        collapse = coevolve_memory1(generations=24, rounds=80, seed="tragedy")
        self.assertGreater(emerge[-1]["avg_coop"], collapse[-1]["avg_coop"])

    def test_coevolution_is_deterministic(self):
        a = coevolve_memory1(generations=10, seed="z")
        b = coevolve_memory1(generations=10, seed="z")
        self.assertEqual([r["best_genome"] for r in a], [r["best_genome"] for r in b])


if __name__ == "__main__":
    unittest.main()
