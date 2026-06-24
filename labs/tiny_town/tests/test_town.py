"""Tests for tiny_town — offline, stdlib only.

    python -m unittest labs.tiny_town.tests.test_town -v
"""
from __future__ import annotations

import unittest

from labs.tiny_town.sim import base_affinity, choose_location, rel_label, run
from labs.tiny_town.world import PHASES, fresh_agents


class RoutineTests(unittest.TestCase):
    def test_everyone_goes_home_at_night(self):
        for ag in fresh_agents():
            self.assertEqual(choose_location(ag, "night"), ag.home)
            self.assertEqual(choose_location(ag, "forenoon"), ag.work)

    def test_locations_are_valid(self):
        from labs.tiny_town.world import LOCATIONS
        for ag in fresh_agents():
            for phase in PHASES:
                self.assertIn(choose_location(ag, phase), LOCATIONS)


class AffinityTests(unittest.TestCase):
    def test_shared_traits_raise_affinity(self):
        agents = {a.name: a for a in fresh_agents()}
        # Alice & Cleo share 'outgoing'; Alice & Bram share nothing
        self.assertGreater(base_affinity(agents["Alice"], agents["Cleo"]),
                           base_affinity(agents["Alice"], agents["Bram"]))

    def test_affinity_symmetric(self):
        agents = {a.name: a for a in fresh_agents()}
        self.assertAlmostEqual(base_affinity(agents["Alice"], agents["Wren"]),
                               base_affinity(agents["Wren"], agents["Alice"]), places=9)


class SimulationTests(unittest.TestCase):
    def test_runs_and_produces_events(self):
        sim = run(days=2, seed="t")
        self.assertGreater(len(sim.chronicle), 0)
        self.assertEqual(len(sim.agents), 5)

    def test_deterministic(self):
        a = run(days=3, seed="fixed")
        b = run(days=3, seed="fixed")
        self.assertEqual(a.to_dict(), b.to_dict())

    def test_relationships_form(self):
        sim = run(days=3, seed="t")
        # somebody should have a real relationship recorded
        total_links = sum(len(a.relationships) for a in sim.agents)
        self.assertGreater(total_links, 0)
        bond = sim.strongest_bond()
        self.assertIsNotNone(bond)

    def test_residents_accumulate_memories(self):
        sim = run(days=2, seed="t")
        for a in sim.agents:
            self.assertGreater(a.memory.stats()["total"], 0)

    def test_more_days_strengthen_the_top_bond(self):
        short = run(days=1, seed="t").strongest_bond()[2]
        long = run(days=4, seed="t").strongest_bond()[2]
        self.assertGreaterEqual(long, short)

    def test_rel_label_bands(self):
        self.assertEqual(rel_label(0.9), "close friends")
        self.assertEqual(rel_label(0.3), "friends")
        self.assertEqual(rel_label(0.0), "acquaintances")
        self.assertEqual(rel_label(-0.5), "on tense terms")

    def test_json_serializable(self):
        import json
        json.dumps(run(days=2, seed="t").to_dict())


if __name__ == "__main__":
    unittest.main()
